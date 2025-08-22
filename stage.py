import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import threading
import time
import random
import json
import os
from urllib.parse import urljoin, urlparse

class LinkCollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Website Link Collector")
        self.stop_event = threading.Event()
        
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self.root, text="Enter Website URL:").pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        self.collect_btn = tk.Button(button_frame, text="Collect Links", command=self.collect_links)
        self.collect_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_collection, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.root, text="Ready")
        self.status_label.pack(pady=(0,5))
        
        self.links_text = scrolledtext.ScrolledText(self.root, width=60, height=20)
        self.links_text.pack(pady=5)
        
    def collect_links(self):
        def worker():
            url = self.url_entry.get().strip()
            if not url:
                # Use root.after to show UI messages from the main thread
                self.root.after(0, lambda: messagebox.showwarning("Input Error", "Please enter a website URL."))
                self.root.after(0, lambda: self.collect_btn.config(state="normal"))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
                return

            # Normalize URL (add scheme if missing)
            if "://" not in url:
                url = "http://" + url

            # small random delay to be polite
            time.sleep(random.uniform(0.5, 1.5))

            links_result = []
            error_msg = None
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
                session = requests.Session()
                resp = session.get(url, headers=headers, timeout=10)
                resp.raise_for_status()

                # Parse the page
                parser = "html.parser"
                try:
                    soup = BeautifulSoup(resp.text, 'lxml')
                except Exception:
                    soup = BeautifulSoup(resp.text, parser)

                raw_hrefs = [a.get('href') for a in soup.find_all('a', href=True)]

                seen = set()
                for href in raw_hrefs:
                    if not href:
                        continue
                    href = href.strip()
                    # skip fragments, javascript/mailto/tel/data schemes, and single-symbol hrefs
                    lch = href.lower()
                    if (href.startswith('#') or
                        lch.startswith('javascript:') or
                        lch.startswith('mailto:') or
                        lch.startswith('tel:') or
                        lch.startswith('sms:') or
                        lch.startswith('data:') or
                        (len(href) == 1 and not href.isalnum())):
                        continue

                    # Convert relative URLs to absolute using the final response URL
                    abs_url = urljoin(resp.url, href)

                    # Keep only http(s)
                    scheme = urlparse(abs_url).scheme.lower()
                    if scheme not in ('http', 'https'):
                        continue

                    # Deduplicate while preserving order
                    if abs_url not in seen:
                        seen.add(abs_url)
                        links_result.append(abs_url)

            except Exception as e:
                error_msg = str(e)

            # Update UI on main thread
            def update_ui():
                self.links_text.delete(1.0, tk.END)
                if error_msg:
                    messagebox.showerror("Error", f"Failed to fetch links: {error_msg}")
                    self.status_label.config(text="Error")
                else:
                    if links_result:
                        self.links_text.insert(tk.END, "\n".join(links_result))
                        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "links.json")
                        try:
                            with open(json_path, "w", encoding="utf-8") as f:
                                json.dump(links_result, f, ensure_ascii=False, indent=2)
                            self.status_label.config(text=f"Done — {len(links_result)} links")
                        except Exception as e:
                            messagebox.showwarning("Save Error", f"Could not save links.json: {e}")
                            self.status_label.config(text="Done (not saved)")
                    else:
                        self.links_text.insert(tk.END, "No links found.")
                        self.status_label.config(text="No links found")
                self.collect_btn.config(state="normal")

            self.root.after(0, update_ui)

        # disable button and update status immediately (from main thread)
        self.collect_btn.config(state="disabled")
        self.status_label.config(text="Collecting...")
        threading.Thread(target=worker, daemon=True).start()
        
    def stop_collection(self):
        self.stop_event.set()
        self.status_label.config(text="Stopping...")
        
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
        
    def update_links_text(self, links):
        self.root.after(0, lambda: self.links_text.insert(tk.END, "\n".join(links) + "\n"))
        
    def collection_finished(self):
        self.root.after(0, lambda: self.collect_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
        
if __name__ == "__main__":
    root = tk.Tk()
    app = LinkCollectorApp(root)
    root.mainloop()