import pyperclip
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
import threading
import datetime
import customtkinter as ctk

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.clipboard_history = []
        self.create_ui()
        self.update_clipboard_history()
        self.root.after(1000, self.check_clipboard)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def create_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.geometry("600x700")

        self.frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.title_label = ctk.CTkLabel(self.frame, text="Clipboard Manager", font=("Helvetica", 24))
        self.title_label.pack(pady=10)

        self.search_entry = ctk.CTkEntry(self.frame, placeholder_text="Search clipboard...", font=("Helvetica", 16))
        self.search_entry.pack(fill=tk.X, padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.filter_history)

        self.sort_options = ["Sort by: Time", "Sort by: A-Z", "Sort by: Z-A"]
        self.sort_var = tk.StringVar(value=self.sort_options[0])
        self.sort_menu = ctk.CTkOptionMenu(self.frame, variable=self.sort_var, values=self.sort_options, command=self.sort_history)
        self.sort_menu.pack(pady=10)

        self.listbox_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = ctk.CTkScrollbar(self.listbox_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.listbox_frame, yscrollcommand=self.scrollbar.set, font=("Helvetica", 16), selectmode=tk.SINGLE, activestyle='none')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scrollbar.configure(command=self.listbox.yview)

        self.button_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.button_frame.pack(pady=10)

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_history, font=("Helvetica", 16))
        self.clear_button.pack(side=tk.LEFT, padx=10)

        self.copy_button = ctk.CTkButton(self.button_frame, text="Copy Selected", command=self.copy_selected, font=("Helvetica", 16))
        self.copy_button.pack(side=tk.LEFT, padx=10)

    def update_clipboard_history(self):
        current_clipboard = pyperclip.paste()
        if len(self.clipboard_history) == 0 or self.clipboard_history[-1]['text'] != current_clipboard:
            item = {
                'text': current_clipboard,
                'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.clipboard_history.append(item)
            self.listbox.insert(tk.END, f"{item['text']}\n{item['time']}")
            self.listbox.itemconfig(tk.END, {'bg': '#2a2d2e', 'fg': '#ffffff'})

    def check_clipboard(self):
        self.update_clipboard_history()
        self.root.after(1000, self.check_clipboard)

    def clear_history(self):
        self.clipboard_history.clear()
        self.listbox.delete(0, tk.END)

    def copy_selected(self):
        try:
            selected = self.listbox.get(self.listbox.curselection())
            selected_text = selected.split('\n')[0]
            pyperclip.copy(selected_text)
            messagebox.showinfo("Clipboard Manager", "Copied to clipboard!")
        except tk.TclError:
            messagebox.showwarning("Clipboard Manager", "No item selected.")

    def sort_history(self, _=None):
        sort_by = self.sort_var.get()
        if sort_by == "Sort by: Time":
            self.clipboard_history.sort(key=lambda x: x['time'], reverse=True)
        elif sort_by == "Sort by: A-Z":
            self.clipboard_history.sort(key=lambda x: x['text'].lower())
        elif sort_by == "Sort by: Z-A":
            self.clipboard_history.sort(key=lambda x: x['text'].lower(), reverse=True)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for index, item in enumerate(self.clipboard_history):
            frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
            frame.pack(fill=tk.X, pady=5, padx=5)
            frame.bind("<Button-1>", lambda e, idx=index: self.on_item_click(idx))

            label_text = ctk.CTkLabel(frame, text=item['text'], font=("Helvetica", 16), anchor="w")
            label_text.pack(fill=tk.X, padx=10, pady=5)

            label_time = ctk.CTkLabel(frame, text=item['time'], font=("Helvetica", 12), anchor="e")
            label_time.pack(fill=tk.X, padx=10, pady=5)

    def filter_history(self, event):
        query = self.search_entry.get().lower()
        filtered = [item for item in self.clipboard_history if query in item['text'].lower()]

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for index, item in enumerate(filtered):
            frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
            frame.pack(fill=tk.X, pady=5, padx=5)
            frame.bind("<Button-1>", lambda e, idx=index: self.on_item_click(idx))

            label_text = ctk.CTkLabel(frame, text=item['text'], font=("Helvetica", 16), anchor="w")
            label_text.pack(fill=tk.X, padx=10, pady=5)

            label_time = ctk.CTkLabel(frame, text=item['time'], font=("Helvetica", 12), anchor="e")
            label_time.pack(fill=tk.X, padx=10, pady=5)

    def hide_window(self):
        self.root.withdraw()
        self.create_tray_icon()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill='blue')
        self.icon = pystray.Icon("Clipboard Manager", image, "Clipboard Manager", self.create_menu())
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon, item):
        self.root.deiconify()
        self.icon.stop()

    def quit_app(self, icon, item):
        self.icon.stop()
        self.root.destroy()

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Quit", self.quit_app)
        )

if __name__ == "__main__":
    root = ctk.CTk()
    clipboard_manager = ClipboardManager(root)
    root.mainloop()

