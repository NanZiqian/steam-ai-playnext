import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import google.generativeai as genai
import threading
import webbrowser
import json
import os

# --- CONSTANTS ---
APP_DIR = "Config"
CONFIG_FILE = os.path.join(APP_DIR, "config.json")
MODEL_NAME = "gemini-3-flash-preview"

class SteamRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Steam Library AI Recommender ({MODEL_NAME})")
        self.root.geometry("650x850")
        
        # Ensure app directory exists
        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- INPUT SECTION ---
        input_frame = ttk.LabelFrame(root, text="Configuration", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Steam ID
        ttk.Label(input_frame, text="Steam ID (64-bit):").grid(row=0, column=0, sticky="w", pady=2)
        self.steam_id_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.steam_id_var, width=40).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Button(input_frame, text="?", width=3, command=lambda: self.open_url("https://steamid.io/")).grid(row=0, column=2)

        # Steam API Key
        ttk.Label(input_frame, text="Steam Web API Key:").grid(row=1, column=0, sticky="w", pady=2)
        self.steam_key_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.steam_key_var, show="*", width=40).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Button(input_frame, text="Get Key", command=lambda: self.open_url("https://steamcommunity.com/dev/apikey")).grid(row=1, column=2)

        # Gemini API Key
        ttk.Label(input_frame, text="Gemini API Key:").grid(row=2, column=0, sticky="w", pady=2)
        self.gemini_key_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.gemini_key_var, show="*", width=40).grid(row=2, column=1, sticky="w", padx=5)
        ttk.Button(input_frame, text="Get Key", command=lambda: self.open_url("https://aistudio.google.com/app/apikey")).grid(row=2, column=2)

        # Proxy Settings
        ttk.Label(input_frame, text="Proxy (VPN) URL:").grid(row=3, column=0, sticky="w", pady=2)
        self.proxy_var = tk.StringVar()
        proxy_entry = ttk.Entry(input_frame, textvariable=self.proxy_var, width=40)
        proxy_entry.grid(row=3, column=1, sticky="w", padx=5)
        ttk.Label(input_frame, text="(e.g. http://127.0.0.1:7890)").grid(row=3, column=2, sticky="w")

        # Config Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.save_config_btn = ttk.Button(btn_frame, text="Save Config", command=self.save_configuration)
        self.save_config_btn.pack(side="left", padx=5)
        
        self.load_btn = ttk.Button(btn_frame, text="Load Steam Library", command=self.start_fetch_library)
        self.load_btn.pack(side="left", padx=5)

        # Status Label
        self.status_var = tk.StringVar(value="Ready to load.")
        self.status_label = ttk.Label(input_frame, textvariable=self.status_var, foreground="gray")
        self.status_label.grid(row=5, column=0, columnspan=3)

        # --- REQUEST SECTION ---
        req_frame = ttk.LabelFrame(root, text="What do you want to play?", padding=10)
        req_frame.pack(fill="x", padx=10, pady=5)
        
        self.user_query = tk.Text(req_frame, height=4, width=50)
        self.user_query.pack(fill="x", pady=5)
        self.user_query.insert("1.0", "I want an exciting adventure with interesting companions, like Fallout 4 or Outer Worlds.")

        # Options Frame (Num games + Import)
        opts_frame = ttk.Frame(req_frame)
        opts_frame.pack(fill="x", pady=2)
        
        ttk.Label(opts_frame, text="Recommended Game number:").pack(side="left")
        self.num_games_var = tk.IntVar(value=5)
        ttk.Spinbox(opts_frame, from_=1, to=20, textvariable=self.num_games_var, width=3).pack(side="left", padx=5)
        
        ttk.Button(opts_frame, text="Import Prompt from .txt", command=self.import_prompt_file).pack(side="left", padx=10)
        
        self.rec_btn = ttk.Button(req_frame, text="Get AI Recommendations", command=self.start_get_recommendation, state="disabled")
        self.rec_btn.pack(side="right")

        # --- RESULTS SECTION ---
        res_frame = ttk.LabelFrame(root, text="Recommendations", padding=10)
        res_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_area = scrolledtext.ScrolledText(res_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        self.result_area.pack(fill="both", expand=True)

        # Internal Data
        self.games_list = []
        
        # Load config on startup if exists
        self.load_configuration()

    def open_url(self, url):
        webbrowser.open(url)

    def log(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def configure_proxy(self):
        """Sets environment variables for Proxy if provided."""
        proxy_url = self.proxy_var.get().strip()
        if proxy_url:
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            self.log(f"Proxy configured: {proxy_url}")
        else:
            # clear if empty
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)

    # --- CONFIG MANAGEMENT ---
    def save_configuration(self):
        data = {
            "steam_id": self.steam_id_var.get().strip(),
            "steam_key": self.steam_key_var.get().strip(),
            "gemini_key": self.gemini_key_var.get().strip(),
            "proxy": self.proxy_var.get().strip()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Saved", f"Configuration saved to {CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config: {e}")

    def load_configuration(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.steam_id_var.set(data.get("steam_id", ""))
                self.steam_key_var.set(data.get("steam_key", ""))
                self.gemini_key_var.set(data.get("gemini_key", ""))
                self.proxy_var.set(data.get("proxy", ""))
        except Exception as e:
            self.log(f"Failed to load config: {e}")

    def import_prompt_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=APP_DIR,
            title="Select Prompt File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.user_query.delete("1.0", tk.END)
                    self.user_query.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    # --- STEP 1: FETCH LIBRARY ---
    def start_fetch_library(self):
        steam_id = self.steam_id_var.get().strip()
        api_key = self.steam_key_var.get().strip()

        if not steam_id or not api_key:
            messagebox.showerror("Error", "Please enter both Steam ID and Steam API Key.")
            return

        self.configure_proxy() # Apply proxy before request
        self.load_btn.config(state="disabled")
        self.log("Fetching library from Steam...")
        
        threading.Thread(target=self.fetch_library_thread, args=(steam_id, api_key), daemon=True).start()

    def fetch_library_thread(self, steam_id, api_key):
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': api_key,
            'steamid': steam_id,
            'format': 'json',
            'include_appinfo': 1,
            'include_played_free_games': 1
        }

        try:
            # Requests will automatically use the environment variables set in configure_proxy
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']
                self.games_list = [g['name'] for g in games]
                count = len(self.games_list)
                self.root.after(0, lambda: self.finish_fetch(True, f"Successfully loaded {count} games."))
            else:
                msg = "No games found. Check: 1. Profile Privacy (Public?) 2. Steam ID"
                self.root.after(0, lambda: self.finish_fetch(False, msg))

        except Exception as e:
            self.root.after(0, lambda: self.finish_fetch(False, str(e)))

    def finish_fetch(self, success, message):
        self.log(message)
        self.load_btn.config(state="normal")
        if success:
            self.rec_btn.config(state="normal")
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    # --- STEP 2: GET AI RECOMMENDATION ---
    def start_get_recommendation(self):
        gemini_key = self.gemini_key_var.get().strip()
        query = self.user_query.get("1.0", tk.END).strip()
        try:
            num_games = self.num_games_var.get()
        except:
            num_games = 5

        if not gemini_key:
            messagebox.showerror("Error", "Please enter your Gemini API Key.")
            return
        
        if not query:
            messagebox.showerror("Error", "Please explain what kind of game you want.")
            return

        self.configure_proxy() # Apply proxy before request
        self.rec_btn.config(state="disabled")
        self.result_area.delete("1.0", tk.END)
        self.result_area.insert("1.0", f"Thinking using {MODEL_NAME}... (Check Proxy if stuck)")
        self.log(f"Sending data to {MODEL_NAME}...")

        threading.Thread(target=self.get_ai_response, args=(gemini_key, query, num_games), daemon=True).start()

    def get_ai_response(self, api_key, user_query, num_games):
        try:
            genai.configure(api_key=api_key)
            
            # Note: Gemini 3.0 Flash Preview is used here.
            # If 3.0 fails for you, change this string back to gemini-2.0-flash-exp or gemini-1.5-flash
            model = genai.GenerativeModel(MODEL_NAME)

            games_str = ", ".join(self.games_list)
            
            prompt = f"""
            I am a gamer with the following games in my Steam library:
            {games_str}

            I want you to recommend {num_games} games FROM THIS LIST ONLY based on this request:
            "{user_query}"

            Format the response nicely. For each recommendation:
            1. Name of the game
            2. Why it fits my request (be specific)
            
            If the game is not in my list, do not recommend it.
            """

            response = model.generate_content(prompt)
            text = response.text
            
            self.root.after(0, lambda: self.display_result(text))

        except Exception as e:
            self.root.after(0, lambda: self.display_error(str(e)))

    def display_result(self, text):
        self.result_area.delete("1.0", tk.END)
        self.result_area.insert("1.0", text)
        self.log("Recommendation complete.")
        self.rec_btn.config(state="normal")

    def display_error(self, error_msg):
        self.result_area.delete("1.0", tk.END)
        self.result_area.insert("1.0", f"Error from AI: {error_msg}\n\nTip: If this is a connection error, try verifying your Proxy URL.")
        self.log("Error occurred.")
        self.rec_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteamRecommenderApp(root)
    root.mainloop()