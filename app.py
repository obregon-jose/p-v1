import tkinter as tk
import threading
import urllib.request
import urllib.error
import json
import os
import sys
import subprocess

# ══════════════════════════════════════════════════════
#  ⚙️  CAMBIA ESTOS DOS VALORES POR LOS TUYOS
GITHUB_USER = "obregon-jose"
GITHUB_REPO = "p-v1"
# ══════════════════════════════════════════════════════

APP_VERSION = "1.0.0"

VERSION_URL_MAIN   = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
VERSION_URL_MASTER = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/master/version.json"

# URL directa al .exe dentro del Release (GitHub la sirve con redirecciones)
EXE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/MiApp.exe"


# ─── Función de descarga que sigue redirecciones manualmente ─────────────────

def download_file(url, dest_path, progress_callback=None):
    """
    Descarga un archivo siguiendo redirecciones HTTP/HTTPS manualmente.
    GitHub Releases redirige varias veces antes de llegar al archivo real.
    """
    MAX_REDIRECTS = 10
    current_url = url

    for _ in range(MAX_REDIRECTS):
        req = urllib.request.Request(
            current_url,
            headers={
                "User-Agent": "MiApp-Updater/1.0",
                "Accept": "*/*",
            }
        )
        try:
            resp = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            # 301/302/303/307/308 → seguir la redirección
            if e.code in (301, 302, 303, 307, 308):
                current_url = e.headers.get("Location", "")
                if not current_url:
                    raise RuntimeError("Redirección sin destino")
                continue
            raise

        # Llegamos al archivo real
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(16384)  # 16 KB por bloque
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total:
                    pct = min(int(downloaded * 100 / total), 100)
                    progress_callback(pct)

        return  # descarga exitosa

    raise RuntimeError(f"Demasiadas redirecciones al descargar:\n{url}")


# ─── Lógica de actualización ──────────────────────────────────────────────────

def get_latest_version():
    """Obtiene la versión más reciente desde GitHub (intenta main y master)."""
    for url in [VERSION_URL_MAIN, VERSION_URL_MASTER]:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "MiApp-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
                return data.get("version", None)
        except Exception:
            continue
    return None


def check_for_updates(root, status_label):
    """Se ejecuta en hilo secundario para no bloquear la interfaz."""
    latest = get_latest_version()

    if latest is None:
        root.after(0, lambda: status_label.config(
            text="⚠️ No se pudo verificar actualizaciones", fg="#e67e22"))
        return

    if latest != APP_VERSION:
        root.after(0, lambda: ask_update(latest, root, status_label))
    else:
        root.after(0, lambda: status_label.config(
            text="✅ La app está actualizada", fg="#27ae60"))


def ask_update(new_version, root, status_label):
    """Ventana de diálogo: ¿Deseas actualizar?"""
    win = tk.Toplevel(root)
    win.title("Nueva versión disponible")
    win.geometry("380x175")
    win.resizable(False, False)
    win.grab_set()
    win.transient(root)
    win.configure(bg="#ffffff")

    tk.Label(win, text="🚀 ¡Actualización disponible!",
             font=("Segoe UI", 13, "bold"),
             bg="#ffffff", fg="#222").pack(pady=(18, 6))

    tk.Label(win,
             text=f"Versión actual:  {APP_VERSION}\n"
                  f"Nueva versión:   {new_version}\n\n"
                  f"Se instalará automáticamente sin pasos extra.",
             font=("Segoe UI", 10), bg="#ffffff",
             fg="#555", justify="center").pack()

    btn_frame = tk.Frame(win, bg="#ffffff")
    btn_frame.pack(pady=14)

    tk.Button(btn_frame, text="✅  Actualizar ahora",
              font=("Segoe UI", 10, "bold"),
              bg="#4CAF50", fg="white", relief="flat",
              padx=16, pady=8,
              command=lambda: [win.destroy(), do_update(root, status_label)]
              ).pack(side="left", padx=10)

    tk.Button(btn_frame, text="Ahora no",
              font=("Segoe UI", 10),
              bg="#e0e0e0", fg="#333", relief="flat",
              padx=12, pady=8,
              command=win.destroy).pack(side="left", padx=10)


def do_update(root, status_label):
    """Descarga el nuevo .exe siguiendo redirecciones y lo reemplaza con .bat."""
    root.after(0, lambda: status_label.config(
        text="⬇️  Conectando con servidor...", fg="#2980b9"))

    def download():
        try:
            # Ruta del ejecutable actual
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable          # .exe compilado
            else:
                exe_path = os.path.abspath(__file__)  # .py en pruebas

            tmp_path = exe_path + ".new"
            bat_path = exe_path + "_update.bat"

            # ── Callback de progreso (se llama desde el hilo de descarga) ──
            def on_progress(pct):
                root.after(0, lambda p=pct: status_label.config(
                    text=f"⬇️  Descargando... {p}%", fg="#2980b9"))

            # ── Descargar siguiendo redirecciones ──────────────────────────
            download_file(EXE_URL, tmp_path, progress_callback=on_progress)

            root.after(0, lambda: status_label.config(
                text="⚙️  Instalando actualización...", fg="#8e44ad"))

            # ── Crear .bat que reemplaza el .exe y reinicia la app ─────────
            with open(bat_path, "w") as f:
                f.write(
                    "@echo off\n"
                    "timeout /t 2 /nobreak >nul\n"
                    f"move /y \"{tmp_path}\" \"{exe_path}\"\n"
                    f"start \"\" \"{exe_path}\"\n"
                    "del \"%~f0\"\n"
                )

            # Ejecutar el .bat y cerrar la app actual
            subprocess.Popen(
                f'cmd /c "{bat_path}"',
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            root.after(1000, root.destroy)

        except Exception as e:
            root.after(0, lambda: status_label.config(
                text=f"⚠️ Error: {e}", fg="#e74c3c"))

    threading.Thread(target=download, daemon=True).start()


# ─── Interfaz versión 1 ───────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title("Mi Aplicación")
    root.geometry("340x210")
    root.resizable(False, False)
    root.configure(bg="#f0f4f8")

    tk.Label(root, text="🖥️ Mi Aplicación",
             font=("Segoe UI", 18, "bold"),
             bg="#f0f4f8", fg="#222").pack(pady=28)

    tk.Label(root, text=f"Versión: {APP_VERSION}",
             font=("Segoe UI", 12),
             bg="#f0f4f8", fg="#555").pack()

    status = tk.Label(root, text="🔍 Buscando actualizaciones...",
                      font=("Segoe UI", 9), bg="#f0f4f8", fg="#aaa")
    status.pack(pady=18)

    threading.Thread(
        target=check_for_updates,
        args=(root, status),
        daemon=True
    ).start()

    root.mainloop()


if __name__ == "__main__":
    main()