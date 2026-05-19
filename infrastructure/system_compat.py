# -*- coding: utf-8 -*-
"""
Módulo de Compatibilidad del Sistema
Proporciona fallbacks y detección de plataforma para máxima compatibilidad.
"""
import platform
import os
import sys
import signal
from typing import Optional, Dict, List, Tuple

# =====================================================================
# REPARACIÓN DE RUTAS DLL PARA WINDOWS (Evita "DLL load failed")
# =====================================================================
if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        os.add_dll_directory(base_dir)
    except:
        pass
        
    internal_dir = os.path.join(base_dir, "_internal")
    if os.path.exists(internal_dir):
        try:
            os.add_dll_directory(internal_dir)
        except:
            pass
            
    try:
        import site
        site_dirs = []
        if hasattr(site, 'getsitepackages'):
            site_dirs.extend(site.getsitepackages())
        if hasattr(site, 'getusersitepackages'):
            site_dirs.append(site.getusersitepackages())
            
        for path in site_dirs:
            if os.path.exists(path):
                tbb_path = os.path.join(path, "tbb")
                if os.path.exists(tbb_path):
                    try: os.add_dll_directory(tbb_path) 
                    except: pass
                    tbb_bin = os.path.join(tbb_path, "bin")
                    if os.path.exists(tbb_bin):
                        try: os.add_dll_directory(tbb_bin)
                        except: pass
                sf_path = os.path.join(path, "soundfile")
                if os.path.exists(sf_path):
                    try: os.add_dll_directory(sf_path)
                    except: pass
                llvm_path = os.path.join(path, "llvmlite", "binding")
                if os.path.exists(llvm_path):
                    try: os.add_dll_directory(llvm_path)
                    except: pass
    except Exception as e:
        pass

    lib_bin = os.path.join(sys.prefix, "Library", "bin")
    if os.path.exists(lib_bin):
        try:
            os.add_dll_directory(lib_bin)
        except:
            pass
            
    try:
        os.add_dll_directory(os.path.dirname(sys.executable))
    except:
        pass
# =====================================================================

class SystemCompatibility:
    """Gestiona la compatibilidad del sistema y proporciona fallbacks."""
    
    def __init__(self):
        self.platform_info = self._detect_platform()
        self.available_audio_backends = self._detect_audio_backends()
        self.available_tts_engines = self._detect_tts_engines()
        self.available_audio_processing = self._detect_audio_processing()
        
    def _detect_platform(self) -> Dict[str, str]:
        """Detecta información detallada de la plataforma."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'is_windows': platform.system() == 'Windows',
            'is_linux': platform.system() == 'Linux',
            'is_macos': platform.system() == 'Darwin'
        }
    
    def _detect_audio_backends(self) -> List[str]:
        """Detecta backends de audio disponibles."""
        backends = []
        
        # Detectar pygame
        try:
            import pygame
            backends.append('pygame')
        except ImportError:
            pass
        
        # Detectar pyaudio
        try:
            import pyaudio
            backends.append('pyaudio')
        except ImportError:
            pass
        
        # Detectar winsound (Windows only)
        if self.platform_info['is_windows']:
            try:
                import winsound
                backends.append('winsound')
            except ImportError:
                pass
        
        # Detectar simpleaudio
        try:
            import simpleaudio
            backends.append('simpleaudio')
        except ImportError:
            pass
        
        # Detectar sounddevice
        try:
            import sounddevice
            backends.append('sounddevice')
        except ImportError:
            pass
        
        return backends
    
    def _detect_tts_engines(self) -> List[str]:
        """Detecta motores TTS disponibles."""
        engines = []
        
        # Detectar pyttsx3
        try:
            import pyttsx3
            engines.append('pyttsx3')
        except ImportError:
            pass
        
        # Detectar espeak (Linux)
        if self.platform_info['is_linux']:
            try:
                import subprocess
                subprocess.run(['espeak', '--version'], 
                             capture_output=True, check=True)
                engines.append('espeak')
            except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Detectar say (macOS)
        if self.platform_info['is_macos']:
            try:
                import subprocess
                subprocess.run(['say', '-v', '?'], 
                             capture_output=True, check=True)
                engines.append('say')
            except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # Detectar SAPI (Windows)
        if self.platform_info['is_windows']:
            try:
                import win32com.client
                engines.append('sapi')
            except ImportError:
                pass
        
        # Detectar gTTS (Google TTS)
        try:
            import gtts
            engines.append('gtts')
        except ImportError:
            pass
        
        return engines
    
    def _detect_audio_processing(self) -> List[str]:
        """Detecta librerías de procesamiento de audio disponibles."""
        libraries = []
        
        # Detectar pydub (requiere ffmpeg)
        try:
            from pydub import AudioSegment
            import subprocess
            # Solo añadir pydub si existe ffmpeg en el sistema
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            libraries.append('pydub')
        except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Detectar librosa
        try:
            import librosa
            libraries.append('librosa')
        except ImportError:
            pass
        
        # Detectar soundfile
        try:
            import soundfile
            libraries.append('soundfile')
        except ImportError:
            pass
        
        # Detectar wave (built-in)
        try:
            import wave
            libraries.append('wave')
        except ImportError:
            pass
        
        return libraries
    
    def get_preferred_audio_backend(self) -> str:
        """Retorna el backend de audio preferido según disponibilidad."""
        priority_order = ['pygame', 'pyaudio', 'sounddevice', 'simpleaudio', 'winsound']
        
        for backend in priority_order:
            if backend in self.available_audio_backends:
                return backend
        
        return None
    
    def get_preferred_tts_engine(self) -> str:
        """Retorna el motor TTS preferido según disponibilidad."""
        priority_order = ['gtts', 'pyttsx3', 'sapi', 'say', 'espeak']
        
        for engine in priority_order:
            if engine in self.available_tts_engines:
                return engine
        
        return None
    
    def get_preferred_audio_processing(self) -> str:
        """Retorna la librería de procesamiento preferida."""
        priority_order = ['pydub', 'librosa', 'soundfile', 'wave']
        
        for library in priority_order:
            if library in self.available_audio_processing:
                return library
        
        return None
    
    def check_system_requirements(self) -> Tuple[bool, List[str]]:
        """Verifica requisitos del sistema y retorna (éxito, advertencias)."""
        warnings = []
        
        # Verificar Python
        if sys.version_info < (3, 7):
            warnings.append("Python 3.7+ recomendado para mejor compatibilidad")
        
        # Verificar backends de audio
        if not self.available_audio_backends:
            warnings.append("No se detectaron backends de audio. Instale pygame o pyaudio.")
        
        # Verificar motores TTS
        if not self.available_tts_engines:
            warnings.append("No se detectaron motores TTS. Instale pyttsx3.")
        
        # Verificar procesamiento de audio
        if not self.available_audio_processing:
            warnings.append("No se detectaron librerías de procesamiento de audio. Instale pydub.")
        
        # Verificar espacio en disco
        try:
            import shutil
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 1:
                warnings.append(f"Espacio en disco bajo: {free_gb:.2f} GB libres")
        except:
            pass
        
        return (len(warnings) == 0, warnings)
    
    def get_system_report(self) -> str:
        """Genera un reporte detallado del sistema."""
        report = []
        report.append("=== REPORTE DE COMPATIBILIDAD DEL SISTEMA ===\n")
        
        report.append("Plataforma:")
        for key, value in self.platform_info.items():
            report.append(f"  {key}: {value}")
        
        report.append("\nBackends de Audio Disponibles:")
        if self.available_audio_backends:
            for backend in self.available_audio_backends:
                report.append(f"  ✓ {backend}")
        else:
            report.append("  ✗ Ninguno detectado")
        
        report.append("\nMotores TTS Disponibles:")
        if self.available_tts_engines:
            for engine in self.available_tts_engines:
                report.append(f"  ✓ {engine}")
        else:
            report.append("  ✗ Ninguno detectado")
        
        report.append("\nLibrerías de Procesamiento de Audio:")
        if self.available_audio_processing:
            for library in self.available_audio_processing:
                report.append(f"  ✓ {library}")
        else:
            report.append("  ✗ Ninguna detectada")
        
        report.append("\nPreferencias del Sistema:")
        report.append(f"  Backend de Audio: {self.get_preferred_audio_backend() or 'Ninguno'}")
        report.append(f"  Motor TTS: {self.get_preferred_tts_engine() or 'Ninguno'}")
        report.append(f"  Procesamiento: {self.get_preferred_audio_processing() or 'Ninguno'}")
        
        success, warnings = self.check_system_requirements()
        report.append("\nAdvertencias:")
        if warnings:
            for warning in warnings:
                report.append(f"  ⚠ {warning}")
        else:
            report.append("  ✓ Sistema compatible")
        
        return "\n".join(report)


# Instancia global de compatibilidad
system_compat = SystemCompatibility()


def setup_signal_handlers(callback):
    """Configura manejadores de señales para cierre graceful."""
    if system_compat.platform_info['is_windows']:
        # Windows usa SIGINT y SIGBREAK
        signal.signal(signal.SIGINT, callback)
        try:
            signal.signal(signal.SIGBREAK, callback)
        except:
            pass
    else:
        # Unix-like systems
        signal.signal(signal.SIGINT, callback)
        signal.signal(signal.SIGTERM, callback)
        try:
            signal.signal(signal.SIGHUP, callback)
        except:
            pass
