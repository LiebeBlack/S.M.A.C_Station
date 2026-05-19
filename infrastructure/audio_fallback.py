# -*- coding: utf-8 -*-
"""
Controlador de Audio con Fallbacks Múltiples
Soporta múltiples backends de audio con fallback automático.
"""
import os
from typing import Optional
from infrastructure.system_compat import system_compat

class AudioFallbackController:
    """Controlador de audio con múltiples backends y fallback automático."""
    
    def __init__(self):
        self.current_backend = None
        self.backends = {}
        self._initialize_backends()
        self._select_best_backend()
        self._reproduciendo = False
    
    def _initialize_backends(self):
        """Inicializa todos los backends de audio disponibles."""
        
        # Backend 1: Pygame (prioridad alta)
        if 'pygame' in system_compat.available_audio_backends:
            try:
                import pygame
                self.backends['pygame'] = PygameBackend()
            except Exception as e:
                print(f"Error inicializando pygame: {e}")
        
        # Backend 2: PyAudio
        if 'pyaudio' in system_compat.available_audio_backends:
            try:
                import pyaudio
                self.backends['pyaudio'] = PyAudioBackend()
            except Exception as e:
                print(f"Error inicializando pyaudio: {e}")
        
        # Backend 3: SoundDevice
        if 'sounddevice' in system_compat.available_audio_backends:
            try:
                import sounddevice
                self.backends['sounddevice'] = SoundDeviceBackend()
            except Exception as e:
                print(f"Error inicializando sounddevice: {e}")
        
        # Backend 4: SimpleAudio
        if 'simpleaudio' in system_compat.available_audio_backends:
            try:
                import simpleaudio
                self.backends['simpleaudio'] = SimpleAudioBackend()
            except Exception as e:
                print(f"Error inicializando simpleaudio: {e}")
        
        # Backend 5: Winsound (Windows only)
        if 'winsound' in system_compat.available_audio_backends:
            try:
                import winsound
                self.backends['winsound'] = WinsoundBackend()
            except Exception as e:
                print(f"Error inicializando winsound: {e}")
    
    def _select_best_backend(self):
        """Selecciona el mejor backend disponible."""
        priority = ['pygame', 'pyaudio', 'sounddevice', 'simpleaudio', 'winsound']
        
        for backend_name in priority:
            if backend_name in self.backends:
                self.current_backend = self.backends[backend_name]
                print(f"Backend de audio seleccionado: {backend_name}")
                return
        
        print("Advertencia: No se encontraron backends de audio disponibles")
    
    def reproducir_audio(self, ruta_archivo: str) -> bool:
        """Reproduce audio usando el backend actual con fallback."""
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encuentra el archivo: {ruta_archivo}")
        
        if not self.current_backend:
            raise RuntimeError("No hay backend de audio disponible")
        
        # Intentar con el backend actual
        try:
            self.current_backend.play(ruta_archivo)
            self._reproduciendo = True
            return True
        except Exception as e:
            print(f"Error con backend {type(self.current_backend).__name__}: {e}")
            # Intentar fallback a otro backend
            return self._try_fallback(ruta_archivo)
    
    def _try_fallback(self, ruta_archivo: str) -> bool:
        """Intenta reproducir con otro backend."""
        for backend_name, backend in self.backends.items():
            if backend != self.current_backend:
                try:
                    print(f"Intentando fallback a {backend_name}...")
                    backend.play(ruta_archivo)
                    self.current_backend = backend
                    self._reproduciendo = True
                    print(f"Fallback exitoso a {backend_name}")
                    return True
                except Exception as e:
                    print(f"Fallback a {backend_name} falló: {e}")
        
        return False
    
    def detener_reproduccion(self):
        """Detiene la reproducción actual."""
        if self.current_backend:
            try:
                self.current_backend.stop()
                self._reproduciendo = False
            except Exception as e:
                print(f"Error al detener reproducción: {e}")
    
    def pausar_reproduccion(self):
        """Pausa la reproducción."""
        if self.current_backend and hasattr(self.current_backend, 'pause'):
            try:
                self.current_backend.pause()
            except Exception as e:
                print(f"Error al pausar: {e}")
    
    def reanudar_reproduccion(self):
        """Reanuda la reproducción."""
        if self.current_backend and hasattr(self.current_backend, 'resume'):
            try:
                self.current_backend.resume()
            except Exception as e:
                print(f"Error al reanudar: {e}")
    
    def esta_reproduciendo(self) -> bool:
        """Verifica si hay audio reproduciéndose."""
        if self.current_backend and hasattr(self.current_backend, 'is_playing'):
            try:
                return self.current_backend.is_playing()
            except:
                return self._reproduciendo
        return self._reproduciendo
    
    def obtener_volumen(self) -> float:
        """Retorna el volumen actual."""
        if self.current_backend and hasattr(self.current_backend, 'get_volume'):
            try:
                return self.current_backend.get_volume()
            except:
                pass
        return 0.0
    
    def establecer_volumen(self, volumen: float):
        """Establece el volumen (0.0 a 1.0)."""
        volumen = max(0.0, min(1.0, volumen))
        if self.current_backend and hasattr(self.current_backend, 'set_volume'):
            try:
                self.current_backend.set_volume(volumen)
            except Exception as e:
                print(f"Error al establecer volumen: {e}")
    
    def cerrar(self):
        """Cierra todos los backends."""
        for backend in self.backends.values():
            try:
                if hasattr(backend, 'close'):
                    backend.close()
            except Exception as e:
                print(f"Error al cerrar backend: {e}")
        self._reproduciendo = False


# Implementaciones de Backends Específicos

class PygameBackend:
    """Backend usando pygame."""
    
    def __init__(self):
        import pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.pygame = pygame
    
    def play(self, ruta_archivo: str):
        self.pygame.mixer.music.load(ruta_archivo)
        self.pygame.mixer.music.play()
    
    def stop(self):
        self.pygame.mixer.music.stop()
    
    def pause(self):
        self.pygame.mixer.music.pause()
    
    def resume(self):
        self.pygame.mixer.music.unpause()
    
    def is_playing(self) -> bool:
        return self.pygame.mixer.music.get_busy()
    
    def get_volume(self) -> float:
        return self.pygame.mixer.music.get_volume()
    
    def set_volume(self, volumen: float):
        self.pygame.mixer.music.set_volume(volumen)
    
    def close(self):
        self.pygame.mixer.quit()


class PyAudioBackend:
    """Backend usando PyAudio."""
    
    def __init__(self):
        import pyaudio
        import wave
        self.pyaudio = pyaudio
        self.wave = wave
        self.stream = None
        self._thread = None
        self._stop_event = None
    
    def play(self, ruta_archivo: str):
        import threading
        self.stop()
        
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._play_loop,
            args=(ruta_archivo, self._stop_event)
        )
        self._thread.daemon = True
        self._thread.start()
        
    def _play_loop(self, ruta_archivo: str, stop_event):
        try:
            wf = self.wave.open(ruta_archivo, 'rb')
            p = self.pyaudio.PyAudio()
            
            self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
            
            data = wf.readframes(1024)
            while data and not stop_event.is_set():
                self.stream.write(data)
                data = wf.readframes(1024)
            
            wf.close()
            if self.stream:
                self.stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error en hilo de reproducción PyAudio: {e}")
    
    def stop(self):
        if self._stop_event:
            self._stop_event.set()
        if self.stream:
            try:
                self.stream.stop_stream()
            except:
                pass
    
    def close(self):
        self.stop()


class SoundDeviceBackend:
    """Backend usando sounddevice."""
    
    def __init__(self):
        import sounddevice as sd
        import soundfile as sf
        self.sd = sd
        self.sf = sf
    
    def play(self, ruta_archivo: str):
        data, samplerate = self.sf.read(ruta_archivo)
        self.sd.play(data, samplerate)
    
    def stop(self):
        self.sd.stop()


class SimpleAudioBackend:
    """Backend usando simpleaudio."""
    
    def __init__(self):
        import simpleaudio as sa
        self.sa = sa
    
    def play(self, ruta_archivo: str):
        wave_obj = self.sa.WaveObject.from_wave_file(ruta_archivo)
        wave_obj.play()
    
    def stop(self):
        self.sa.stop_all()


class WinsoundBackend:
    """Backend usando winsound (Windows only)."""
    
    def __init__(self):
        import winsound
        self.winsound = winsound
    
    def play(self, ruta_archivo: str):
        self.winsound.PlaySound(ruta_archivo, self.winsound.SND_FILENAME | self.winsound.SND_ASYNC)
    
    def stop(self):
        self.winsound.PlaySound(None, self.winsound.SND_PURGE)
