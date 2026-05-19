# -*- coding: utf-8 -*-
"""
Procesador de Audio con Fallbacks Múltiples
Soporta múltiples librerías de procesamiento de audio con fallback automático.
"""
import os
from typing import Optional
from infrastructure.system_compat import system_compat

class AudioProcessingFallback:
    """Procesador de audio con múltiples librerías y fallback automático."""
    
    def __init__(self):
        self.current_library = None
        self.libraries = {}
        self._initialize_libraries()
        self._select_best_library()
    
    def _initialize_libraries(self):
        """Inicializa todas las librerías de procesamiento disponibles."""
        
        # Librería 1: pydub (prioridad alta)
        if 'pydub' in system_compat.available_audio_processing:
            try:
                self.libraries['pydub'] = PydubProcessor()
            except Exception as e:
                print(f"Error inicializando pydub: {e}")
        
        # Librería 2: librosa
        if 'librosa' in system_compat.available_audio_processing:
            try:
                self.libraries['librosa'] = LibrosaProcessor()
            except Exception as e:
                print(f"Error inicializando librosa: {e}")
        
        # Librería 3: soundfile
        if 'soundfile' in system_compat.available_audio_processing:
            try:
                self.libraries['soundfile'] = SoundfileProcessor()
            except Exception as e:
                print(f"Error inicializando soundfile: {e}")
        
        # Librería 4: wave (built-in, fallback básico)
        if 'wave' in system_compat.available_audio_processing:
            try:
                self.libraries['wave'] = WaveProcessor()
            except Exception as e:
                print(f"Error inicializando wave: {e}")
    
    def _select_best_library(self):
        """Selecciona la mejor librería disponible."""
        priority = ['pydub', 'librosa', 'soundfile', 'wave']
        
        for library_name in priority:
            if library_name in self.libraries:
                self.current_library = self.libraries[library_name]
                print(f"Librería de procesamiento seleccionada: {library_name}")
                return
        
        print("Advertencia: No se encontraron librerías de procesamiento de audio")
    
    def load_audio(self, ruta_archivo: str):
        """Carga audio usando la librería actual con fallback."""
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encuentra el archivo: {ruta_archivo}")
        
        if not self.current_library:
            raise RuntimeError("No hay librería de procesamiento disponible")
        
        try:
            return self.current_library.load(ruta_archivo)
        except Exception as e:
            print(f"Error con librería {type(self.current_library).__name__}: {e}")
            return self._try_fallback_load(ruta_archivo)
    
    def _try_fallback_load(self, ruta_archivo: str):
        """Intenta cargar con otra librería."""
        for library_name, library in self.libraries.items():
            if library != self.current_library:
                try:
                    print(f"Intentando fallback a {library_name}...")
                    resultado = library.load(ruta_archivo)
                    self.current_library = library
                    print(f"Fallback exitoso a {library_name}")
                    return resultado
                except Exception as e:
                    print(f"Fallback a {library_name} falló: {e}")
        
        raise RuntimeError("Todas las librerías de procesamiento fallaron")
    
    def save_audio(self, audio_data, ruta_salida: str, formato: str = 'wav'):
        """Guarda audio usando la librería actual con fallback."""
        if not self.current_library:
            raise RuntimeError("No hay librería de procesamiento disponible")
        
        try:
            return self.current_library.save(audio_data, ruta_salida, formato)
        except Exception as e:
            print(f"Error con librería {type(self.current_library).__name__}: {e}")
            return self._try_fallback_save(audio_data, ruta_salida, formato)
    
    def _try_fallback_save(self, audio_data, ruta_salida: str, formato: str):
        """Intenta guardar con otra librería."""
        for library_name, library in self.libraries.items():
            if library != self.current_library:
                try:
                    print(f"Intentando fallback a {library_name}...")
                    resultado = library.save(audio_data, ruta_salida, formato)
                    self.current_library = library
                    print(f"Fallback exitoso a {library_name}")
                    return resultado
                except Exception as e:
                    print(f"Fallback a {library_name} falló: {e}")
        
        raise RuntimeError("Todas las librerías de procesamiento fallaron")
    
    def mix_audio(self, audio1, audio2, volume_db: int = -18):
        """Mezcla dos pistas de audio."""
        if not self.current_library:
            raise RuntimeError("No hay librería de procesamiento disponible")
        
        try:
            return self.current_library.mix(audio1, audio2, volume_db)
        except Exception as e:
            print(f"Error mezclando audio: {e}")
            # Intentar mezcla básica
            return self._basic_mix(audio1, audio2, volume_db)
    
    def _basic_mix(self, audio1, audio2, volume_db: int):
        """Mezcla básica de fallback."""
        # Implementación simplificada usando la librería actual
        try:
            if hasattr(self.current_library, 'mix'):
                return self.current_library.mix(audio1, audio2, volume_db)
        except:
            pass
        return audio1  # Fallback: retornar solo audio1
    
    def get_duration(self, audio_data) -> float:
        """Retorna la duración del audio en segundos."""
        if self.current_library and hasattr(self.current_library, 'get_duration'):
            try:
                return self.current_library.get_duration(audio_data)
            except:
                pass
        return 0.0
    
    def close(self):
        """Cierra todas las librerías."""
        for library in self.libraries.values():
            try:
                if hasattr(library, 'close'):
                    library.close()
            except Exception as e:
                print(f"Error al cerrar librería: {e}")


# Implementaciones de Procesadores Específicos

class PydubProcessor:
    """Procesador usando pydub."""
    
    def __init__(self):
        from pydub import AudioSegment
        self.AudioSegment = AudioSegment
    
    def load(self, ruta_archivo: str):
        return self.AudioSegment.from_file(ruta_archivo)
    
    def save(self, audio_data, ruta_salida: str, formato: str = 'wav'):
        audio_data.export(ruta_salida, format=formato)
        return ruta_salida
    
    def mix(self, audio1, audio2, volume_db: int = -18):
        audio2_attenuated = audio2 - volume_db
        return audio1.overlay(audio2_attenuated)
    
    def get_duration(self, audio_data) -> float:
        return len(audio_data) / 1000.0


class LibrosaProcessor:
    """Procesador usando librosa."""
    
    def __init__(self):
        import librosa
        import soundfile as sf
        self.librosa = librosa
        self.sf = sf
    
    def load(self, ruta_archivo: str):
        y, sr = self.librosa.load(ruta_archivo, sr=None)
        return {'audio': y, 'sample_rate': sr}
    
    def save(self, audio_data, ruta_salida: str, formato: str = 'wav'):
        self.sf.write(ruta_salida, audio_data['audio'], audio_data['sample_rate'])
        return ruta_salida
    
    def mix(self, audio1, audio2, volume_db: int = -18):
        # Implementación básica de mezcla con librosa
        import numpy as np
        y1, sr1 = audio1['audio'], audio1['sample_rate']
        y2, sr2 = audio2['audio'], audio2['sample_rate']
        
        # Alinear sample rates
        if sr1 != sr2:
            y2 = self.librosa.resample(y2, orig_sr=sr2, target_sr=sr1)
        
        # Ajustar longitud
        min_len = min(len(y1), len(y2))
        y1 = y1[:min_len]
        y2 = y2[:min_len]
        
        # Mezclar con atenuación
        volume_factor = 10 ** (volume_db / 20)
        mixed = y1 + (y2 * volume_factor)
        
        return {'audio': mixed, 'sample_rate': sr1}
    
    def get_duration(self, audio_data) -> float:
        return len(audio_data['audio']) / audio_data['sample_rate']


class SoundfileProcessor:
    """Procesador usando soundfile."""
    
    def __init__(self):
        import soundfile as sf
        self.sf = sf
    
    def load(self, ruta_archivo: str):
        data, samplerate = self.sf.read(ruta_archivo)
        return {'audio': data, 'sample_rate': samplerate}
    
    def save(self, audio_data, ruta_salida: str, formato: str = 'wav'):
        self.sf.write(ruta_salida, audio_data['audio'], audio_data['sample_rate'])
        return ruta_salida
    
    def mix(self, audio1, audio2, volume_db: int = -18):
        # Implementación básica
        import numpy as np
        y1, sr1 = audio1['audio'], audio1['sample_rate']
        y2, sr2 = audio2['audio'], audio2['sample_rate']
        
        # Alinear
        if sr1 != sr2:
            from scipy import signal
            y2 = signal.resample(y2, int(len(y2) * sr1 / sr2))
        
        min_len = min(len(y1), len(y2))
        y1 = y1[:min_len]
        y2 = y2[:min_len]
        
        volume_factor = 10 ** (volume_db / 20)
        mixed = y1 + (y2 * volume_factor)
        
        return {'audio': mixed, 'sample_rate': sr1}
    
    def get_duration(self, audio_data) -> float:
        return len(audio_data['audio']) / audio_data['sample_rate']


class WaveProcessor:
    """Procesador usando wave (built-in, fallback básico)."""
    
    def __init__(self):
        import wave
        self.wave = wave
    
    def _convert_to_wav(self, ruta_archivo: str) -> str:
        """Convierte un archivo de audio no-WAV a WAV temporal usando pygame."""
        import tempfile
        ruta_wav = tempfile.mktemp(suffix=".wav", prefix="conv_")
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            sound = pygame.mixer.Sound(ruta_archivo)
            import array
            raw = sound.get_raw()
            with self.wave.open(ruta_wav, 'wb') as wf:
                # pygame Sound.get_raw() returns signed 16-bit samples
                mixer_settings = pygame.mixer.get_init()
                freq = mixer_settings[0]
                channels = mixer_settings[2]
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(freq)
                wf.writeframes(raw)
            return ruta_wav
        except Exception as e:
            print(f"Error convirtiendo a WAV con pygame: {e}")
            # Generate a short silent WAV as ultimate fallback
            return self._generate_silent_wav(ruta_wav)
    
    def _generate_silent_wav(self, ruta_wav: str) -> str:
        """Genera un archivo WAV silencioso de 5 segundos como fallback."""
        import struct
        sample_rate = 16000
        duration = 5
        num_samples = sample_rate * duration
        with self.wave.open(ruta_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f'<{num_samples}h', *([0] * num_samples)))
        return ruta_wav
    
    def load(self, ruta_archivo: str):
        ruta_temporal_convertida = None
        try:
            with self.wave.open(ruta_archivo, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                return {
                    'audio': frames,
                    'sample_rate': wf.getframerate(),
                    'channels': wf.getnchannels(),
                    'sampwidth': wf.getsampwidth()
                }
        except self.wave.Error:
            # Not a WAV file (e.g. MP3) — convert first
            print(f"Archivo no es WAV, convirtiendo: {ruta_archivo}")
            ruta_temporal_convertida = self._convert_to_wav(ruta_archivo)
            with self.wave.open(ruta_temporal_convertida, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                result = {
                    'audio': frames,
                    'sample_rate': wf.getframerate(),
                    'channels': wf.getnchannels(),
                    'sampwidth': wf.getsampwidth()
                }
            # Clean up temporary converted file
            try:
                import os
                os.remove(ruta_temporal_convertida)
            except:
                pass
            return result
    
    def save(self, audio_data, ruta_salida: str, formato: str = 'wav'):
        with self.wave.open(ruta_salida, 'wb') as wf:
            wf.setnchannels(audio_data.get('channels', 1))
            wf.setsampwidth(audio_data.get('sampwidth', 2))
            wf.setframerate(audio_data['sample_rate'])
            wf.writeframes(audio_data['audio'])
        return ruta_salida
    
    def mix(self, audio1, audio2, volume_db: int = -18):
        import struct
        import math
        
        try:
            # 1. Verificar anchos de muestra
            if audio1.get('sampwidth') != 2 or audio2.get('sampwidth') != 2:
                return audio1
            
            sr1 = audio1['sample_rate']
            sr2 = audio2['sample_rate']
            ch1 = audio1.get('channels', 1)
            ch2 = audio2.get('channels', 1)
            
            # 2. Desempaquetar audio1 (voz / señal principal)
            bytes1 = audio1['audio']
            num_samples1 = len(bytes1) // 2
            samples1 = list(struct.unpack(f'<{num_samples1}h', bytes1))
            
            # 3. Desempaquetar audio2 (cortina / fondo)
            bytes2 = audio2['audio']
            num_samples2 = len(bytes2) // 2
            samples2_raw = struct.unpack(f'<{num_samples2}h', bytes2)
            
            # 4. Proyectar y remuestrear audio2 en el espacio de audio1
            samples2 = []
            
            # Factor de conversión de sample rate
            rate_factor = sr2 / sr1
            
            # Factor de volumen (ducking)
            db_val = abs(volume_db)
            volume_factor = 10 ** (-db_val / 20)
            
            # Remuestreo simple por vecindad más cercana y mezcla de canales
            for i in range(num_samples1):
                # i representa el índice de la muestra en el canal de audio1
                frame_idx = i // ch1
                
                # Mapear al frame correspondiente de audio2
                frame_idx_2 = int(frame_idx * rate_factor)
                
                # Si nos pasamos del final del fondo, hacer loop
                frame_idx_2 = frame_idx_2 % (num_samples2 // ch2)
                
                # Determinar canal de audio2
                chan_idx = (i % ch1) % ch2
                
                # Obtener el valor de la muestra de fondo
                val2 = samples2_raw[frame_idx_2 * ch2 + chan_idx]
                samples2.append(val2)
                
            # 5. Mezclar ambas señales
            mixed_samples = []
            for s1, s2 in zip(samples1, samples2):
                val = int(s1 + s2 * volume_factor)
                # Evitar desbordamiento (clipping)
                val = max(-32768, min(32767, val))
                mixed_samples.append(val)
                
            # 6. Re-empaquetar
            mixed_bytes = struct.pack(f'<{len(mixed_samples)}h', *mixed_samples)
            
            return {
                'audio': mixed_bytes,
                'sample_rate': sr1,
                'channels': ch1,
                'sampwidth': 2
            }
        except Exception as e:
            print(f"Error en mezcla WaveProcessor: {e}")
            return audio1
    
    def get_duration(self, audio_data) -> float:
        # Estimación básica
        frames = len(audio_data['audio'])
        sample_rate = audio_data['sample_rate']
        sampwidth = audio_data.get('sampwidth', 2)
        channels = audio_data.get('channels', 1)
        bytes_per_sample = sampwidth * channels
        total_samples = frames / bytes_per_sample
        return total_samples / sample_rate
