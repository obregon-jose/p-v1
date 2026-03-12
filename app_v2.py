import tkinter as tk
import threading
import urllib.request
import json
import os
import sys
import subprocess

# ══════════════════════════════════════════════════════
#  ⚙️  CAMBIA ESTOS DOS VALORES POR LOS TUYOS
GITHUB_USER = "obregon-jose"
GITHUB_REPO = "p-v1"
# ══════════════════════════════════════════════════════

APP_VERSION = "2.0.0"

VERSION_URL_MAIN   = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
VERSION_URL_MASTER = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/master/version.json"
EXE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/MiApp.exe"


# ─── Lógica de actualización ─────────────────────────────────────────────────

def get_latest_version():
    for url in [VERSION_URL_MAIN, VERSION_URL_MASTER]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MiApp-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
                return data.get("version", None)
        except Exception:
            continue
    return None


def check_for_updates(root, status_label):
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
    win = tk.Toplevel(root)
    win.title("Nueva versión disponible")
    win.geometry("380x170")
    win.resizable(False, False)
    win.grab_set()
    win.transient(root)
    win.configure(bg="#ffffff")

    tk.Label(win, text="🚀 ¡Actualización disponible!",
             font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#222").pack(pady=(18, 6))
    tk.Label(win,
             text=f"Versión actual:  {APP_VERSION}\n"
                  f"Nueva versión:   {new_version}\n\n"
                  f"Se instalará automáticamente.",
             font=("Segoe UI", 10), bg="#ffffff", fg="#555", justify="center").pack()

    btn_frame = tk.Frame(win, bg="#ffffff")
    btn_frame.pack(pady=12)

    tk.Button(btn_frame, text="✅  Actualizar ahora",
              font=("Segoe UI", 10, "bold"),
              bg="#4CAF50", fg="white", relief="flat", padx=16, pady=8,
              command=lambda: [win.destroy(), do_update(root, status_label)]
              ).pack(side="left", padx=10)

    tk.Button(btn_frame, text="Ahora no",
              font=("Segoe UI", 10),
              bg="#e0e0e0", fg="#333", relief="flat", padx=12, pady=8,
              command=win.destroy).pack(side="left", padx=10)


def do_update(root, status_label):
    status_label.config(text="⬇️  Iniciando descarga...", fg="#2980b9")

    def download():
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            tmp_path = exe_path + ".new"

            req = urllib.request.Request(EXE_URL, headers={"User-Agent": "MiApp-Updater/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(tmp_path, "wb") as f:
                    while True:
                        buf = resp.read(8192)
                        if not buf:
                            break
                        f.write(buf)
                        downloaded += len(buf)
                        if total:
                            pct = min(int(downloaded * 100 / total), 100)
                            root.after(0, lambda p=pct: status_label.config(
                                text=f"⬇️  Descargando... {p}%", fg="#2980b9"))

            root.after(0, lambda: status_label.config(
                text="⚙️  Instalando...", fg="#8e44ad"))

            bat_path = exe_path + "_update.bat"
            with open(bat_path, "w") as f:
                f.write(
                    f"@echo off\n"
                    f"timeout /t 2 /nobreak >nul\n"
                    f"move /y \"{tmp_path}\" \"{exe_path}\"\n"
                    f"start \"\" \"{exe_path}\"\n"
                    f"del \"%~f0\"\n"
                )
            subprocess.Popen(f'cmd /c "{bat_path}"', shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            root.after(800, root.destroy)

        except Exception as e:
            root.after(0, lambda: status_label.config(
                text=f"⚠️ Error: {e}", fg="#e74c3c"))

    threading.Thread(target=download, daemon=True).start()


# ─── Calculadora ─────────────────────────────────────────────────────────────

expression = ""

def press(key, display_var):
    global expression
    if key == "C":
        expression = ""
    elif key == "=":
        try:
            expression = str(eval(expression))
        except Exception:
            expression = "Error"
    elif key == "⌫":
        expression = expression[:-1]
    else:
        expression += str(key)
    display_var.set(expression or "0")


# ─── Interfaz versión 2 ───────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title("Mi Aplicación v2")
    root.geometry("340x500")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")

    # Encabezado
    header = tk.Frame(root, bg="#2a2a3e", pady=8)
    header.pack(fill="x")
    tk.Label(header, text="🖥️ Mi Aplicación",
             font=("Segoe UI", 13, "bold"), bg="#2a2a3e", fg="white").pack()
    tk.Label(header, text=f"Versión: {APP_VERSION}",
             font=("Segoe UI", 9), bg="#2a2a3e", fg="#aaa").pack()

    # Display
    display_var = tk.StringVar(value="0")
    tk.Entry(root, textvariable=display_var,
             font=("Segoe UI", 22, "bold"), justify="right",
             bd=0, bg="#12121f", fg="white",
             insertbackground="white", state="readonly",
             readonlybackground="#12121f"
             ).pack(fill="x", padx=10, pady=10, ipady=12)

    # Botones
    BUTTONS = [
        ["C",  "⌫", "%",  "/"],
        ["7",  "8",  "9",  "*"],
        ["4",  "5",  "6",  "-"],
        ["1",  "2",  "3",  "+"],
        ["0",  ".",  "=",   ""],
    ]
    COLORS = {
        "=": "#4CAF50", "/": "#ff9800", "*": "#ff9800",
        "-": "#ff9800", "+": "#ff9800",
        "C": "#e53935", "⌫": "#546e7a", "%": "#546e7a",
    }

    btn_frame = tk.Frame(root, bg="#1e1e2e")
    btn_frame.pack(fill="both", expand=True, padx=10, pady=5)

    for row_keys in BUTTONS:
        row = tk.Frame(btn_frame, bg="#1e1e2e")
        row.pack(fill="x", pady=3)
        for key in row_keys:
            if key == "":
                tk.Label(row, bg="#1e1e2e", width=7).pack(side="left", padx=3)
                continue
            w = 14 if key == "0" else 7
            tk.Button(row, text=key,
                      font=("Segoe UI", 13, "bold"),
                      bg=COLORS.get(key, "#2a2a3e"),
                      fg="white", activebackground="#555",
                      relief="flat", width=w, height=2,
                      command=lambda k=key: press(k, display_var)
                      ).pack(side="left", padx=3)

    # Status
    status = tk.Label(root, text="🔍 Buscando actualizaciones...",
                      font=("Segoe UI", 8), fg="#666", bg="#1e1e2e")
    status.pack(pady=4)

    threading.Thread(
        target=check_for_updates,
        args=(root, status),
        daemon=True
    ).start()

    root.mainloop()


if __name__ == "__main__":
    main()