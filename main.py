import tkinter as tk
from tkinter import messagebox

from src.config import ensure_api_key, load as load_config
from src.ui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.withdraw()  # Hide until setup is complete

    try:
        ensure_api_key(parent=root)
    except RuntimeError as e:
        messagebox.showerror("Startup Error", str(e))
        root.destroy()
        return

    cfg = load_config()
    root.deiconify()
    app = MainWindow(root, config=cfg)
    app.run()


if __name__ == "__main__":
    main()
