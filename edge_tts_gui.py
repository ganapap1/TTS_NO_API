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
        self.show_all_languages_var = ctk.BooleanVar(value=False)
        self.selected_language = ctk.StringVar(value="English (US)")  # User selected language

        # Piper supported languages (~40 from HuggingFace)
        self.piper_languages = [
            "Arabic", "Catalan", "Chinese", "Czech", "Danish", "Dutch", "English (GB)",
            "English (US)", "Finnish", "French", "German", "Greek", "Hungarian",
            "Icelandic", "Italian", "Japanese", "Kazakh", "Korean", "Nepali",
            "Norwegian", "Polish", "Portuguese (BR)", "Portuguese (PT)", "Romanian",
            "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", "Swedish",
            "Swahili", "Turkish", "Ukrainian", "Vietnamese", "Welsh"
        ]

        # Edge TTS supported languages (100+)
        self.edge_languages = [
            "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani",
            "Bangla", "Basque", "Bosnian", "Bulgarian", "Burmese", "Catalan",
            "Chinese (Cantonese)", "Chinese (Mandarin)", "Chinese (Taiwanese)",
            "Croatian", "Czech", "Danish", "Dutch", "English (AU)", "English (CA)",
            "English (GB)", "English (HK)", "English (IE)", "English (IN)",
            "English (KE)", "English (NZ)", "English (PH)", "English (SG)",
            "English (US)", "English (ZA)", "Estonian", "Filipino", "Finnish",
            "French", "French (BE)", "French (CA)", "French (CH)", "Galician",
            "Georgian", "German", "German (AT)", "German (CH)", "Greek", "Gujarati",
            "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish",
            "Italian", "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer",
            "Korean", "Lao", "Latvian", "Lithuanian", "Macedonian", "Malay",
            "Malayalam", "Maltese", "Marathi", "Mongolian", "Nepali", "Norwegian",
            "Pashto", "Persian", "Polish", "Portuguese (BR)", "Portuguese (PT)",
            "Punjabi", "Romanian", "Russian", "Serbian", "Sinhala", "Slovak",
            "Slovenian", "Somali", "Spanish", "Spanish (AR)", "Spanish (CO)",
            "Spanish (MX)", "Spanish (US)", "Sundanese", "Swahili", "Swedish",
            "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian", "Urdu", "Uzbek",
            "Vietnamese", "Welsh", "Zulu"
        ]

        # Language code mapping for filtering voices
        self.language_to_code = {
            "English (US)": "en", "English (GB)": "en", "English (AU)": "en",
            "English (CA)": "en", "English (IN)": "en", "English (IE)": "en",
            "English (NZ)": "en", "English (ZA)": "en", "English (HK)": "en",
            "English (KE)": "en", "English (PH)": "en", "English (SG)": "en",
            "Spanish": "es", "Spanish (AR)": "es", "Spanish (CO)": "es",
            "Spanish (MX)": "es", "Spanish (US)": "es",
            "French": "fr", "French (BE)": "fr", "French (CA)": "fr", "French (CH)": "fr",
            "German": "de", "German (AT)": "de", "German (CH)": "de",
            "Italian": "it", "Portuguese (BR)": "pt", "Portuguese (PT)": "pt",
            "Russian": "ru", "Chinese (Mandarin)": "zh", "Chinese (Cantonese)": "zh",
            "Chinese (Taiwanese)": "zh", "Chinese": "zh", "Japanese": "ja",
            "Korean": "ko", "Arabic": "ar", "Hindi": "hi", "Dutch": "nl",
            "Polish": "pl", "Turkish": "tr", "Vietnamese": "vi", "Thai": "th",
            "Greek": "el", "Czech": "cs", "Romanian": "ro", "Hungarian": "hu",
            "Danish": "da", "Finnish": "fi", "Norwegian": "nb", "Swedish": "sv",
            "Ukrainian": "uk", "Hebrew": "he", "Indonesian": "id", "Malay": "ms",
            "Filipino": "fil", "Slovak": "sk", "Slovenian": "sl", "Croatian": "hr",
            "Bulgarian": "bg", "Serbian": "sr", "Catalan": "ca", "Galician": "gl",
            "Basque": "eu", "Welsh": "cy", "Irish": "ga", "Icelandic": "is",
            "Latvian": "lv", "Lithuanian": "lt", "Estonian": "et", "Maltese": "mt",
            "Albanian": "sq", "Macedonian": "mk", "Bosnian": "bs", "Georgian": "ka",
            "Armenian": "hy", "Azerbaijani": "az", "Kazakh": "kk", "Uzbek": "uz",
            "Mongolian": "mn", "Nepali": "ne", "Bengali": "bn", "Bangla": "bn",
            "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Malayalam": "ml",
            "Marathi": "mr", "Gujarati": "gu", "Punjabi": "pa", "Urdu": "ur",
            "Persian": "fa", "Pashto": "ps", "Sinhala": "si", "Burmese": "my",
            "Khmer": "km", "Lao": "lo", "Javanese": "jv", "Sundanese": "su",
            "Swahili": "sw", "Amharic": "am", "Somali": "so", "Zulu": "zu",
            "Afrikaans": "af"
        }

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

        # Language selection with searchable dropdown
        lang_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(lang_frame, text="Language:", width=80).pack(side="left", padx=5)

        # Language button that opens searchable dropdown
        self.language_btn = ctk.CTkButton(
            lang_frame,
            textvariable=self.selected_language,
            width=200,
            height=28,
            fg_color=["#E5E5E5", "#2B2B2B"],
            hover_color=["#D5D5D5", "#3A3A3A"],
            border_width=2,
            border_color=["#CCCCCC", "#404040"],
            text_color=["#000000", "#FFFFFF"],
            anchor="w",
            command=self.show_language_selector
        )
        self.language_btn.pack(side="left", padx=5)

        # Store current language list reference
        self.current_language_list = self.edge_languages

        # Show all languages checkbox
        self.show_all_lang_checkbox = ctk.CTkCheckBox(
            lang_frame,
            text="Show all voices",
            variable=self.show_all_languages_var,
            command=self.on_language_filter_change,
            font=ctk.CTkFont(size=11)
        )
        self.show_all_lang_checkbox.pack(side="left", padx=15)

        # Voice selection
        voice_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        voice_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(voice_frame, text="Voice:", width=80).pack(side="left", padx=5)
        self.voice_menu = ctk.CTkOptionMenu(
            voice_frame,
            variable=self.voice_display_var,
            values=list(self.voice_display.keys()),
            command=self.on_voice_display_change,
            width=300
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
            # Update language list to Edge languages
            self.current_language_list = self.edge_languages
            if self.selected_language.get() not in self.edge_languages:
                self.selected_language.set("English (US)")
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
            # Update language list to Piper languages
            self.current_language_list = self.piper_languages
            if self.selected_language.get() not in self.piper_languages:
                self.selected_language.set("English (US)")

        # Update voice dropdown with filtered voices
        self.update_voice_dropdown()

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

        # Header frame with title and check button
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Available Piper Voices",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        # Check for new voices button
        ctk.CTkButton(
            header_frame,
            text="🔄 Check for New Voices",
            width=160,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda: self.check_for_new_voices(dialog)
        ).pack(side="right", padx=5)

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

    def show_language_selector(self):
        """Show searchable language selector dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Select Language")
        dialog.geometry("300x400")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog near the button
        dialog.update_idletasks()
        x = self.winfo_x() + 150
        y = self.winfo_y() + 200
        dialog.geometry(f"+{x}+{y}")

        # Search entry
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Search language...",
            textvariable=search_var,
            width=260
        )
        search_entry.pack(padx=15, pady=(15, 10))
        search_entry.focus_set()

        # Scrollable frame for language list
        scroll_frame = ctk.CTkScrollableFrame(dialog, height=300)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Store button references for filtering
        lang_buttons = []

        def select_language(lang):
            self.selected_language.set(lang)
            dialog.destroy()
            self.on_language_change(lang)

        def create_buttons(filter_text=""):
            # Clear existing buttons
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            lang_buttons.clear()

            filter_lower = filter_text.lower()
            for lang in self.current_language_list:
                if filter_lower in lang.lower():
                    btn = ctk.CTkButton(
                        scroll_frame,
                        text=lang,
                        anchor="w",
                        height=28,
                        fg_color="transparent",
                        text_color=["#000000", "#FFFFFF"],
                        hover_color=["#ECECEC", "#3E3E3E"],
                        command=lambda l=lang: select_language(l)
                    )
                    btn.pack(fill="x", pady=1)
                    lang_buttons.append(btn)

        # Initial population
        create_buttons()

        # Filter on search
        def on_search(*args):
            create_buttons(search_var.get())

        search_var.trace_add("write", on_search)

        # Handle Enter key to select first match
        def on_enter(event):
            if lang_buttons:
                # Get first visible button's text
                first_lang = lang_buttons[0].cget("text")
                select_language(first_lang)

        search_entry.bind("<Return>", on_enter)

        # Handle Escape to close
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def on_language_change(self, selected_lang: str):
        """Handle language selection change - filter voices by selected language"""
        self.update_voice_dropdown()

        # For Piper: check if voices are downloaded for this language
        if isinstance(self.current_engine, PiperTTSEngine):
            lang_code = self.language_to_code.get(selected_lang, selected_lang[:2].lower())
            if not self.current_engine.has_downloaded_voices_for_language(lang_code):
                self.show_language_not_available_dialog(lang_code)

    def on_language_filter_change(self):
        """Handle 'Show all voices' checkbox change"""
        self.update_voice_dropdown()

    def update_voice_dropdown(self):
        """Update voice dropdown based on language selection"""
        show_all = self.show_all_languages_var.get()
        selected_lang = self.selected_language.get()
        lang_code = self.language_to_code.get(selected_lang, selected_lang[:2].lower())

        # Get all voices from current engine
        all_voice_categories = self.current_engine.get_voices()

        if show_all:
            # Show all voices without filtering
            self.voice_categories = all_voice_categories
        else:
            # Filter voices by selected language
            filtered = {}
            for category, voices in all_voice_categories.items():
                filtered_voices = {}
                for voice_id, voice_desc in voices.items():
                    # Get voice language code
                    if isinstance(self.current_engine, PiperTTSEngine):
                        voice_lang = self.current_engine.get_voice_language(voice_id)
                    else:
                        # Edge TTS: extract from voice_id (e.g., en-US-JennyNeural -> en)
                        voice_lang = voice_id.split('-')[0].lower() if '-' in voice_id else None

                    if voice_lang == lang_code:
                        filtered_voices[voice_id] = voice_desc

                if filtered_voices:
                    filtered[category] = filtered_voices

            self.voice_categories = filtered if filtered else all_voice_categories

        # Rebuild voice display mappings
        self.all_voices = {}
        for category, voices in self.voice_categories.items():
            self.all_voices.update(voices)

        self.voice_display = {}
        self.voice_id_to_display = {}
        for voice_id, desc in self.all_voices.items():
            # Remove status tags and indentation for display name
            display_name = desc.strip().split(' [')[0].split(' (')[0]
            self.voice_display[display_name] = voice_id
            self.voice_id_to_display[voice_id] = display_name

        # Update dropdown values
        display_names = list(self.voice_display.keys())
        if display_names:
            self.voice_menu.configure(values=display_names)

            # Try to keep current voice if still available
            current_voice = self.voice_var.get()
            if current_voice in self.voice_id_to_display:
                self.voice_display_var.set(self.voice_id_to_display[current_voice])
            else:
                # Select first voice
                self.voice_display_var.set(display_names[0])
                self.voice_var.set(self.voice_display[display_names[0]])

            self.update_voice_status()

    def check_for_new_voices(self, parent_dialog):
        """Check for new voices in user's downloaded languages only"""
        if not isinstance(self.current_engine, PiperTTSEngine):
            return

        # Get languages that user has already downloaded
        downloaded_langs = self.current_engine.get_downloaded_languages()

        if not downloaded_langs:
            messagebox.showinfo(
                "No Languages Installed",
                "You haven't downloaded any voices yet.\n\nDownload voices first to check for updates."
            )
            return

        # Check for new voices in those languages
        new_voices = {}
        lang_names_map = {
            'en': 'English', 'es': 'Spanish', 'it': 'Italian', 'fr': 'French',
            'de': 'German', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'nl': 'Dutch', 'pl': 'Polish',
            'uk': 'Ukrainian', 'vi': 'Vietnamese', 'ar': 'Arabic', 'tr': 'Turkish',
            'hi': 'Hindi', 'cs': 'Czech', 'da': 'Danish', 'fi': 'Finnish',
            'el': 'Greek', 'hu': 'Hungarian', 'is': 'Icelandic', 'nb': 'Norwegian',
            'ro': 'Romanian', 'sk': 'Slovak', 'sv': 'Swedish', 'sw': 'Swahili',
            'ka': 'Georgian'
        }

        # Scan for new voices
        for category, voices in self.current_engine.PIPER_VOICES.items():
            for voice_id, info in voices.items():
                voice_lang = self.current_engine.get_voice_language(voice_id)

                # Only check voices in downloaded languages
                if voice_lang in downloaded_langs:
                    # Check if this voice is NOT downloaded
                    if not self.current_engine.is_voice_downloaded(voice_id):
                        lang_name = lang_names_map.get(voice_lang, voice_lang.upper())
                        if lang_name not in new_voices:
                            new_voices[lang_name] = []
                        new_voices[lang_name].append(info['name'])

        # Show results
        if not new_voices:
            messagebox.showinfo(
                "No New Voices",
                "You have all available voices for your installed languages!"
            )
            return

        # Create dialog showing new voices
        result_dialog = ctk.CTkToplevel(self)
        result_dialog.title("New Voices Available")
        result_dialog.geometry("400x300")
        result_dialog.transient(parent_dialog)
        result_dialog.grab_set()

        # Center dialog
        result_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 150
        result_dialog.geometry(f"+{x}+{y}")

        # Title
        total_new = sum(len(v) for v in new_voices.values())
        ctk.CTkLabel(
            result_dialog,
            text=f"{total_new} New Voice{'s' if total_new > 1 else ''} Available!",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # Scrollable frame for results
        scroll = ctk.CTkScrollableFrame(result_dialog, height=180)
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        # List new voices by language
        for lang_name in sorted(new_voices.keys()):
            voices_list = new_voices[lang_name]

            # Language header
            ctk.CTkLabel(
                scroll,
                text=f"{lang_name}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).pack(anchor="w", pady=(10, 5))

            # Voice list
            for voice_name in voices_list:
                ctk.CTkLabel(
                    scroll,
                    text=f"  • {voice_name}",
                    font=ctk.CTkFont(size=11),
                    anchor="w"
                ).pack(anchor="w", pady=2)

        # Close button
        ctk.CTkButton(
            result_dialog,
            text="Close",
            width=100,
            command=result_dialog.destroy
        ).pack(pady=15)

    def show_language_not_available_dialog(self, lang_code: str):
        """Show dialog when a language is detected but no voices are downloaded"""
        # Language name mapping
        lang_names = {
            'en': 'English', 'es': 'Spanish', 'it': 'Italian', 'fr': 'French',
            'de': 'German', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'nl': 'Dutch', 'pl': 'Polish',
            'uk': 'Ukrainian', 'vi': 'Vietnamese', 'ar': 'Arabic', 'tr': 'Turkish',
            'hi': 'Hindi', 'cs': 'Czech', 'da': 'Danish', 'fi': 'Finnish',
            'el': 'Greek', 'hu': 'Hungarian', 'is': 'Icelandic', 'nb': 'Norwegian',
            'ro': 'Romanian', 'sk': 'Slovak', 'sv': 'Swedish', 'sw': 'Swahili',
            'ka': 'Georgian'
        }

        lang_name = lang_names.get(lang_code, lang_code.upper())

        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"{lang_name} Language Selected")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 100
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            dialog,
            text=f"{lang_name} Language Selected",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))

        # Message
        ctk.CTkLabel(
            dialog,
            text=f"No {lang_name} voices are installed.\n\nWould you like to download {lang_name} voices?",
            font=ctk.CTkFont(size=12),
            justify="center"
        ).pack(pady=10)

        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        def on_download():
            dialog.destroy()
            self.download_voices_for_language(lang_code, lang_name)

        def on_dismiss():
            dialog.destroy()

        ctk.CTkButton(
            btn_frame,
            text="Download Voices",
            width=140,
            command=on_download
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Dismiss",
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=on_dismiss
        ).pack(side="left", padx=10)

    def download_voices_for_language(self, lang_code: str, lang_name: str):
        """Download voices for a specific language"""
        if not isinstance(self.current_engine, PiperTTSEngine):
            return

        # Find voices for this language in predefined list
        voices_to_download = []
        for category, voices in self.current_engine.PIPER_VOICES.items():
            for voice_id, info in voices.items():
                voice_lang = self.current_engine.get_voice_language(voice_id)
                if voice_lang == lang_code and not self.current_engine.is_voice_downloaded(voice_id):
                    voices_to_download.append((voice_id, info))

        if voices_to_download:
            # Has predefined voices - show download dialog
            self.show_language_download_dialog(lang_code, lang_name, voices_to_download)
        else:
            # No predefined voices - show manual download instructions
            self.show_manual_download_instructions(lang_code, lang_name)

    def show_language_download_dialog(self, lang_code: str, lang_name: str, voices: list):
        """Show dialog to download voices for a specific language"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Download {lang_name} Voices")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            dialog,
            text=f"Download {lang_name} Voices",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        ctk.CTkLabel(
            dialog,
            text=f"Found {len(voices)} {lang_name} voice(s) available for download:",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 10))

        # Scrollable frame for voices
        scroll_frame = ctk.CTkScrollableFrame(dialog, height=180)
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Track download buttons and progress bars
        download_widgets = {}

        for voice_id, info in voices:
            voice_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            voice_frame.pack(fill="x", pady=5)

            # Voice name
            ctk.CTkLabel(
                voice_frame,
                text=info['name'],
                font=ctk.CTkFont(size=11),
                anchor="w",
                width=200
            ).pack(side="left", padx=5)

            # Progress bar (hidden initially)
            progress_bar = ctk.CTkProgressBar(voice_frame, width=120, height=12)
            progress_bar.set(0)
            progress_bar.pack(side="left", padx=5)
            progress_bar.pack_forget()  # Hide initially

            # Status label
            status_label = ctk.CTkLabel(
                voice_frame,
                text="",
                font=ctk.CTkFont(size=9),
                width=80
            )
            status_label.pack(side="left", padx=2)
            status_label.pack_forget()  # Hide initially

            # Download button
            btn = ctk.CTkButton(
                voice_frame,
                text="Download",
                width=80,
                height=24,
                font=ctk.CTkFont(size=10),
                command=lambda vid=voice_id: self.download_single_voice_with_progress(vid, download_widgets)
            )
            btn.pack(side="right", padx=5)

            download_widgets[voice_id] = {
                'button': btn,
                'progress': progress_bar,
                'status': status_label
            }

        # Download all button
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)

        def download_all():
            for voice_id, info in voices:
                if not self.current_engine.is_voice_downloaded(voice_id):
                    self.download_single_voice_with_progress(voice_id, download_widgets)

        ctk.CTkButton(
            btn_frame,
            text=f"Download All ({len(voices)})",
            width=140,
            command=download_all
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Close",
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=dialog.destroy
        ).pack(side="left", padx=10)

    def download_single_voice_from_dialog(self, voice_id: str, buttons_dict: dict):
        """Download a single voice and update button state"""
        if voice_id in buttons_dict:
            buttons_dict[voice_id].configure(text="...", state="disabled")

        def do_download():
            try:
                def progress_callback(progress, status):
                    pass  # Silent download

                self.current_engine.download_voice(voice_id, progress_callback)

                # Update button on completion
                if voice_id in buttons_dict:
                    self.after(0, lambda: buttons_dict[voice_id].configure(
                        text="Done",
                        fg_color="green",
                        state="disabled"
                    ))

                # Refresh voice dropdown
                self.after(100, self.update_voice_dropdown)

            except Exception as e:
                if voice_id in buttons_dict:
                    self.after(0, lambda: buttons_dict[voice_id].configure(
                        text="Failed",
                        fg_color="red",
                        state="disabled"
                    ))

        threading.Thread(target=do_download, daemon=True).start()

    def download_single_voice_with_progress(self, voice_id: str, widgets_dict: dict):
        """Download a single voice with progress bar updates"""
        if voice_id not in widgets_dict:
            return

        widgets = widgets_dict[voice_id]
        btn = widgets['button']
        progress_bar = widgets['progress']
        status_label = widgets['status']

        # Hide button, show progress bar and status
        btn.pack_forget()
        progress_bar.pack(side="right", padx=5)
        status_label.pack(side="right", padx=2)
        progress_bar.set(0)
        status_label.configure(text="Starting...")

        def do_download():
            try:
                def progress_callback(progress, status):
                    # Update progress bar and status on main thread
                    def update_ui():
                        progress_bar.set(progress / 100)
                        # Shorten status text for display
                        if "Downloading" in status:
                            status_label.configure(text=f"{int(progress)}%")
                        elif "Complete" in status or "done" in status.lower():
                            status_label.configure(text="Done!", text_color="green")
                        else:
                            status_label.configure(text=status[:15])
                    self.after(0, update_ui)

                self.current_engine.download_voice(voice_id, progress_callback)

                # Update UI on completion
                def on_complete():
                    progress_bar.set(1)
                    status_label.configure(text="✓ Done", text_color="green")
                    # Refresh voice dropdown
                    self.update_voice_dropdown()

                self.after(0, on_complete)

            except Exception as e:
                def on_error():
                    progress_bar.pack_forget()
                    status_label.configure(text="Failed", text_color="red")
                    btn.pack(side="right", padx=5)
                    btn.configure(text="Retry", state="normal")
                self.after(0, on_error)

        threading.Thread(target=do_download, daemon=True).start()

    def show_manual_download_instructions(self, lang_code: str, lang_name: str):
        """Show instructions for manually downloading voices"""
        # Map language codes to HuggingFace folder names
        lang_folder_map = {
            'it': 'it/it_IT', 'fr': 'fr/fr_FR', 'es': 'es/es_ES', 'de': 'de/de_DE',
            'pt': 'pt/pt_BR', 'ru': 'ru/ru_RU', 'zh': 'zh/zh_CN', 'ja': 'ja/ja_JP',
            'ko': 'ko/ko_KR', 'nl': 'nl/nl_NL', 'pl': 'pl/pl_PL', 'uk': 'uk/uk_UA',
            'vi': 'vi/vi_VN', 'ar': 'ar/ar_JO', 'tr': 'tr/tr_TR', 'hi': 'hi/hi_IN',
            'cs': 'cs/cs_CZ', 'da': 'da/da_DK', 'fi': 'fi/fi_FI', 'el': 'el/el_GR',
            'hu': 'hu/hu_HU', 'is': 'is/is_IS', 'nb': 'nb/nb_NO', 'ro': 'ro/ro_RO',
            'sk': 'sk/sk_SK', 'sv': 'sv/sv_SE', 'sw': 'sw/sw_CD', 'ka': 'ka/ka_GE'
        }

        folder = lang_folder_map.get(lang_code, f"{lang_code}/{lang_code}_XX")
        url = f"https://huggingface.co/rhasspy/piper-voices/tree/main/{folder}"

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Download {lang_name} Voices")
        dialog.geometry("500x280")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 140
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            dialog,
            text=f"Download {lang_name} Voices",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # Instructions
        instructions = f"""No predefined {lang_name} voices found in the app.

You can manually download {lang_name} voices from HuggingFace:

1. Visit the link below
2. Download both .onnx and .onnx.json files
3. Place them in the models/piper/ folder
4. Restart the app - voices will appear automatically!"""

        ctk.CTkLabel(
            dialog,
            text=instructions,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w"
        ).pack(padx=20, pady=10, anchor="w")

        # URL display
        url_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=5)

        url_entry = ctk.CTkEntry(url_frame, width=350)
        url_entry.insert(0, url)
        url_entry.configure(state="readonly")
        url_entry.pack(side="left", padx=5)

        def copy_url():
            self.clipboard_clear()
            self.clipboard_append(url)
            copy_btn.configure(text="Copied!")
            self.after(2000, lambda: copy_btn.configure(text="Copy"))

        copy_btn = ctk.CTkButton(
            url_frame,
            text="Copy",
            width=60,
            command=copy_url
        )
        copy_btn.pack(side="left", padx=5)

        # Close button
        ctk.CTkButton(
            dialog,
            text="Close",
            width=100,
            command=dialog.destroy
        ).pack(pady=15)

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
