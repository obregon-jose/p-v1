import tkinter as tk
import threading
import updater

APP_VERSION = "2.0.0"

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


def main():
    root = tk.Tk()
    root.title("Mi Aplicación v2")
    root.geometry("340x480")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")

    # ── Encabezado ──────────────────────────────────────
    header = tk.Frame(root, bg="#2a2a3e", pady=8)
    header.pack(fill="x")
    tk.Label(header, text="🖥️ Mi Aplicación",
             font=("Segoe UI", 13, "bold"),
             bg="#2a2a3e", fg="white").pack()
    tk.Label(header, text=f"Versión: {APP_VERSION}",
             font=("Segoe UI", 9), bg="#2a2a3e", fg="#aaa").pack()

    # ── Display ─────────────────────────────────────────
    display_var = tk.StringVar(value="0")
    tk.Entry(root, textvariable=display_var,
             font=("Segoe UI", 22, "bold"),
             justify="right", bd=0,
             bg="#12121f", fg="white",
             insertbackground="white",
             state="readonly", readonlybackground="#12121f"
             ).pack(fill="x", padx=10, pady=10, ipady=12)

    # ── Botones ─────────────────────────────────────────
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

    # ── Status ───────────────────────────────────────────
    status = tk.Label(root, text="Buscando actualizaciones...",
                      font=("Segoe UI", 8), fg="#666", bg="#1e1e2e")
    status.pack(pady=4)

    def check():
        updater.check(APP_VERSION, root, status)

    threading.Thread(target=check, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()