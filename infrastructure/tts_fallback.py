# -*- coding: utf-8 -*-
"""
Controlador de TTS con Fallbacks Múltiples
Soporta múltiples motores TTS con fallback automático.
"""
import os
import subprocess
import tempfile
from typing import Optional
from infrastructure.system_compat import system_compat

class TTSFallbackController:
    """Controlador TTS con múltiples motores y fallback automático."""
    
    def __init__(self):
        self.current_engine = None
        self.engines = {}
        self._initialize_engines()
        self._select_best_engine()
    
    def _initialize_engines(self):
        """Inicializa todos los motores TTS disponibles."""
        
        # Motor 1: pyttsx3 (prioridad alta)
        if 'pyttsx3' in system_compat.available_tts_engines:
            try:
                self.engines['pyttsx3'] = Pyttsx3Engine()
            except Exception as e:
                print(f"Error inicializando pyttsx3: {e}")
        
        # Motor 2: SAPI (Windows only)
        if 'sapi' in system_compat.available_tts_engines:
            try:
                self.engines['sapi'] = SAPIEngine()
            except Exception as e:
                print(f"Error inicializando SAPI: {e}")
        
        # Motor 3: say (macOS only)
        if 'say' in system_compat.available_tts_engines:
            try:
                self.engines['say'] = SayEngine()
            except Exception as e:
                print(f"Error inicializando say: {e}")
        
        # Motor 4: espeak (Linux)
        if 'espeak' in system_compat.available_tts_engines:
            try:
                self.engines['espeak'] = EspeakEngine()
            except Exception as e:
                print(f"Error inicializando espeak: {e}")
        
        # Motor 5: pico2wave (Linux)
        if system_compat.platform_info['is_linux']:
            try:
                subprocess.run(['pico2wave', '--version'], 
                             capture_output=True, check=True)
                self.engines['pico2wave'] = Pico2WaveEngine()
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Motor Premium: gTTS (Google Text-to-Speech)
        try:
            import gtts
            self.engines['gtts'] = GTTSEngine()
        except ImportError:
            pass
        
        # Motor Fallback Definitivo: Alerta Táctica
        try:
            self.engines['tactic_alert'] = TacticAlertEngine()
        except Exception as e:
            print(f"Error inicializando alerta táctica: {e}")
    
    def _select_best_engine(self):
        """Selecciona el mejor motor disponible."""
        # Prioridad: gTTS (Premium) -> pyttsx3 -> sapi -> say -> espeak -> pico2wave -> tactic_alert
        priority = ['gtts', 'pyttsx3', 'sapi', 'say', 'espeak', 'pico2wave', 'tactic_alert']
        
        for engine_name in priority:
            if engine_name in self.engines:
                self.current_engine = self.engines[engine_name]
                print(f"Motor TTS seleccionado: {engine_name}")
                return
        
        print("Advertencia: No se encontraron motores TTS disponibles")
    
    def text_to_speech(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        """Convierte texto a audio usando el motor actual con fallback."""
        if not texto or texto.strip() == "":
            raise ValueError("El texto no puede estar vacío")
        
        if not self.current_engine:
            raise RuntimeError("No hay motor TTS disponible")
        
        # Intentar con el motor actual
        try:
            return self.current_engine.synthesize(texto, ruta_salida, rate)
        except Exception as e:
            print(f"Error con motor {type(self.current_engine).__name__}: {e}")
            # Intentar fallback a otro motor
            return self._try_fallback(texto, ruta_salida, rate)
    
    def _try_fallback(self, texto: str, ruta_salida: str, rate: int) -> str:
        """Intenta sintetizar con otro motor."""
        for engine_name, engine in self.engines.items():
            if engine != self.current_engine:
                try:
                    print(f"Intentando fallback a {engine_name}...")
                    resultado = engine.synthesize(texto, ruta_salida, rate)
                    self.current_engine = engine
                    print(f"Fallback exitoso a {engine_name}")
                    return resultado
                except Exception as e:
                    print(f"Fallback a {engine_name} falló: {e}")
        
        raise RuntimeError("Todos los motores TTS fallaron")
    
    def set_rate(self, rate: int):
        """Establece la velocidad de voz."""
        if self.current_engine and hasattr(self.current_engine, 'set_rate'):
            try:
                self.current_engine.set_rate(rate)
            except Exception as e:
                print(f"Error al establecer velocidad: {e}")
    
    def get_available_voices(self) -> list:
        """Retorna las voces disponibles del motor actual."""
        if self.current_engine and hasattr(self.current_engine, 'get_voices'):
            try:
                return self.current_engine.get_voices()
            except:
                pass
        return []
    
    def set_voice(self, voice_id: str):
        """Establece la voz."""
        if self.current_engine and hasattr(self.current_engine, 'set_voice'):
            try:
                self.current_engine.set_voice(voice_id)
            except Exception as e:
                print(f"Error al establecer voz: {e}")
    
    def close(self):
        """Cierra todos los motores."""
        for engine in self.engines.values():
            try:
                if hasattr(engine, 'close'):
                    engine.close()
            except Exception as e:
                print(f"Error al cerrar motor: {e}")


# Implementaciones de Motores Específicos

class Pyttsx3Engine:
    """Motor TTS usando pyttsx3."""
    
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()
        self.rate = 160
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        self.engine.setProperty('rate', rate)
        self.engine.save_to_file(texto, ruta_salida)
        self.engine.runAndWait()
        return ruta_salida
    
    def set_rate(self, rate: int):
        self.rate = rate
    
    def get_voices(self) -> list:
        return [voice.id for voice in self.engine.getProperty('voices')]
    
    def set_voice(self, voice_id: str):
        self.engine.setProperty('voice', voice_id)
    
    def close(self):
        self.engine.stop()


class SAPIEngine:
    """Motor TTS usando SAPI (Windows)."""
    
    def __init__(self):
        # No guardamos el objeto COM en self porque no se puede compartir entre hilos
        pass
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        import win32com.client
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except:
            pass
        stream = None
        try:
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Format.Type = 22  # PCM 16kHz 16bit Mono
            stream.Open(ruta_salida, 3)  # SSFMCreateForWrite
            
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            voice.AudioOutputStream = stream
            voice.Speak(texto)
        finally:
            if stream:
                try:
                    stream.Close()
                except:
                    pass
        
        return ruta_salida
    
    def get_voices(self) -> list:
        import win32com.client
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except:
            pass
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()
            return [voice.GetDescription() for voice in voices]
        except:
            return []
    
    def set_voice(self, voice_id: str):
        # SAPI es complejo para establecer voces de forma persistente sin mantener el objeto
        # En una arquitectura multi-hilo, lo ideal es pasar la voz al momento de sintetizar.
        pass


class SayEngine:
    """Motor TTS usando say (macOS)."""
    
    def __init__(self):
        self.rate = 160
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        # say puede guardar a archivo usando -o
        cmd = ['say', '-o', ruta_salida, texto]
        subprocess.run(cmd, check=True)
        return ruta_salida
    
    def set_rate(self, rate: int):
        self.rate = rate
    
    def get_voices(self) -> list:
        cmd = ['say', '-v', '?']
        result = subprocess.run(cmd, capture_output=True, text=True)
        voices = []
        for line in result.stdout.split('\n'):
            if line.strip():
                voices.append(line.strip())
        return voices
    
    def set_voice(self, voice_id: str):
        # say usa -v para seleccionar voz
        pass


class EspeakEngine:
    """Motor TTS usando espeak (Linux)."""
    
    def __init__(self):
        self.rate = 160
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        # espeak puede guardar a WAV
        cmd = ['espeak', '-w', ruta_salida, texto]
        subprocess.run(cmd, check=True)
        return ruta_salida
    
    def set_rate(self, rate: int):
        self.rate = rate
    
    def get_voices(self) -> list:
        cmd = ['espeak', '--voices']
        result = subprocess.run(cmd, capture_output=True, text=True)
        voices = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                voices.append(line.strip())
        return voices


class Pico2WaveEngine:
    """Motor TTS usando pico2wave (Linux)."""
    
    def __init__(self):
        self.rate = 160
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        # pico2wave genera WAV
        cmd = ['pico2wave', '-w', ruta_salida, texto]
        subprocess.run(cmd, check=True)
        return ruta_salida
    
    def set_rate(self, rate: int):
        self.rate = rate


class TacticAlertEngine:
    """Motor de fallback táctico que genera tonos de alerta y secuencias cuando no hay TTS."""
    
    def __init__(self):
        pass
        
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        import wave
        import math
        import struct
        
        # Frecuencia de muestreo
        sample_rate = 16000
        # Duración: generamos una señal de alerta de 5 segundos
        duration = 5.0
        num_samples = int(duration * sample_rate)
        
        # Abrir archivo wave
        with wave.open(ruta_salida, 'wb') as wav_file:
            # 1 canal (mono), 2 bytes por muestra (16 bits), sample_rate
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            # Generar secuencia de bip-bip de alerta de emergencia
            samples = []
            for i in range(num_samples):
                t = i / sample_rate
                # Sirena que alterna cada 0.25 segundos
                freq = 880 if int(t * 4) % 2 == 0 else 660
                
                # Atenuar al final de cada bip para suavizar el sonido
                bip_t = t % 0.25
                fade = 1.0
                if bip_t > 0.20:
                    fade = max(0.0, 1.0 - (bip_t - 0.20) / 0.05)
                elif bip_t < 0.01:
                    fade = bip_t / 0.01
                
                # Onda senoidal
                value = int(32767 * 0.5 * fade * math.sin(2 * math.pi * freq * t))
                samples.append(struct.pack('<h', value))
                
            wav_file.writeframes(b''.join(samples))
            
        return ruta_salida

    def get_voices(self) -> list:
        return ["Tactic Alert Signal (Fallback)"]
        
    def set_voice(self, voice_id: str):
        pass


class GTTSEngine:
    """Motor TTS Premium usando Google Text-to-Speech (gTTS)."""
    
    def __init__(self):
        self.language = 'es'
        self.tld = 'com' # Accent (com=Mexico/Spain, com.mx=Mexico)
    
    def synthesize(self, texto: str, ruta_salida: str, rate: int = 160) -> str:
        from gtts import gTTS
        import os
        import tempfile
        import shutil
        
        is_slow = rate < 120
        temp_mp3 = tempfile.mktemp(suffix=".mp3", prefix="gtts_raw_")
        tts = gTTS(text=texto, lang=self.language, tld=self.tld, slow=is_slow)
        tts.save(temp_mp3)
        
        # Transcodificar a WAV puro para evitar "Unknown WAVE format" y dependencias FFmpeg
        transcoded = False
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            sound = pygame.mixer.Sound(temp_mp3)
            raw = sound.get_raw()
            
            import wave
            mixer_settings = pygame.mixer.get_init()
            freq = mixer_settings[0]
            channels = mixer_settings[2]
            
            with wave.open(ruta_salida, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)
                wf.setframerate(freq)
                wf.writeframes(raw)
            transcoded = True
        except Exception as e:
            print(f"Fallback transcodificación gTTS: {e}")
            
        if not transcoded:
            shutil.copy2(temp_mp3, ruta_salida)
            
        try:
            os.remove(temp_mp3)
        except:
            pass
            
        return ruta_salida

    def get_voices(self) -> list:
        return ["Google Español (Estándar)", "Google Español (México)", "Google Español (España)"]
        
    def set_voice(self, voice_id: str):
        if "México" in voice_id:
            self.tld = 'com.mx'
        elif "España" in voice_id:
            self.tld = 'es'
        else:
            self.tld = 'com'
