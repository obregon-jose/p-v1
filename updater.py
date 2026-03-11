import urllib.request
import json
import os
import sys
import subprocess
import threading
import tkinter as tk

# ══════════════════════════════════════════════════════
#  ⚙️  CAMBIA ESTOS DOS VALORES POR LOS TUYOS
GITHUB_USER = "obregon-jose"
GITHUB_REPO = "https://github.com/obregon-jose/preuba-v1"
# ══════════════════════════════════════════════════════

VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
EXE_URL     = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/MiApp.exe"


def check(current_version, root, status_label):
    """Llama a GitHub y compara versiones. Se ejecuta en hilo secundario."""
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=6) as r:
            data = json.loads(r.read().decode())
        latest = data.get("version", current_version)

        if latest != current_version:
            # Volver al hilo principal para mostrar UI
            root.after(0, lambda: _ask_update(latest, root, status_label))
        else:
            root.after(0, lambda: status_label.config(text="✅ La app está actualizada"))
    except Exception:
        root.after(0, lambda: status_label.config(text=""))


def _ask_update(new_version, root, status_label):
    """Ventana de diálogo: ¿Deseas actualizar?"""
    win = tk.Toplevel(root)
    win.title("Nueva versión disponible")
    win.geometry("360x160")
    win.resizable(False, False)
    win.grab_set()
    win.configure(bg="#ffffff")

    tk.Label(win, text="🚀 ¡Actualización disponible!",
             font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#222").pack(pady=(18, 4))

    tk.Label(win, text=f"Nueva versión: {new_version}\nSe instalará automáticamente sin pasos extra.",
             font=("Segoe UI", 10), bg="#ffffff", fg="#555", justify="center").pack()

    btn_frame = tk.Frame(win, bg="#ffffff")
    btn_frame.pack(pady=14)

    tk.Button(btn_frame, text="✅  Actualizar ahora",
              font=("Segoe UI", 10, "bold"),
              bg="#4CAF50", fg="white", relief="flat",
              padx=16, pady=6,
              command=lambda: [win.destroy(), _do_update(root, status_label)]
              ).pack(side="left", padx=8)

    tk.Button(btn_frame, text="Ahora no",
              font=("Segoe UI", 10),
              bg="#e0e0e0", fg="#333", relief="flat",
              padx=12, pady=6,
              command=win.destroy
              ).pack(side="left", padx=8)


def _do_update(root, status_label):
    """Descarga el nuevo .exe y reemplaza el actual, luego reinicia."""
    status_label.config(text="⬇️  Descargando actualización...")
    root.update()

    def download():
        try:
            exe_path = sys.executable          # ruta del .exe actual
            tmp_path  = exe_path + ".new"      # archivo temporal

            # Descarga el nuevo ejecutable
            urllib.request.urlretrieve(EXE_URL, tmp_path,
                reporthook=lambda b, bs, ts: _progress(root, status_label, b, bs, ts))

            # Script bat que: espera, reemplaza, reinicia
            bat = exe_path + "_update.bat"
            with open(bat, "w") as f:
                f.write(f"""@echo off
timeout /t 2 /nobreak >nul
move /y "{tmp_path}" "{exe_path}"
start "" "{exe_path}"
del "%~f0"
""")
            subprocess.Popen(["cmd", "/c", bat], shell=False,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            root.after(500, root.destroy)

        except Exception as e:
            root.after(0, lambda: status_label.config(text=f"⚠️ Error: {e}"))

    threading.Thread(target=download, daemon=True).start()


def _progress(root, label, blocks, block_size, total_size):
    if total_size > 0:
        pct = min(int(blocks * block_size * 100 / total_size), 100)
        root.after(0, lambda: label.config(text=f"⬇️  Descargando... {pct}%"))