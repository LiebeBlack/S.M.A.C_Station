# -*- coding: utf-8 -*-
"""
Verificador de Compatibilidad del Sistema
Realiza verificaciones completas del sistema y proporciona advertencias.
"""
import sys
import os
from typing import List, Tuple, Dict
from infrastructure.system_compat import system_compat
from infrastructure.ui_fallback import check_ui_dependencies
from infrastructure.localization import i18n

class SystemChecker:
    """Verifica la compatibilidad del sistema y genera reportes."""
    
    def __init__(self):
        self.checks_performed = False
        self.warnings = []
        self.errors = []
        self.recommendations = []
    
    def run_all_checks(self) -> Dict[str, any]:
        """Ejecuta todas las verificaciones del sistema."""
        self.checks_performed = True
        
        result = {
            'platform': self._check_platform(),
            'python': self._check_python(),
            'audio_backends': self._check_audio_backends(),
            'tts_engines': self._check_tts_engines(),
            'audio_processing': self._check_audio_processing(),
            'ui_toolkits': self._check_ui_toolkits(),
            'disk_space': self._check_disk_space(),
            'memory': self._check_memory(),
            'permissions': self._check_permissions(),
            'overall_status': 'unknown'
        }
        
        result['overall_status'] = self._determine_overall_status(result)
        
        return result
    
    def _check_platform(self) -> Dict[str, any]:
        """Verifica la plataforma del sistema."""
        info = {
            'compatible': True,
            'details': system_compat.platform_info,
            'warnings': []
        }
        
        # Verificar compatibilidad de plataforma
        if system_compat.platform_info['python_version'].startswith('2.'):
            info['compatible'] = False
            info['warnings'].append("Python 2 no es compatible. Se requiere Python 3.7+")
        
        if sys.version_info < (3, 7):
            info['warnings'].append("Python 3.7+ recomendado para mejor compatibilidad")
        
        return info
    
    def _check_python(self) -> Dict[str, any]:
        """Verifica la instalación de Python."""
        info = {
            'compatible': True,
            'version': sys.version,
            'warnings': []
        }
        
        if sys.version_info < (3, 6):
            info['compatible'] = False
            info['warnings'].append("Python 3.6+ requerido")
        
        return info
    
    def _check_audio_backends(self) -> Dict[str, any]:
        """Verifica backends de audio."""
        info = {
            'available': system_compat.available_audio_backends,
            'preferred': system_compat.get_preferred_audio_backend(),
            'compatible': len(system_compat.available_audio_backends) > 0,
            'warnings': []
        }
        
        if not info['available']:
            info['compatible'] = False
            info['warnings'].append("No se detectaron backends de audio")
            info['warnings'].append("Instale: pip install pygame pyaudio")
        else:
            info['warnings'].append(f"Backends disponibles: {', '.join(info['available'])}")
        
        return info
    
    def _check_tts_engines(self) -> Dict[str, any]:
        """Verifica motores TTS."""
        info = {
            'available': system_compat.available_tts_engines,
            'preferred': system_compat.get_preferred_tts_engine(),
            'compatible': len(system_compat.available_tts_engines) > 0,
            'warnings': []
        }
        
        if not info['available']:
            info['compatible'] = False
            info['warnings'].append("No se detectaron motores TTS")
            info['warnings'].append("Instale: pip install pyttsx3")
        else:
            info['warnings'].append(f"Motores disponibles: {', '.join(info['available'])}")
        
        return info
    
    def _check_audio_processing(self) -> Dict[str, any]:
        """Verifica librerías de procesamiento de audio."""
        info = {
            'available': system_compat.available_audio_processing,
            'preferred': system_compat.get_preferred_audio_processing(),
            'compatible': len(system_compat.available_audio_processing) > 0,
            'warnings': []
        }
        
        if not info['available']:
            info['compatible'] = False
            info['warnings'].append("No se detectaron librerías de procesamiento de audio")
            info['warnings'].append("Instale: pip install pydub")
        else:
            info['warnings'].append(f"Librerías disponibles: {', '.join(info['available'])}")
        
        return info
    
    def _check_ui_toolkits(self) -> Dict[str, any]:
        """Verifica toolkits de UI."""
        ui_available, ui_toolkit, ui_warnings = check_ui_dependencies()
        
        info = {
            'available': ui_toolkit,
            'compatible': ui_available,
            'warnings': ui_warnings
        }
        
        return info
    
    def _check_disk_space(self) -> Dict[str, any]:
        """Verifica espacio en disco."""
        info = {
            'compatible': True,
            'warnings': []
        }
        
        try:
            import shutil
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            
            info['free_gb'] = free_gb
            info['total_gb'] = total_gb
            info['usage_percent'] = (disk_usage.used / disk_usage.total) * 100
            
            if free_gb < 0.5:
                info['compatible'] = False
                info['warnings'].append(f"Espacio en disco crítico: {free_gb:.2f} GB libres")
            elif free_gb < 2:
                info['warnings'].append(f"Espacio en disco bajo: {free_gb:.2f} GB libres")
            
        except Exception as e:
            info['warnings'].append(f"No se pudo verificar espacio en disco: {e}")
        
        return info
    
    def _check_memory(self) -> Dict[str, any]:
        """Verifica memoria disponible."""
        info = {
            'compatible': True,
            'warnings': []
        }
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            total_gb = mem.total / (1024**3)
            
            info['available_gb'] = available_gb
            info['total_gb'] = total_gb
            info['usage_percent'] = mem.percent
            
            if available_gb < 0.5:
                info['compatible'] = False
                info['warnings'].append(f"Memoria disponible baja: {available_gb:.2f} GB")
            elif available_gb < 1:
                info['warnings'].append(f"Memoria disponible limitada: {available_gb:.2f} GB")
            
        except ImportError:
            info['warnings'].append("psutil no disponible para verificar memoria")
        except Exception as e:
            info['warnings'].append(f"No se pudo verificar memoria: {e}")
        
        return info
    
    def _check_permissions(self) -> Dict[str, any]:
        """Verifica permisos del sistema."""
        info = {
            'compatible': True,
            'warnings': []
        }
        
        # Verificar permisos de escritura en directorio actual
        try:
            test_file = ".permission_test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except PermissionError:
            info['compatible'] = False
            info['warnings'].append("No hay permisos de escritura en el directorio actual")
        except Exception as e:
            info['warnings'].append(f"Error al verificar permisos: {e}")
        
        return info
    
    def _determine_overall_status(self, results: Dict) -> str:
        """Determina el estado general del sistema."""
        critical_failures = []
        warnings = []
        
        for check_name, check_result in results.items():
            if check_name == 'overall_status':
                continue
            
            if not check_result.get('compatible', True):
                critical_failures.append(check_name)
            
            if 'warnings' in check_result:
                warnings.extend(check_result['warnings'])
        
        self.warnings = warnings
        self.errors = critical_failures
        
        if critical_failures:
            return 'critical'
        elif warnings:
            return 'warning'
        else:
            return 'ok'
    
    def generate_report(self, results: Dict = None) -> str:
        """Genera un reporte detallado del sistema."""
        if results is None:
            results = self.run_all_checks()
        
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE COMPATIBILIDAD DEL SISTEMA")
        report.append("=" * 60)
        report.append("")
        
        # Estado general
        status_emoji = {
            'ok': '✅',
            'warning': '⚠️',
            'critical': '❌'
        }
        status = results['overall_status']
        report.append(f"Estado General: {status_emoji.get(status, '❓')} {status.upper()}")
        report.append("")
        
        # Plataforma
        report.append("--- PLATAFORMA ---")
        platform = results['platform']
        report.append(f"Sistema: {platform['details']['system']}")
        report.append(f"Versión: {platform['details']['release']}")
        report.append(f"Arquitectura: {platform['details']['architecture']}")
        report.append(f"Python: {platform['details']['python_version']}")
        if platform['warnings']:
            for w in platform['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # Audio
        report.append("--- AUDIO ---")
        audio = results['audio_backends']
        if audio['available']:
            report.append(f"Backends: {', '.join(audio['available'])}")
            report.append(f"Preferido: {audio['preferred']}")
        else:
            report.append("❌ No hay backends de audio disponibles")
        if audio['warnings']:
            for w in audio['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # TTS
        report.append("--- TTS ---")
        tts = results['tts_engines']
        if tts['available']:
            report.append(f"Motores: {', '.join(tts['available'])}")
            report.append(f"Preferido: {tts['preferred']}")
        else:
            report.append("❌ No hay motores TTS disponibles")
        if tts['warnings']:
            for w in tts['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # Procesamiento de Audio
        report.append("--- PROCESAMIENTO DE AUDIO ---")
        proc = results['audio_processing']
        if proc['available']:
            report.append(f"Librerías: {', '.join(proc['available'])}")
            report.append(f"Preferida: {proc['preferred']}")
        else:
            report.append("❌ No hay librerías de procesamiento disponibles")
        if proc['warnings']:
            for w in proc['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # UI
        report.append("--- INTERFAZ GRÁFICA ---")
        ui = results['ui_toolkits']
        if ui['available']:
            report.append(f"Toolkit: {ui['available']}")
        else:
            report.append("❌ No hay toolkit de UI disponible")
        if ui['warnings']:
            for w in ui['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # Recursos del Sistema
        report.append("--- RECURSOS DEL SISTEMA ---")
        disk = results['disk_space']
        if 'free_gb' in disk:
            report.append(f"Disco Libre: {disk['free_gb']:.2f} GB / {disk['total_gb']:.2f} GB")
            report.append(f"Uso: {disk['usage_percent']:.1f}%")
        if disk['warnings']:
            for w in disk['warnings']:
                report.append(f"  ⚠️ {w}")
        
        memory = results['memory']
        if 'available_gb' in memory:
            report.append(f"Memoria Libre: {memory['available_gb']:.2f} GB / {memory['total_gb']:.2f} GB")
            report.append(f"Uso: {memory['usage_percent']:.1f}%")
        if memory['warnings']:
            for w in memory['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # Permisos
        report.append("--- PERMISOS ---")
        perms = results['permissions']
        if perms['compatible']:
            report.append("✅ Permisos de escritura correctos")
        else:
            report.append("❌ No hay permisos de escritura")
        if perms['warnings']:
            for w in perms['warnings']:
                report.append(f"  ⚠️ {w}")
        report.append("")
        
        # Recomendaciones
        report.append("--- RECOMENDACIONES ---")
        if results['overall_status'] == 'critical':
            report.append("❌ El sistema tiene fallas críticas que deben ser resueltas")
            report.append("   antes de continuar.")
        elif results['overall_status'] == 'warning':
            report.append("⚠️ El sistema tiene advertencias pero puede funcionar")
            report.append("   con funcionalidad limitada.")
        else:
            report.append("✅ El sistema es totalmente compatible.")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def get_installation_commands(self) -> List[str]:
        """Retorna comandos de instalación para dependencias faltantes."""
        commands = []
        
        if not system_compat.available_audio_backends:
            commands.append("pip install pygame pyaudio")
        
        if not system_compat.available_tts_engines:
            commands.append("pip install pyttsx3")
        
        if not system_compat.available_audio_processing:
            commands.append("pip install pydub")
        
        ui_available, ui_toolkit, _ = check_ui_dependencies()
        if not ui_available or ui_toolkit != 'customtkinter':
            commands.append("pip install customtkinter==5.2.2")
        
        # Agregar dependencias opcionales
        commands.append("pip install psutil scipy")  # Para verificación de memoria y procesamiento avanzado
        
        return commands


# Instancia global del verificador
system_checker = SystemChecker()
