"""
Multi-Engine TTS - Free Text-to-Speech Desktop Application
Modern GUI using CustomTkinter with Multiple TTS Engines
- Edge TTS: Microsoft Neural Voices (Online)
- Piper TTS: High-Quality Local Voices (Offline)

Author: Happy Learning-GP
YouTube: https://www.youtube.com/@happylearning-gp
GitHub: https://github.com/ganapap1/TTS_NO_API

Free and Open Source - MIT License
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
import threading
import asyncio
from pathlib import Path
from datetime import datetime

# Import TTS engines
from tts_engines import EdgeTTSEngine, PiperTTSEngine

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configuration file for saving settings
CONFIG_FILE = "tts_config.json"

# Application version
VERSION = "2.0.0"


class EdgeTTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title(f"Multi-Engine TTS - Free Text-to-Speech v{VERSION}")
        self.geometry("900x800")
        self.minsize(800, 750)

        # Center window on screen
        self.update_idletasks()
        width = 900
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Initialize TTS engines
        self.engines = {
            'edge': EdgeTTSEngine(),
            'piper': PiperTTSEngine()
        }
        self.current_engine = self.engines['edge']

        # Load voices from current engine
        self.voice_categories = self.current_engine.get_voices()

        # Flatten voices for dropdown
        # all_voices maps voice_id -> description
        self.all_voices = {}
        for category, voices in self.voice_categories.items():
            self.all_voices.update(voices)

        # Create display name mapping for better UX
        # voice_display maps display_name -> voice_id
        self.voice_display = {}
        self.voice_id_to_display = {}
        for voice_id, desc in self.all_voices.items():
            # Create a shorter display name from the description
            display_name = desc.split(' [')[0].split(' (')[0]  # Remove status tags
            self.voice_display[display_name] = voice_id
            self.voice_id_to_display[voice_id] = display_name

        # Variables
        self.engine_var = ctk.StringVar(value='edge')
        # voice_var stores the actual voice_id
        self.voice_var = ctk.StringVar(value='en-US-JennyNeural')
        # voice_display_var stores the display name for the dropdown
        self.voice_display_var = ctk.StringVar(value=self.voice_id_to_display.get('en-US-JennyNeural', 'Jenny - Female, Friendly'))
        self.speed_var = ctk.DoubleVar(value=1.0)
        self.pitch_var = ctk.DoubleVar(value=0)
        self.volume_var = ctk.DoubleVar(value=0)

        # Generate default output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = str(Path.cwd() / f"speech_{timestamp}.mp3")
        self.output_path_var = ctk.StringVar(value=default_output)

        self.char_count_var = ctk.StringVar(value="Characters: 0")
        self.word_count_var = ctk.StringVar(value="Words: 0")
        self.status_var = ctk.StringVar(value="Ready - 100% FREE!")

        # Load saved settings
        self.load_settings()

        # Create UI
        self.create_widgets()

        # Update stats initially
        self.update_stats()

    def create_widgets(self):
        # Create scrollable frame for all content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        main_frame = self.scrollable_frame

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎙️ Multi-Engine TTS - Free Text-to-Speech",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 5))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Edge TTS (Online) + Piper TTS (Offline) - 100% FREE",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 5))

        # Channel links row (visible at top)
        top_links_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_links_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top_links_frame,
            text="Subscribe on YouTube",
            width=140,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color="#333333",
            hover_color="#555555",
            command=lambda: self.open_url("https://www.youtube.com/@happylearning-gp")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top_links_frame,
            text="Star on GitHub",
            width=120,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color="#333333",
            hover_color="#555555",
            command=lambda: self.open_url("https://github.com/ganapap1/TTS_NO_API")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top_links_frame,
            text="About",
            width=60,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color="#888888",
            hover_color="#333333",
            command=self.show_about
        ).pack(side="right", padx=5)

        # Engine Selection Section
        engine_frame = ctk.CTkFrame(main_frame)
        engine_frame.pack(fill="x", pady=(0, 10))

        engine_inner = ctk.CTkFrame(engine_frame, fg_color="transparent")
        engine_inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            engine_inner,
            text="TTS Engine:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        ).pack(side="left", padx=5)

        self.engine_menu = ctk.CTkOptionMenu(
            engine_inner,
            variable=self.engine_var,
            values=["edge", "piper"],
            command=self.on_engine_change,
            width=200
        )
        self.engine_menu.pack(side="left", padx=5)

        self.engine_status_label = ctk.CTkLabel(
            engine_inner,
            text="🌐 Online - Microsoft Edge Neural Voices",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        self.engine_status_label.pack(side="left", padx=10)

        # Download voices button (for Piper)
        self.download_btn = ctk.CTkButton(
            engine_inner,
            text="📥 Download Voices",
            width=130,
            command=self.show_download_manager,
            state="disabled"
        )
        self.download_btn.pack(side="right", padx=5)

        # Text Input Section
        text_frame = ctk.CTkFrame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))

        text_header = ctk.CTkFrame(text_frame, fg_color="transparent")
        text_header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            text_header,
            text="Input Text:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")

        # Clear button
        clear_btn = ctk.CTkButton(
            text_header,
            text="Clear",
            width=60,
            height=25,
            command=self.clear_text
        )
        clear_btn.pack(side="right", padx=5)

        self.text_box = ctk.CTkTextbox(
            text_frame,
            height=180,
            font=ctk.CTkFont(size=11)
        )
        self.text_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.text_box.bind("<KeyRelease>", lambda e: self.update_stats())

        # Import button
        import_btn = ctk.CTkButton(
            text_frame,
            text="📁 Import Text File",
            command=self.import_text_file
        )
        import_btn.pack(padx=10, pady=(0, 10))

        # Voice Settings and Generate Button Container
        settings_container = ctk.CTkFrame(main_frame)
        settings_container.pack(fill="x", pady=(0, 10))

        # Left side - Voice Settings
        settings_frame = ctk.CTkFrame(settings_container)
        settings_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            settings_frame,
            text="Voice Settings:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))

        # Voice selection
        voice_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        voice_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(voice_frame, text="Voice:", width=80).pack(side="left", padx=5)
        self.voice_menu = ctk.CTkOptionMenu(
            voice_frame,
            variable=self.voice_display_var,
            values=list(self.voice_display.keys()),
            command=self.on_voice_display_change,
            width=220
        )
        self.voice_menu.pack(side="left", padx=5)

        # Status label (shows download status for Piper voices)
        self.voice_status_label = ctk.CTkLabel(
            voice_frame,
            text="",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        self.voice_status_label.pack(side="left", padx=5)
        self.update_voice_status()

        # Speed slider
        speed_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        speed_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(speed_frame, text="Speed:", width=80).pack(side="left", padx=5)
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.5,
            to=2.0,
            variable=self.speed_var,
            command=self.update_speed_label,
            width=200,
            height=20,
            button_color="#3B8ED0",
            button_hover_color="#36719F",
            progress_color="#3B8ED0"
        )
        self.speed_slider.pack(side="left", padx=5)

        self.speed_label = ctk.CTkLabel(speed_frame, text="1.00x", width=50)
        self.speed_label.pack(side="left", padx=5)

        # Pitch slider
        pitch_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        pitch_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(pitch_frame, text="Pitch:", width=80).pack(side="left", padx=5)
        self.pitch_slider = ctk.CTkSlider(
            pitch_frame,
            from_=-50,
            to=50,
            variable=self.pitch_var,
            command=self.update_pitch_label,
            width=200,
            height=20,
            button_color="#3B8ED0",
            button_hover_color="#36719F",
            progress_color="#3B8ED0"
        )
        self.pitch_slider.pack(side="left", padx=5)

        self.pitch_label = ctk.CTkLabel(pitch_frame, text="+0Hz", width=50)
        self.pitch_label.pack(side="left", padx=5)

        # Volume slider
        volume_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(volume_frame, text="Volume:", width=80).pack(side="left", padx=5)
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=-50,
            to=50,
            variable=self.volume_var,
            command=self.update_volume_label,
            width=200,
            height=20,
            button_color="#3B8ED0",
            button_hover_color="#36719F",
            progress_color="#3B8ED0"
        )
        self.volume_slider.pack(side="left", padx=5)

        self.volume_label = ctk.CTkLabel(volume_frame, text="+0%", width=50)
        self.volume_label.pack(side="left", padx=5)

        # Right side - Generate Button
        button_frame = ctk.CTkFrame(settings_container, fg_color="transparent")
        button_frame.pack(side="right", padx=10, pady=10)

        self.generate_btn = ctk.CTkButton(
            button_frame,
            text="🎵 Generate MP3",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            height=120,
            command=self.generate_mp3
        )
        self.generate_btn.pack()

        # Statistics Section
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=(0, 8))

        self.char_label = ctk.CTkLabel(
            stats_frame,
            textvariable=self.char_count_var,
            font=ctk.CTkFont(size=12)
        )
        self.char_label.pack(side="left", padx=20, pady=8)

        self.word_label = ctk.CTkLabel(
            stats_frame,
            textvariable=self.word_count_var,
            font=ctk.CTkFont(size=12)
        )
        self.word_label.pack(side="left", padx=20, pady=8)

        # FREE badge
        free_label = ctk.CTkLabel(
            stats_frame,
            text="💚 Cost: $0.00 (FREE!)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff00"
        )
        free_label.pack(side="right", padx=20, pady=8)

        # Progress Section
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            progress_frame,
            text="Progress:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=10, pady=(5, 2))

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=3)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            progress_frame,
            textvariable=self.status_var,
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(padx=10, pady=(0, 5))

        # Output Section
        output_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        output_container.pack(fill="x", pady=(0, 8))

        controls_frame = ctk.CTkFrame(output_container, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            controls_frame,
            text="Output:",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=60
        ).pack(side="left", padx=(0, 5))

        self.output_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.output_path_var,
            width=300
        )
        self.output_entry.pack(side="left", padx=(0, 5))

        browse_btn = ctk.CTkButton(
            controls_frame,
            text="Browse",
            width=70,
            command=self.browse_output
        )
        browse_btn.pack(side="left", padx=2)

        self.play_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ Play",
            width=70,
            command=self.play_audio,
            state="disabled"
        )
        self.play_btn.pack(side="left", padx=2)

        self.open_folder_btn = ctk.CTkButton(
            controls_frame,
            text="📁 Folder",
            width=70,
            command=self.open_folder
        )
        self.open_folder_btn.pack(side="left", padx=2)

        theme_btn = ctk.CTkButton(
            controls_frame,
            text="🌓 Theme",
            width=70,
            command=self.toggle_theme
        )
        theme_btn.pack(side="left", padx=2)

        # Footer
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))

        footer_label = ctk.CTkLabel(
            footer_frame,
            text=f"Multi-Engine TTS v{VERSION} | Created by Happy Learning-GP",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        footer_label.pack()

    def clear_text(self):
        """Clear the text box"""
        self.text_box.delete("1.0", "end")
        self.update_stats()

    def on_engine_change(self, choice):
        """Handle engine selection change"""
        self.current_engine = self.engines[choice]

        # Update engine status label and controls
        if choice == 'edge':
            self.engine_status_label.configure(
                text="🌐 Online - Microsoft Edge Neural Voices"
            )
            self.download_btn.configure(state="disabled")
            # Enable voice modification sliders for Edge TTS
            self.speed_slider.configure(state="normal")
            self.pitch_slider.configure(state="normal")
            self.volume_slider.configure(state="normal")
        else:
            self.engine_status_label.configure(
                text="💻 Offline - Piper Local Neural Voices"
            )
            self.download_btn.configure(state="normal")
            # Disable voice modification sliders for Piper (not supported)
            self.speed_slider.configure(state="disabled")
            self.pitch_slider.configure(state="disabled")
            self.volume_slider.configure(state="disabled")
            # Reset to default values
            self.speed_var.set(1.0)
            self.pitch_var.set(0)
            self.volume_var.set(0)
            self.speed_label.configure(text="1.00x")
            self.pitch_label.configure(text="+0Hz")
            self.volume_label.configure(text="+0%")

        # Update voices for new engine
        self.voice_categories = self.current_engine.get_voices()
        self.all_voices = {}
        for category, voices in self.voice_categories.items():
            self.all_voices.update(voices)

        # Rebuild display name mappings
        self.voice_display = {}
        self.voice_id_to_display = {}
        for voice_id, desc in self.all_voices.items():
            display_name = desc.split(' [')[0].split(' (')[0]
            self.voice_display[display_name] = voice_id
            self.voice_id_to_display[voice_id] = display_name

        # Update voice dropdown with display names
        display_names = list(self.voice_display.keys())
        self.voice_menu.configure(values=display_names)

        # Select first voice
        if display_names:
            self.voice_display_var.set(display_names[0])
            first_voice_id = self.voice_display[display_names[0]]
            self.voice_var.set(first_voice_id)
            self.update_voice_status()

        # Update output extension
        ext = self.current_engine.get_output_extension()
        current_path = self.output_path_var.get()
        if current_path:
            base = os.path.splitext(current_path)[0]
            self.output_path_var.set(base + ext)

    def show_download_manager(self):
        """Show voice download manager dialog"""
        if not isinstance(self.current_engine, PiperTTSEngine):
            return

        # Create download dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Download Piper Voices")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text="Available Piper Voices",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Scrollable frame for voices
        scroll_frame = ctk.CTkScrollableFrame(dialog, height=250)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # List all voices with download buttons
        piper_engine = self.current_engine
        for category, voices in piper_engine.PIPER_VOICES.items():
            # Category header
            ctk.CTkLabel(
                scroll_frame,
                text=category,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(anchor="w", pady=(10, 5))

            for voice_id, info in voices.items():
                voice_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                voice_frame.pack(fill="x", pady=2)

                # Voice name
                ctk.CTkLabel(
                    voice_frame,
                    text=info['name'],
                    width=200
                ).pack(side="left", padx=5)

                # Status/Download button
                if piper_engine.is_voice_downloaded(voice_id):
                    ctk.CTkLabel(
                        voice_frame,
                        text="✓ Downloaded",
                        text_color="green",
                        width=100
                    ).pack(side="right", padx=5)
                else:
                    btn = ctk.CTkButton(
                        voice_frame,
                        text="Download",
                        width=80,
                        command=lambda vid=voice_id, dlg=dialog: self.download_voice(vid, dlg)
                    )
                    btn.pack(side="right", padx=5)

        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy
        ).pack(pady=10)

    def download_voice(self, voice_id, dialog):
        """Download a Piper voice"""
        if not isinstance(self.current_engine, PiperTTSEngine):
            return

        def do_download():
            try:
                self.after(0, lambda: self.status_var.set(f"Downloading {voice_id}..."))
                self.after(0, lambda: self.progress_bar.set(0.1))

                def progress_cb(progress, status):
                    self.after(0, lambda p=progress, s=status: (
                        self.progress_bar.set(p),
                        self.status_var.set(s)
                    ))

                self.current_engine.download_voice(voice_id, progress_cb)

                self.after(0, lambda: self.status_var.set(f"✅ Downloaded {voice_id}"))
                self.after(0, lambda: self.progress_bar.set(1.0))

                # Refresh voice list
                self.after(0, lambda: self.on_engine_change(self.engine_var.get()))

                # Refresh dialog
                self.after(100, lambda: (dialog.destroy(), self.show_download_manager()))

            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"❌ Download failed: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to download voice:\n{e}"))

        threading.Thread(target=do_download, daemon=True).start()

    def on_voice_display_change(self, display_name):
        """Handle voice selection change from dropdown"""
        # Map display name back to voice_id
        voice_id = self.voice_display.get(display_name, '')
        if voice_id:
            self.voice_var.set(voice_id)
        self.update_voice_status()

    def update_voice_status(self):
        """Update voice status label"""
        voice_id = self.voice_var.get()

        # For Piper, show download status
        if isinstance(self.current_engine, PiperTTSEngine):
            if self.current_engine.is_voice_downloaded(voice_id):
                self.voice_status_label.configure(text="✓ Ready", text_color="green")
            else:
                self.voice_status_label.configure(text="⚠ Not Downloaded", text_color="orange")
        else:
            # Edge TTS - always ready (online)
            self.voice_status_label.configure(text="🌐 Online", text_color="gray")

    def update_speed_label(self, value):
        """Update speed label when slider changes"""
        self.speed_label.configure(text=f"{value:.2f}x")

    def update_pitch_label(self, value):
        """Update pitch label when slider changes"""
        pitch_int = int(value)
        sign = "+" if pitch_int >= 0 else ""
        self.pitch_label.configure(text=f"{sign}{pitch_int}Hz")

    def update_volume_label(self, value):
        """Update volume label when slider changes"""
        vol_int = int(value)
        sign = "+" if vol_int >= 0 else ""
        self.volume_label.configure(text=f"{sign}{vol_int}%")

    def update_stats(self):
        """Update character and word count"""
        text = self.text_box.get("1.0", "end-1c")
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        self.char_count_var.set(f"Characters: {char_count:,}")
        self.word_count_var.set(f"Words: {word_count:,}")

    def import_text_file(self):
        """Import text from a file"""
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", text)
                self.update_stats()
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def browse_output(self):
        """Browse for output file location"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"speech_{timestamp}.mp3"

        current_path = self.output_path_var.get()
        initial_dir = os.path.dirname(current_path) if current_path else os.getcwd()

        file_path = filedialog.asksaveasfilename(
            title="Save MP3 As",
            defaultextension=".mp3",
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")],
            initialfile=default_filename,
            initialdir=initial_dir
        )
        if file_path:
            self.output_path_var.set(file_path)

    def generate_mp3(self):
        """Generate audio from text using selected TTS engine"""
        text = self.text_box.get("1.0", "end-1c").strip()
        output_path = self.output_path_var.get()

        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert.")
            return

        if not output_path:
            messagebox.showwarning("Warning", "Please specify an output file path.")
            return

        # Check if engine is available
        if not self.current_engine.is_available():
            engine_name = self.current_engine.name
            if isinstance(self.current_engine, PiperTTSEngine):
                messagebox.showerror(
                    "Error",
                    f"{engine_name} is not available.\n\n"
                    "Please run: pip install piper-tts"
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"{engine_name} is not available.\n\n"
                    "Please run: pip install edge-tts"
                )
            return

        # Scroll to bottom to show progress
        self.scrollable_frame._parent_canvas.yview_moveto(1.0)

        # Disable generate button
        self.generate_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_var.set("Starting generation...")

        def generate():
            try:
                voice = self.voice_var.get()
                speed = self.speed_var.get()
                pitch = int(self.pitch_var.get())
                volume = int(self.volume_var.get())

                def progress_callback(progress, status):
                    self.after(0, lambda p=progress, s=status: (
                        self.progress_bar.set(p),
                        self.status_var.set(s)
                    ))

                # Generate using current engine
                self.current_engine.generate(
                    text=text,
                    voice=voice,
                    output_path=output_path,
                    speed=speed,
                    pitch=pitch,
                    volume=volume,
                    progress_callback=progress_callback
                )

                self.after(0, lambda: self.progress_bar.set(1.0))

                # Success
                file_size = os.path.getsize(output_path) / 1024  # KB
                ext = os.path.splitext(output_path)[1].upper()[1:]
                engine_name = self.current_engine.name

                self.after(0, lambda: self.status_var.set(
                    f"✅ Success! {ext} saved ({file_size:.1f} KB) - FREE!"
                ))
                self.after(0, lambda: self.play_btn.configure(state="normal"))
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Audio file generated successfully!\n\n"
                    f"Engine: {engine_name}\n"
                    f"File: {os.path.basename(output_path)}\n"
                    f"Size: {file_size:.1f} KB\n"
                    f"Cost: $0.00 (FREE!)"
                ))

            except ImportError as e:
                self.after(0, lambda: self.status_var.set(f"❌ Missing dependency"))
                self.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Missing dependency:\n{e}\n\n"
                    "Please check installation."
                ))
                self.after(0, lambda: self.progress_bar.set(0))

            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self.status_var.set(f"❌ Error: {error_msg[:50]}..."))
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to generate audio:\n{error_msg}"))
                self.after(0, lambda: self.progress_bar.set(0))

            finally:
                self.after(0, lambda: self.generate_btn.configure(state="normal"))

        # Run in separate thread
        threading.Thread(target=generate, daemon=True).start()

    def play_audio(self):
        """Play the generated MP3 file"""
        output_path = self.output_path_var.get()
        if os.path.exists(output_path):
            try:
                os.startfile(output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to play audio:\n{e}")
        else:
            messagebox.showwarning("Warning", "MP3 file not found. Generate it first.")

    def open_folder(self):
        """Open the folder containing the output file"""
        output_path = self.output_path_var.get()
        folder = os.path.dirname(output_path) or os.getcwd()
        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{e}")

    def toggle_theme(self):
        """Toggle between dark and light mode"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def open_url(self, url):
        """Open a URL in the default browser"""
        import webbrowser
        webbrowser.open(url)

    def show_about(self):
        """Show About dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("About Multi-Engine TTS")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 175
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            dialog,
            text="Multi-Engine TTS",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            dialog,
            text=f"Version {VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(
            dialog,
            text="Free Text-to-Speech Application\nEdge TTS (Online) + Piper TTS (Offline)",
            font=ctk.CTkFont(size=11),
            justify="center"
        ).pack(pady=5)

        # Author
        ctk.CTkLabel(
            dialog,
            text="Created by Happy Learning-GP",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(pady=(15, 5))

        # Links
        links_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        links_frame.pack(pady=10)

        ctk.CTkButton(
            links_frame,
            text="Subscribe on YouTube",
            width=180,
            fg_color="#FF0000",
            hover_color="#CC0000",
            command=lambda: self.open_url("https://www.youtube.com/@happylearning-gp")
        ).pack(pady=3)

        ctk.CTkButton(
            links_frame,
            text="Star on GitHub",
            width=180,
            fg_color="#333333",
            hover_color="#555555",
            command=lambda: self.open_url("https://github.com/ganapap1/TTS_NO_API")
        ).pack(pady=3)

        # License
        ctk.CTkLabel(
            dialog,
            text="MIT License - Free & Open Source",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        ).pack(pady=(10, 5))

        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            width=100,
            command=dialog.destroy
        ).pack(pady=10)

    def save_settings(self):
        """Save settings to config file"""
        config = {
            'engine': self.engine_var.get(),
            'voice': self.voice_var.get(),
            'speed': self.speed_var.get(),
            'pitch': self.pitch_var.get(),
            'volume': self.volume_var.get(),
            'output_path': self.output_path_var.get()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        """Load settings from config file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)

                # Load engine first
                saved_engine = config.get('engine', 'edge')
                if saved_engine in self.engines:
                    self.engine_var.set(saved_engine)
                    self.current_engine = self.engines[saved_engine]
                    self.voice_categories = self.current_engine.get_voices()
                    self.all_voices = {}
                    for category, voices in self.voice_categories.items():
                        self.all_voices.update(voices)

                # Rebuild display mappings for loaded engine
                self.voice_display = {}
                self.voice_id_to_display = {}
                for voice_id, desc in self.all_voices.items():
                    display_name = desc.split(' [')[0].split(' (')[0]
                    self.voice_display[display_name] = voice_id
                    self.voice_id_to_display[voice_id] = display_name

                # Load voice (must be valid for current engine)
                saved_voice = config.get('voice', '')
                if saved_voice in self.all_voices:
                    self.voice_var.set(saved_voice)
                    # Also set display var
                    display_name = self.voice_id_to_display.get(saved_voice, '')
                    if display_name:
                        self.voice_display_var.set(display_name)
                elif self.all_voices:
                    first_voice = list(self.all_voices.keys())[0]
                    self.voice_var.set(first_voice)
                    display_name = self.voice_id_to_display.get(first_voice, '')
                    if display_name:
                        self.voice_display_var.set(display_name)

                self.speed_var.set(config.get('speed', 1.0))
                self.pitch_var.set(config.get('pitch', 0))
                self.volume_var.set(config.get('volume', 0))
                self.output_path_var.set(config.get('output_path', str(Path.cwd() / "output.mp3")))
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def on_closing(self):
        """Handle window close event"""
        self.save_settings()
        self.destroy()


def main():
    app = EdgeTTSApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
