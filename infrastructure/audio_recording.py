# -*- coding: utf-8 -*-
"""
Grabadora de Audio con Fallbacks Múltiples
Soporta múltiples dispositivos de entrada con fallback automático.
"""
import os
import tempfile
from typing import Optional, List
from infrastructure.system_compat import system_compat

class AudioRecordingFallback:
    """Grabadora de audio con múltiples backends y fallback automático."""
    
    def __init__(self):
        self.current_backend = None
        self.backends = {}
        self._initialize_backends()
        self._select_best_backend()
        self.recording = False
    
    def _initialize_backends(self):
        """Inicializa todos los backends de grabación disponibles."""
        
        # Backend 1: PyAudio (prioridad alta)
        if 'pyaudio' in system_compat.available_audio_backends:
            try:
                self.backends['pyaudio'] = PyAudioRecorder()
            except Exception as e:
                print(f"Error inicializando pyaudio recorder: {e}")
        
        # Backend 2: SoundDevice
        if 'sounddevice' in system_compat.available_audio_backends:
            try:
                self.backends['sounddevice'] = SoundDeviceRecorder()
            except Exception as e:
                print(f"Error inicializando sounddevice recorder: {e}")
        
        # Backend 3: PyAudio con wave (fallback básico)
        if 'pyaudio' in system_compat.available_audio_backends:
            try:
                self.backends['pyaudio_wave'] = PyAudioWaveRecorder()
            except Exception as e:
                print(f"Error inicializando pyaudio_wave recorder: {e}")
    
    def _select_best_backend(self):
        """Selecciona el mejor backend disponible."""
        priority = ['pyaudio', 'sounddevice', 'pyaudio_wave']
        
        for backend_name in priority:
            if backend_name in self.backends:
                self.current_backend = self.backends[backend_name]
                print(f"Backend de grabación seleccionado: {backend_name}")
                return
        
        print("Advertencia: No se encontraron backends de grabación disponibles")
    
    def get_input_devices(self) -> List[dict]:
        """Retorna la lista de dispositivos de entrada disponibles."""
        if self.current_backend and hasattr(self.current_backend, 'get_input_devices'):
            try:
                return self.current_backend.get_input_devices()
            except Exception as e:
                print(f"Error al obtener dispositivos: {e}")
        return []
    
    def start_recording(self, output_file: str, device_index: Optional[int] = None, 
                       sample_rate: int = 44100, channels: int = 1) -> bool:
        """Inicia la grabación de audio."""
        if not self.current_backend:
            raise RuntimeError("No hay backend de grabación disponible")
        
        try:
            self.current_backend.start(output_file, device_index, sample_rate, channels)
            self.recording = True
            return True
        except Exception as e:
            print(f"Error iniciando grabación: {e}")
            return self._try_fallback_start(output_file, device_index, sample_rate, channels)
    
    def _try_fallback_start(self, output_file: str, device_index: Optional[int], 
                           sample_rate: int, channels: int) -> bool:
        """Intenta iniciar grabación con otro backend."""
        for backend_name, backend in self.backends.items():
            if backend != self.current_backend:
                try:
                    print(f"Intentando fallback a {backend_name}...")
                    backend.start(output_file, device_index, sample_rate, channels)
                    self.current_backend = backend
                    self.recording = True
                    print(f"Fallback exitoso a {backend_name}")
                    return True
                except Exception as e:
                    print(f"Fallback a {backend_name} falló: {e}")
        
        return False
    
    def stop_recording(self) -> str:
        """Detiene la grabación y retorna la ruta del archivo."""
        if self.current_backend:
            try:
                ruta = self.current_backend.stop()
                self.recording = False
                return ruta
            except Exception as e:
                print(f"Error al detener grabación: {e}")
        return None
    
    def is_recording(self) -> bool:
        """Verifica si está grabando."""
        return self.recording
        
    def get_last_amplitude(self) -> float:
        """Retorna la última amplitud capturada del micrófono en tiempo real."""
        if self.recording and self.current_backend and hasattr(self.current_backend, 'last_amplitude'):
            return self.current_backend.last_amplitude
        return 0.0
    
    def close(self):
        """Cierra todos los backends."""
        for backend in self.backends.values():
            try:
                if hasattr(backend, 'close'):
                    backend.close()
            except Exception as e:
                print(f"Error al cerrar backend: {e}")
        self.recording = False


# Implementaciones de Grabadores Específicos

class PyAudioRecorder:
    """Grabador usando PyAudio."""
    
    def __init__(self):
        import pyaudio
        import threading
        self.pyaudio = pyaudio
        self.threading = threading
        self.stream = None
        self.frames = []
        self.output_file = None
        self.recording_thread = None
        self.should_record = False
        self.last_amplitude = 0.0
    
    def get_input_devices(self) -> List[dict]:
        """Retorna dispositivos de entrada disponibles."""
        p = self.pyaudio.PyAudio()
        devices = []
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        
        p.terminate()
        return devices
    
    def _record_frames(self):
        """Captura frames de audio en un thread separado."""
        import numpy as np
        while self.should_record and self.stream and self.stream.is_active():
            try:
                data = self.stream.read(1024)
                self.frames.append(data)
                if len(data) > 0:
                    samples = np.frombuffer(data, dtype=np.int16)
                    if len(samples) > 0:
                        self.last_amplitude = float(np.sqrt(np.mean(samples.astype(np.float32)**2)) / 32768.0)
            except:
                break
    
    def start(self, output_file: str, device_index: Optional[int] = None, 
              sample_rate: int = 44100, channels: int = 1):
        """Inicia la grabación."""
        self.output_file = output_file
        self.frames = []
        self.should_record = True
        self.sample_rate = sample_rate
        self.channels = channels
        
        p = self.pyaudio.PyAudio()
        
        self.stream = p.open(
            format=self.pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        self.stream.start_stream()
        
        # Iniciar thread para capturar frames
        self.recording_thread = self.threading.Thread(target=self._record_frames)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop(self) -> str:
        """Detiene la grabación y guarda el archivo."""
        self.should_record = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Guardar archivo WAV
        import wave
        wf = wave.open(self.output_file, 'wb')
        wf.setnchannels(getattr(self, 'channels', 1))
        wf.setsampwidth(self.pyaudio.get_sample_size(self.pyaudio.paInt16))
        wf.setframerate(getattr(self, 'sample_rate', 44100))
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        return self.output_file
    
    def close(self):
        """Cierra el grabador."""
        self.should_record = False
        if self.stream:
            try:
                self.stream.close()
            except:
                pass


class SoundDeviceRecorder:
    """Grabador usando sounddevice."""
    
    def __init__(self):
        import sounddevice as sd
        import soundfile as sf
        self.sd = sd
        self.sf = sf
        self.recording = None
        self.output_file = None
        self.last_amplitude = 0.0
    
    def get_input_devices(self) -> List[dict]:
        """Retorna dispositivos de entrada disponibles."""
        devices = []
        device_list = self.sd.query_devices()
        
        for i, device in enumerate(device_list):
            if device['max_input_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': int(device['default_samplerate'])
                })
        
        return devices
    
    def start(self, output_file: str, device_index: Optional[int] = None, 
              sample_rate: int = 44100, channels: int = 1):
        """Inicia la grabación."""
        self.output_file = output_file
        
        # Preparar archivo de salida
        self.sf_file = self.sf.SoundFile(self.output_file, mode='w', samplerate=sample_rate,
                                         channels=channels, subtype='PCM_16')
                                         
        def callback(indata, frames, time, status):
            if status:
                pass
            self.sf_file.write(indata.copy())
            import numpy as np
            if len(indata) > 0:
                self.last_amplitude = float(np.sqrt(np.mean(indata**2)))
            
        self.stream = self.sd.InputStream(samplerate=sample_rate, device=device_index,
                                          channels=channels, callback=callback)
        self.stream.start()
    
    def stop(self) -> str:
        """Detiene la grabación."""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'sf_file') and self.sf_file:
            self.sf_file.close()
        return self.output_file
    
    def close(self):
        """Cierra el grabador."""
        self.stop()


class PyAudioWaveRecorder:
    """Grabador usando PyAudio con wave (fallback básico)."""
    
    def __init__(self):
        import pyaudio
        import wave
        import threading
        self.pyaudio = pyaudio
        self.wave = wave
        self.threading = threading
        self.stream = None
        self.frames = []
        self.output_file = None
        self.recording_thread = None
        self.should_record = False
        self.last_amplitude = 0.0
    
    def get_input_devices(self) -> List[dict]:
        """Retorna dispositivos de entrada disponibles."""
        p = self.pyaudio.PyAudio()
        devices = []
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        
        p.terminate()
        return devices
    
    def _record_frames(self):
        """Captura frames de audio en un thread separado."""
        import numpy as np
        while self.should_record and self.stream and self.stream.is_active():
            try:
                data = self.stream.read(1024)
                self.frames.append(data)
                if len(data) > 0:
                    samples = np.frombuffer(data, dtype=np.int16)
                    if len(samples) > 0:
                        self.last_amplitude = float(np.sqrt(np.mean(samples.astype(np.float32)**2)) / 32768.0)
            except:
                break
    
    def start(self, output_file: str, device_index: Optional[int] = None, 
              sample_rate: int = 44100, channels: int = 1):
        """Inicia la grabación."""
        self.output_file = output_file
        self.frames = []
        self.should_record = True
        self.sample_rate = sample_rate
        self.channels = channels
        
        p = self.pyaudio.PyAudio()
        
        self.stream = p.open(
            format=self.pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        self.stream.start_stream()
        
        # Iniciar thread para capturar frames
        self.recording_thread = self.threading.Thread(target=self._record_frames)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop(self) -> str:
        """Detiene la grabación y guarda el archivo."""
        self.should_record = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Guardar archivo WAV
        wf = self.wave.open(self.output_file, 'wb')
        wf.setnchannels(getattr(self, 'channels', 1))
        wf.setsampwidth(self.pyaudio.get_sample_size(self.pyaudio.paInt16))
        wf.setframerate(getattr(self, 'sample_rate', 44100))
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        return self.output_file
    
    def close(self):
        """Cierra el grabador."""
        self.should_record = False
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
