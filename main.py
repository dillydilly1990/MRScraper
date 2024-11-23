import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import quote, unquote
import shutil
import threading


class DownloaderApp:
    VERSION = "1.0"

    def __init__(self, root):
        self.root = root
        self.root.title(f"MRScraper v{self.VERSION}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.console_url = tk.StringVar()
        self.region = tk.StringVar(value="Europe")
        self.limit = tk.IntVar(value=10)
        self.status = tk.StringVar(value="Ready")
        self.do_limit = tk.BooleanVar(value=False)
        self.output_dir = tk.StringVar(value="C:/")

        # Flags
        self.curr_downloading = False
        self.cancel_flag = threading.Event()
        self.pause_flag = threading.Event()

        # Widgets
        self.limit_label = None
        self.limit_entry = None
        self.progress = None
        self.download_button = None
        self.cancel_button = None
        self.pause_button = None

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # System selection
        ttk.Label(frame, text="System:", width=20).grid(row=0, column=0, sticky=tk.W)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "systemlist.txt")
        with open(file_path, 'r') as f:
            consoles = [line.strip() for line in f.readlines()]

        dropdown = ttk.Combobox(frame, textvariable=self.console_url, values=consoles, width=50)
        dropdown.grid(row=0, column=1, sticky=tk.W)

        # Region selection
        ttk.Label(frame, text="Region:", width=40).grid(row=1, column=0, sticky=tk.E)
        regions = ["Europe", "USA", "Japan", "China", "Korea", "Australia", "Asia", "World only"]
        dropdown = ttk.Combobox(frame, textvariable=self.region, values=regions, width=10)
        dropdown.grid(row=1, column=1, sticky=tk.W)

        # File amount limits
        ttk.Checkbutton(frame, text="Limit files", variable=self.do_limit, command=self.toggle_limit_option).grid(row=2, column=0, sticky=tk.W)

        self.limit_label = ttk.Label(frame, text="Boundary:", width=20)
        self.limit_label.grid(row=3, column=0, sticky=tk.W)
        self.limit_entry = ttk.Spinbox(frame, from_=1, to=10000, textvariable=self.limit, width=10)
        self.limit_entry.grid(row=3, column=1, sticky=tk.W)
        self.toggle_limit_option()

        # Output directory
        ttk.Label(frame, text="Output dir:", width=20).grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.output_dir, width=50).grid(row=4, column=1, sticky=tk.W)
        ttk.Button(frame, text="Browse", command=self.select_output_dir).grid(row=4, column=2, sticky=tk.W)

        # Progress bar
        self.progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.W)

        # Download buttons
        self.download_button = ttk.Button(frame, text="Start Download", command=self.start_download)
        self.download_button.grid(row=6, column=0, sticky=tk.W)

        self.cancel_button = ttk.Button(frame, text="Cancel Download", command=self.cancel_download)
        self.cancel_button.grid(row=6, column=1, sticky=tk.W)
        self.cancel_button.config(state=tk.DISABLED)

        self.pause_button = ttk.Button(frame, text="Pause Download", command=self.pause_download)
        self.pause_button.grid(row=6, column=2, sticky=tk.W)
        self.pause_button.config(state=tk.DISABLED)

        # Status label
        ttk.Label(frame, textvariable=self.status, width=80).grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W)

    def toggle_limit_option(self):
        if self.do_limit.get():
            self.limit_label.config(state=tk.NORMAL)
            self.limit_entry.config(state=tk.NORMAL)
        else:
            self.limit_label.config(state=tk.DISABLED)
            self.limit_entry.config(state=tk.DISABLED)

    def select_output_dir(self):
        self.output_dir.set(tk.filedialog.askdirectory())

    def start_download(self):
        if not self.console_url.get():
            messagebox.showwarning("Warning", "Please select a console.")
            return
        elif not self.output_dir.get():
            messagebox.showwarning("Warning", "Please select an output directory.")
            return
        elif os.path.exists(os.path.join(self.output_dir.get(), "output")):
            result = messagebox.askyesno("Warning", "Proceeding will overwrite existing files! Are you sure?")
            if not result:
                return

        self.curr_downloading = True
        self.status.set("Downloading...")
        self.root.update_idletasks()
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_flag.clear()
        self.pause_flag.set()  # Ensure the pause flag is set to allow running
        download_thread = threading.Thread(target=self.download_files)
        download_thread.start()

    def cancel_download(self):
        self.cancel_flag.set()

    def pause_download(self):
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            self.pause_button.config(text="Resume Download")
        else:
            self.pause_flag.set()
            self.pause_button.config(text="Pause Download")

    def download_files(self):
        base_url = f"https://myrient.erista.me/files/No-Intro/{quote(self.console_url.get())}"
        limit = self.limit.get()

        min_free_space = 100 * 1024 * 1024

        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        full_path = os.path.join(self.output_dir.get(), "output")
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
        os.makedirs(full_path)

        links = soup.select("tbody > tr > td.link > a")

        if self.do_limit.get():
            filtered_links = [link for link in links[1:limit] if self.is_valid_file(link['href'])]
        else:
            filtered_links = [link for link in links if self.is_valid_file(link['href'])]

        amount = len(filtered_links)
        self.progress["maximum"] = amount

        curr_file = 0
        for link in filtered_links:
            if self.cancel_flag.is_set():
                self.cancel_flag.clear()
                self.status.set("Download cancelled!")
                self.cancel_button.config(state=tk.DISABLED)
                self.download_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED)
                return

            while not self.pause_flag.is_set():
                self.status.set("Paused...")
                self.root.update_idletasks()
                if self.cancel_flag.is_set():
                    self.cancel_flag.clear()
                    self.status.set("Download cancelled!")
                    self.cancel_button.config(state=tk.DISABLED)
                    self.download_button.config(state=tk.NORMAL)
                    self.pause_button.config(state=tk.DISABLED)
                    return

            file_url = link['href']
            if not file_url.startswith("http"):
                file_url = base_url + file_url

            file_name = unquote(file_url.split('/')[-1])

            total, used, free = shutil.disk_usage(full_path)
            if free < min_free_space:
                messagebox.showwarning("Warning", "Insufficient disk space.")
                break

            file_response = requests.get(file_url)
            file_response.raise_for_status()

            self.status.set(f"Downloading {file_name}")
            print(f"Downloading {file_name}")

            with open(os.path.join(full_path, file_name), 'wb') as f:
                f.write(file_response.content)

            curr_file += 1
            self.progress["value"] = curr_file
            self.root.update_idletasks()

        self.curr_downloading = False
        self.status.set("Download completed!")
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)

    def is_valid_file(self, file_url):
        file_name = unquote(file_url.split('/')[-1])
        regions = [self.region.get(), "(World)"]
        excluded_keywords = [
            "(Beta)", "(Alpha)", "(Proto)",
            "(Virtual Console)",
            "(Aftermarket)", "(Unl)",
            "(Sample)", "(Promo)", "(Demo)", "(Kiosk)",
        ]
        if regions and not any(region in file_name for region in regions):
            return False
        if any(keyword in file_name for keyword in excluded_keywords):
            return False
        return True

    def on_close(self):
        if not self.curr_downloading:
            self.root.destroy()
        elif messagebox.askokcancel("Confirm quit", "Quitting now will cancel any ongoing downloads. Are you sure?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()