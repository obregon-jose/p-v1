import tkinter as tk
import threading
import updater

APP_VERSION = "1.0.0"

def main():
    root = tk.Tk()
    root.title("Mi Aplicación")
    root.geometry("340x200")
    root.resizable(False, False)
    root.configure(bg="#f0f0f0")

    tk.Label(root, text="🖥️ Mi Aplicación",
             font=("Segoe UI", 18, "bold"),
             bg="#f0f0f0", fg="#222").pack(pady=30)

    tk.Label(root, text=f"Versión: {APP_VERSION}",
             font=("Segoe UI", 12),
             bg="#f0f0f0", fg="#555").pack()

    status = tk.Label(root, text="Buscando actualizaciones...",
                      font=("Segoe UI", 9), bg="#f0f0f0", fg="#aaa")
    status.pack(pady=15)

    def check():
        updater.check(APP_VERSION, root, status)

    threading.Thread(target=check, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()