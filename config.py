# -*- coding: utf-8 -*-
"""
Archivo de configuración del sistema SMAC Station.
Modifica estos parámetros según tus necesidades.
"""
import os
import sys

def obtener_ruta_datos(ruta_relativa):
    """Obtiene la ruta para archivos de datos mutables al lado del ejecutable."""
    if getattr(sys, 'frozen', False):
        # Si está empaquetado por PyInstaller, buscar al lado del archivo .exe
        directorio_exe = os.path.dirname(sys.executable)
        return os.path.join(directorio_exe, ruta_relativa)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), ruta_relativa)

# Configuración de Audio
AUDIO_CONFIG = {
    # Velocidad de TTS (palabras por minuto)
    'tts_rate': 160,
    
    # Atenuación de música de fondo en dB (ducking)
    'ducking_db': 18,
    
    # Volumen de reproducción (0.0 a 1.0)
    'default_volume': 0.8,
    
    # Formato de audio de salida
    'output_format': 'wav',
    
    # Ruta predeterminada de cortina musical
    'default_cortina': obtener_ruta_datos('cortina_base.mp3'),
    
    # Ruta de salida predeterminada
    'default_output': obtener_ruta_datos('boletin_salida.wav')
}

# Configuración de Base de Datos
DB_CONFIG = {
    # Nombre del archivo de base de datos
    'db_file': obtener_ruta_datos('smac_station.db'),
    
    # Habilitar logging de consultas
    'enable_query_logging': False
}

# Configuración de Interfaz
UI_CONFIG = {
    # Modo de apariencia: "Dark", "Light", "System"
    'appearance_mode': 'Dark',
    
    # Tema de color: "blue", "dark-blue", "green"
    'color_theme': 'blue',
    
    # Dimensiones de ventana
    'window_width': 700,
    'window_height': 500,
    
    # Título de la aplicación
    'app_title': 'S.M.A.C. - Estación de Control Operacional'
}

# Configuración de Filtro de Contenido
FILTER_CONFIG = {
    # Lista negra de términos prohibidos
    'blacklist': [
        "partido", "vota", "candidato", "oposicion", 
        "oficialismo", "consigna", "comicios", "militante"
    ],
    
    # Habilitar filtrado estricto (incluye variaciones)
    'strict_filtering': True,
    
    # Mensaje de error cuando se bloquea contenido
    'blocked_message': "Contenido bloqueado: Viola el protocolo de neutralidad institucional."
}

# Configuración de Sistema
SYSTEM_CONFIG = {
    # Habilitar modo debug
    'debug_mode': False,
    
    # Nivel de logging: "DEBUG", "INFO", "WARNING", "ERROR"
    'log_level': 'INFO',
    
    # Crear directorios automáticamente si no existen
    'auto_create_dirs': True,
    
    # Limpiar archivos temporales automáticamente
    'auto_cleanup_temp': True
}
