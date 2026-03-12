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

# GitHub intenta rama 'main' y si falla intenta 'master'
VERSION_URL_MAIN   = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
VERSION_URL_MASTER = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/master/version.json"
EXE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/MiApp.exe"


# ─── Lógica de actualización ──────────────────────────────────────────────────

def get_latest_version():
    """Intenta obtener version.json desde main o master."""
    for url in [VERSION_URL_MAIN, VERSION_URL_MASTER]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MiApp-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
                return data.get("version", None)
        except Exception:
            continue
    return None  # no se pudo conectar


def check_for_updates(root, status_label):
    """Se ejecuta en hilo secundario."""
    latest = get_latest_version()

    if latest is None:
        # Sin internet o repo mal configurado
        root.after(0, lambda: status_label.config(
            text="⚠️ No se pudo verificar actualizaciones", fg="#e67e22"))
        return

    if latest != APP_VERSION:
        root.after(0, lambda: ask_update(latest, root, status_label))
    else:
        root.after(0, lambda: status_label.config(
            text="✅ La app está actualizada", fg="#27ae60"))


def ask_update(new_version, root, status_label):
    """Muestra ventana de diálogo al usuario."""
    win = tk.Toplevel(root)
    win.title("Nueva versión disponible")
    win.geometry("380x170")
    win.resizable(False, False)
    win.grab_set()
    win.configure(bg="#ffffff")
    # Centrar sobre la ventana principal
    win.transient(root)

    tk.Label(win, text="🚀 ¡Actualización disponible!",
             font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#222").pack(pady=(18, 6))

    tk.Label(win,
             text=f"Versión actual:  {APP_VERSION}\n"
                  f"Nueva versión:   {new_version}\n\n"
                  f"Se instalará automáticamente.",
             font=("Segoe UI", 10), bg="#ffffff", fg="#555",
             justify="center").pack()

    btn_frame = tk.Frame(win, bg="#ffffff")
    btn_frame.pack(pady=12)

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
              command=win.destroy
              ).pack(side="left", padx=10)


def do_update(root, status_label):
    """Descarga el nuevo .exe y lo reemplaza usando un .bat auxiliar."""
    status_label.config(text="⬇️  Iniciando descarga...", fg="#2980b9")

    def download():
        try:
            # Ruta del .exe en ejecución
            if getattr(sys, 'frozen', False):
                # Ejecutando como .exe compilado por PyInstaller
                exe_path = sys.executable
            else:
                # Ejecutando como script .py (para pruebas)
                exe_path = os.path.abspath(__file__)

            tmp_path = exe_path + ".new"

            # ── Descargar nuevo ejecutable ──────────────────────
            def progress(block_num, block_size, total_size):
                if total_size > 0:
                    pct = min(int(block_num * block_size * 100 / total_size), 100)
                    root.after(0, lambda p=pct: status_label.config(
                        text=f"⬇️  Descargando... {p}%", fg="#2980b9"))

            req = urllib.request.Request(
                EXE_URL, headers={"User-Agent": "MiApp-Updater/1.0"})
            # urlretrieve no acepta Request directamente, usamos urlopen + write
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk = 8192
                with open(tmp_path, "wb") as f:
                    while True:
                        buf = resp.read(chunk)
                        if not buf:
                            break
                        f.write(buf)
                        downloaded += len(buf)
                        if total:
                            pct = min(int(downloaded * 100 / total), 100)
                            root.after(0, lambda p=pct: status_label.config(
                                text=f"⬇️  Descargando... {p}%", fg="#2980b9"))

            root.after(0, lambda: status_label.config(
                text="⚙️  Instalando actualización...", fg="#8e44ad"))

            # ── Script .bat: espera, reemplaza, reinicia ─────────
            bat_path = exe_path + "_update.bat"
            with open(bat_path, "w") as f:
                f.write(
                    f"@echo off\n"
                    f"timeout /t 2 /nobreak >nul\n"
                    f"move /y \"{tmp_path}\" \"{exe_path}\"\n"
                    f"start \"\" \"{exe_path}\"\n"
                    f"del \"%~f0\"\n"
                )

            subprocess.Popen(
                f'cmd /c "{bat_path}"',
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            root.after(800, root.destroy)

        except Exception as e:
            root.after(0, lambda: status_label.config(
                text=f"⚠️ Error al actualizar: {e}", fg="#e74c3c"))

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

    # Lanza la verificación en hilo separado para no bloquear la UI
    threading.Thread(
        target=check_for_updates,
        args=(root, status),
        daemon=True
    ).start()

    root.mainloop()


if __name__ == "__main__":
    main()