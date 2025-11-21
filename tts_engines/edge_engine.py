"""
Edge TTS Engine - Microsoft Edge Neural Voices (Online)
"""

import asyncio
from typing import Dict, Optional
from .base_engine import BaseTTSEngine


class EdgeTTSEngine(BaseTTSEngine):
    """Edge TTS engine using Microsoft Edge Neural Voices"""

    @property
    def name(self) -> str:
        return "Edge TTS (Online)"

    @property
    def is_online(self) -> bool:
        return True

    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """Get Edge TTS voices organized by category"""
        return {
            # English voices
            'English (US)': {
                'en-US-JennyNeural': 'Jenny - Female, Friendly',
                'en-US-GuyNeural': 'Guy - Male, Professional',
                'en-US-AriaNeural': 'Aria - Female, Natural',
                'en-US-DavisNeural': 'Davis - Male, Calm',
                'en-US-AmberNeural': 'Amber - Female, Warm',
                'en-US-AnaNeural': 'Ana - Female, Child',
                'en-US-AndrewNeural': 'Andrew - Male, Warm',
                'en-US-EmmaNeural': 'Emma - Female, Clear',
                'en-US-BrianNeural': 'Brian - Male, Casual',
                'en-US-ChristopherNeural': 'Christopher - Male, Authoritative',
                'en-US-EricNeural': 'Eric - Male, Friendly',
                'en-US-MichelleNeural': 'Michelle - Female, Professional',
                'en-US-RogerNeural': 'Roger - Male, Elderly',
                'en-US-SteffanNeural': 'Steffan - Male, News',
            },
            'English (UK)': {
                'en-GB-SoniaNeural': 'Sonia - Female, British',
                'en-GB-RyanNeural': 'Ryan - Male, British',
                'en-GB-LibbyNeural': 'Libby - Female, British Warm',
                'en-GB-MaisieNeural': 'Maisie - Female, Child',
                'en-GB-ThomasNeural': 'Thomas - Male, British Friendly',
            },
            'English (Australia)': {
                'en-AU-NatashaNeural': 'Natasha - Female, Australian',
                'en-AU-WilliamNeural': 'William - Male, Australian',
            },
            'English (India)': {
                'en-IN-NeerjaNeural': 'Neerja - Female, Indian',
                'en-IN-PrabhatNeural': 'Prabhat - Male, Indian',
            },
            'English (Other)': {
                'en-CA-ClaraNeural': 'Clara - Female, Canadian',
                'en-CA-LiamNeural': 'Liam - Male, Canadian',
                'en-IE-EmilyNeural': 'Emily - Female, Irish',
                'en-IE-ConnorNeural': 'Connor - Male, Irish',
                'en-NZ-MollyNeural': 'Molly - Female, New Zealand',
                'en-NZ-MitchellNeural': 'Mitchell - Male, New Zealand',
                'en-ZA-LeahNeural': 'Leah - Female, South African',
                'en-ZA-LukeNeural': 'Luke - Male, South African',
            },
            # French voices
            'French': {
                'fr-FR-DeniseNeural': 'Denise - Female, French',
                'fr-FR-HenriNeural': 'Henri - Male, French',
                'fr-FR-EloiseNeural': 'Eloise - Female, Child',
                'fr-CA-SylvieNeural': 'Sylvie - Female, Canadian French',
                'fr-CA-JeanNeural': 'Jean - Male, Canadian French',
                'fr-CA-AntoineNeural': 'Antoine - Male, Canadian French',
                'fr-BE-CharlineNeural': 'Charline - Female, Belgian French',
                'fr-BE-GerardNeural': 'Gerard - Male, Belgian French',
                'fr-CH-ArianeNeural': 'Ariane - Female, Swiss French',
                'fr-CH-FabriceNeural': 'Fabrice - Male, Swiss French',
            },
            # Spanish voices
            'Spanish': {
                'es-ES-ElviraNeural': 'Elvira - Female, Spanish',
                'es-ES-AlvaroNeural': 'Alvaro - Male, Spanish',
                'es-MX-DaliaNeural': 'Dalia - Female, Mexican',
                'es-MX-JorgeNeural': 'Jorge - Male, Mexican',
                'es-AR-ElenaNeural': 'Elena - Female, Argentine',
                'es-AR-TomasNeural': 'Tomas - Male, Argentine',
                'es-CO-SalomeNeural': 'Salome - Female, Colombian',
                'es-CO-GonzaloNeural': 'Gonzalo - Male, Colombian',
                'es-US-PalomaNeural': 'Paloma - Female, US Spanish',
                'es-US-AlonsoNeural': 'Alonso - Male, US Spanish',
            },
            # German voices
            'German': {
                'de-DE-KatjaNeural': 'Katja - Female, German',
                'de-DE-ConradNeural': 'Conrad - Male, German',
                'de-DE-AmalaNeural': 'Amala - Female, Warm',
                'de-DE-KillianNeural': 'Killian - Male, Friendly',
                'de-AT-IngridNeural': 'Ingrid - Female, Austrian',
                'de-AT-JonasNeural': 'Jonas - Male, Austrian',
                'de-CH-LeniNeural': 'Leni - Female, Swiss German',
                'de-CH-JanNeural': 'Jan - Male, Swiss German',
            },
            # Italian voices
            'Italian': {
                'it-IT-ElsaNeural': 'Elsa - Female, Italian',
                'it-IT-DiegoNeural': 'Diego - Male, Italian',
                'it-IT-IsabellaNeural': 'Isabella - Female, Warm',
                'it-IT-GiuseppeNeural': 'Giuseppe - Male, Friendly',
            },
            # Portuguese voices
            'Portuguese': {
                'pt-BR-FranciscaNeural': 'Francisca - Female, Brazilian',
                'pt-BR-AntonioNeural': 'Antonio - Male, Brazilian',
                'pt-BR-ThalitaNeural': 'Thalita - Female, Warm',
                'pt-PT-RaquelNeural': 'Raquel - Female, Portuguese',
                'pt-PT-DuarteNeural': 'Duarte - Male, Portuguese',
            },
            # Russian voices
            'Russian': {
                'ru-RU-SvetlanaNeural': 'Svetlana - Female, Russian',
                'ru-RU-DmitryNeural': 'Dmitry - Male, Russian',
                'ru-RU-DariyaNeural': 'Dariya - Female, Warm',
            },
            # Chinese voices
            'Chinese': {
                'zh-CN-XiaoxiaoNeural': 'Xiaoxiao - Female, Mandarin',
                'zh-CN-YunxiNeural': 'Yunxi - Male, Mandarin',
                'zh-CN-YunjianNeural': 'Yunjian - Male, Narrator',
                'zh-CN-XiaoyiNeural': 'Xiaoyi - Female, Friendly',
                'zh-TW-HsiaoChenNeural': 'HsiaoChen - Female, Taiwanese',
                'zh-TW-YunJheNeural': 'YunJhe - Male, Taiwanese',
                'zh-HK-HiuMaanNeural': 'HiuMaan - Female, Cantonese',
                'zh-HK-WanLungNeural': 'WanLung - Male, Cantonese',
            },
            # Japanese voices
            'Japanese': {
                'ja-JP-NanamiNeural': 'Nanami - Female, Japanese',
                'ja-JP-KeitaNeural': 'Keita - Male, Japanese',
                'ja-JP-AoiNeural': 'Aoi - Female, Child',
                'ja-JP-DaichiNeural': 'Daichi - Male, Friendly',
            },
            # Korean voices
            'Korean': {
                'ko-KR-SunHiNeural': 'SunHi - Female, Korean',
                'ko-KR-InJoonNeural': 'InJoon - Male, Korean',
                'ko-KR-BongJinNeural': 'BongJin - Male, Friendly',
                'ko-KR-GookMinNeural': 'GookMin - Male, Narrator',
            },
            # Arabic voices
            'Arabic': {
                'ar-SA-ZariyahNeural': 'Zariyah - Female, Saudi',
                'ar-SA-HamedNeural': 'Hamed - Male, Saudi',
                'ar-EG-SalmaNeural': 'Salma - Female, Egyptian',
                'ar-EG-ShakirNeural': 'Shakir - Male, Egyptian',
                'ar-AE-FatimaNeural': 'Fatima - Female, UAE',
                'ar-AE-HamdanNeural': 'Hamdan - Male, UAE',
            },
            # Hindi voices
            'Hindi': {
                'hi-IN-SwaraNeural': 'Swara - Female, Hindi',
                'hi-IN-MadhurNeural': 'Madhur - Male, Hindi',
            },
            # Dutch voices
            'Dutch': {
                'nl-NL-ColetteNeural': 'Colette - Female, Dutch',
                'nl-NL-MaartenNeural': 'Maarten - Male, Dutch',
                'nl-BE-DenaNeural': 'Dena - Female, Belgian Dutch',
                'nl-BE-ArnaudNeural': 'Arnaud - Male, Belgian Dutch',
            },
            # Polish voices
            'Polish': {
                'pl-PL-AgnieszkaNeural': 'Agnieszka - Female, Polish',
                'pl-PL-MarekNeural': 'Marek - Male, Polish',
                'pl-PL-ZofiaNeural': 'Zofia - Female, Warm',
            },
            # Turkish voices
            'Turkish': {
                'tr-TR-EmelNeural': 'Emel - Female, Turkish',
                'tr-TR-AhmetNeural': 'Ahmet - Male, Turkish',
            },
            # Vietnamese voices
            'Vietnamese': {
                'vi-VN-HoaiMyNeural': 'HoaiMy - Female, Vietnamese',
                'vi-VN-NamMinhNeural': 'NamMinh - Male, Vietnamese',
            },
            # Thai voices
            'Thai': {
                'th-TH-PremwadeeNeural': 'Premwadee - Female, Thai',
                'th-TH-NiwatNeural': 'Niwat - Male, Thai',
            },
            # Greek voices
            'Greek': {
                'el-GR-AthinaNeural': 'Athina - Female, Greek',
                'el-GR-NestorasNeural': 'Nestoras - Male, Greek',
            },
            # Czech voices
            'Czech': {
                'cs-CZ-VlastaNeural': 'Vlasta - Female, Czech',
                'cs-CZ-AntoninNeural': 'Antonin - Male, Czech',
            },
            # Romanian voices
            'Romanian': {
                'ro-RO-AlinaNeural': 'Alina - Female, Romanian',
                'ro-RO-EmilNeural': 'Emil - Male, Romanian',
            },
            # Hungarian voices
            'Hungarian': {
                'hu-HU-NoemiNeural': 'Noemi - Female, Hungarian',
                'hu-HU-TamasNeural': 'Tamas - Male, Hungarian',
            },
            # Danish voices
            'Danish': {
                'da-DK-ChristelNeural': 'Christel - Female, Danish',
                'da-DK-JeppeNeural': 'Jeppe - Male, Danish',
            },
            # Finnish voices
            'Finnish': {
                'fi-FI-SelmaNeural': 'Selma - Female, Finnish',
                'fi-FI-HarriNeural': 'Harri - Male, Finnish',
            },
            # Norwegian voices
            'Norwegian': {
                'nb-NO-PernilleNeural': 'Pernille - Female, Norwegian',
                'nb-NO-FinnNeural': 'Finn - Male, Norwegian',
            },
            # Swedish voices
            'Swedish': {
                'sv-SE-SofieNeural': 'Sofie - Female, Swedish',
                'sv-SE-MattiasNeural': 'Mattias - Male, Swedish',
            },
            # Ukrainian voices
            'Ukrainian': {
                'uk-UA-PolinaNeural': 'Polina - Female, Ukrainian',
                'uk-UA-OstapNeural': 'Ostap - Male, Ukrainian',
            },
            # Hebrew voices
            'Hebrew': {
                'he-IL-HilaNeural': 'Hila - Female, Hebrew',
                'he-IL-AvriNeural': 'Avri - Male, Hebrew',
            },
            # Indonesian voices
            'Indonesian': {
                'id-ID-GadisNeural': 'Gadis - Female, Indonesian',
                'id-ID-ArdiNeural': 'Ardi - Male, Indonesian',
            },
            # Malay voices
            'Malay': {
                'ms-MY-YasminNeural': 'Yasmin - Female, Malay',
                'ms-MY-OsmanNeural': 'Osman - Male, Malay',
            },
            # Filipino voices
            'Filipino': {
                'fil-PH-BlessicaNeural': 'Blessica - Female, Filipino',
                'fil-PH-AngeloNeural': 'Angelo - Male, Filipino',
            },
            # Slovak voices
            'Slovak': {
                'sk-SK-ViktoriaNeural': 'Viktoria - Female, Slovak',
                'sk-SK-LukasNeural': 'Lukas - Male, Slovak',
            },
            # Slovenian voices
            'Slovenian': {
                'sl-SI-PetraNeural': 'Petra - Female, Slovenian',
                'sl-SI-RokNeural': 'Rok - Male, Slovenian',
            },
            # Croatian voices
            'Croatian': {
                'hr-HR-GabrijelaNeural': 'Gabrijela - Female, Croatian',
                'hr-HR-SreckoNeural': 'Srecko - Male, Croatian',
            },
            # Bulgarian voices
            'Bulgarian': {
                'bg-BG-KalinaNeural': 'Kalina - Female, Bulgarian',
                'bg-BG-BorislavNeural': 'Borislav - Male, Bulgarian',
            },
            # Serbian voices
            'Serbian': {
                'sr-RS-SophieNeural': 'Sophie - Female, Serbian',
                'sr-RS-NicholasNeural': 'Nicholas - Male, Serbian',
            },
            # Catalan voices
            'Catalan': {
                'ca-ES-JoanaNeural': 'Joana - Female, Catalan',
                'ca-ES-EnricNeural': 'Enric - Male, Catalan',
            },
            # Welsh voices
            'Welsh': {
                'cy-GB-NiaNeural': 'Nia - Female, Welsh',
                'cy-GB-AledNeural': 'Aled - Male, Welsh',
            },
            # Irish voices
            'Irish': {
                'ga-IE-OrlaNeural': 'Orla - Female, Irish',
                'ga-IE-ColmNeural': 'Colm - Male, Irish',
            },
            # Icelandic voices
            'Icelandic': {
                'is-IS-GudrunNeural': 'Gudrun - Female, Icelandic',
                'is-IS-GunnarNeural': 'Gunnar - Male, Icelandic',
            },
            # Latvian voices
            'Latvian': {
                'lv-LV-EveritaNeural': 'Everita - Female, Latvian',
                'lv-LV-NilsNeural': 'Nils - Male, Latvian',
            },
            # Lithuanian voices
            'Lithuanian': {
                'lt-LT-OnaNeural': 'Ona - Female, Lithuanian',
                'lt-LT-LeonasNeural': 'Leonas - Male, Lithuanian',
            },
            # Estonian voices
            'Estonian': {
                'et-EE-AnuNeural': 'Anu - Female, Estonian',
                'et-EE-KertNeural': 'Kert - Male, Estonian',
            },
            # Georgian voices
            'Georgian': {
                'ka-GE-EkaNeural': 'Eka - Female, Georgian',
                'ka-GE-GiorgiNeural': 'Giorgi - Male, Georgian',
            },
            # Kazakh voices
            'Kazakh': {
                'kk-KZ-AigulNeural': 'Aigul - Female, Kazakh',
                'kk-KZ-DauletNeural': 'Daulet - Male, Kazakh',
            },
            # Nepali voices
            'Nepali': {
                'ne-NP-HemkalaNeural': 'Hemkala - Female, Nepali',
                'ne-NP-SagarNeural': 'Sagar - Male, Nepali',
            },
            # Bengali voices
            'Bengali': {
                'bn-BD-NabanitaNeural': 'Nabanita - Female, Bengali',
                'bn-BD-PradeepNeural': 'Pradeep - Male, Bengali',
                'bn-IN-TanishaaNeural': 'Tanishaa - Female, Bengali (India)',
                'bn-IN-BashkarNeural': 'Bashkar - Male, Bengali (India)',
            },
            # Tamil voices
            'Tamil': {
                'ta-IN-PallaviNeural': 'Pallavi - Female, Tamil',
                'ta-IN-ValluvarNeural': 'Valluvar - Male, Tamil',
            },
            # Telugu voices
            'Telugu': {
                'te-IN-ShrutiNeural': 'Shruti - Female, Telugu',
                'te-IN-MohanNeural': 'Mohan - Male, Telugu',
            },
            # Swahili voices
            'Swahili': {
                'sw-KE-ZuriNeural': 'Zuri - Female, Swahili',
                'sw-KE-RafikiNeural': 'Rafiki - Male, Swahili',
            },
            # Afrikaans voices
            'Afrikaans': {
                'af-ZA-AdriNeural': 'Adri - Female, Afrikaans',
                'af-ZA-WillemNeural': 'Willem - Male, Afrikaans',
            },
        }

    def generate(
        self,
        text: str,
        voice: str,
        output_path: str,
        speed: float = 1.0,
        pitch: int = 0,
        volume: int = 0,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Generate speech using Edge TTS"""
        try:
            import edge_tts

            # Convert parameters to Edge TTS format
            rate_percent = int((speed - 1.0) * 100)
            rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
            pitch_str = f"+{pitch}Hz" if pitch >= 0 else f"{pitch}Hz"
            volume_str = f"+{volume}%" if volume >= 0 else f"{volume}%"

            if progress_callback:
                progress_callback(0.2, "Connecting to Edge TTS...")

            async def run_edge_tts():
                communicate = edge_tts.Communicate(
                    text,
                    voice,
                    rate=rate,
                    pitch=pitch_str,
                    volume=volume_str
                )
                await communicate.save(output_path)

            if progress_callback:
                progress_callback(0.5, "Generating speech...")

            asyncio.run(run_edge_tts())

            if progress_callback:
                progress_callback(1.0, "Complete!")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise

    def is_available(self) -> bool:
        """Check if edge-tts is installed"""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def get_output_extension(self) -> str:
        return ".mp3"
