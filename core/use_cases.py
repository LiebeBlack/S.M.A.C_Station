# -*- coding: utf-8 -*-
import os
from core.domain import FiltroContenido
from infrastructure.tts_fallback import TTSFallbackController
from infrastructure.audio_processing_fallback import AudioProcessingFallback
import config

class ProcesadorBoletin:
    def __init__(self):
        self.filtro = FiltroContenido()
        self.tts_rate = config.AUDIO_CONFIG['tts_rate']
        self.ducking_db = config.AUDIO_CONFIG['ducking_db']
        
        # Inicializar controladores con fallbacks
        self.tts_controller = TTSFallbackController()
        self.audio_processor = AudioProcessingFallback()
        
    def actualizar_configuracion(self, tts_rate: int = None, ducking_db: int = None):
        """Actualiza la configuración del procesador."""
        if tts_rate is not None:
            self.tts_rate = tts_rate
            self.tts_controller.set_rate(tts_rate)
        if ducking_db is not None:
            self.ducking_db = ducking_db
        
    def generar_audio_bucle(self, texto: str, ruta_cortina: str, ruta_salida: str) -> str:
        """
        Procesa el texto, renderiza la voz offline y la mezcla con música de fondo.
        Usa fallbacks automáticos para TTS y procesamiento de audio.
        """
        if not texto or texto.strip() == "":
            raise ValueError("El texto del boletín no puede estar vacío.")
            
        if not os.path.exists(ruta_cortina):
            raise FileNotFoundError(f"No se encuentra el archivo de cortina: {ruta_cortina}")
        
        if not self.filtro.validar_texto(texto):
            raise ValueError("Contenido bloqueado: Viola el protocolo de neutralidad institucional.")

        ruta_voz_temp = ""
        try:
            # 1. Generar TTS usando controlador con fallbacks
            import tempfile
            ruta_voz_temp = tempfile.mktemp(suffix=".wav", prefix="temp_voz_")
            self.tts_controller.text_to_speech(texto, ruta_voz_temp, self.tts_rate)

            # 2. Cargar pistas de audio usando procesador con fallbacks
            if not os.path.exists(ruta_voz_temp):
                raise RuntimeError("Error al generar archivo de voz temporal.")
                
            audio_voz = self.audio_processor.load_audio(ruta_voz_temp)
            audio_fondo = self.audio_processor.load_audio(ruta_cortina)

            # 3. Lógica de mezcla y atenuación automática (Ducking)
            # Atenuamos la música de fondo según configuración
            audio_mezclado = self.audio_processor.mix_audio(audio_voz, audio_fondo, self.ducking_db)

            # 4. Exportar el bloque masterizado listo para la transmisión
            self.audio_processor.save_audio(audio_mezclado, ruta_salida, formato='wav')
            
            # Limpieza de archivo temporal
            if os.path.exists(ruta_voz_temp):
                os.remove(ruta_voz_temp)
                
            return ruta_salida
            
        except Exception as e:
            # Limpieza en caso de error
            if ruta_voz_temp and os.path.exists(ruta_voz_temp):
                try:
                    os.remove(ruta_voz_temp)
                except:
                    pass
            raise RuntimeError(f"Error al procesar audio: {str(e)}")
            
    def procesar_boletin(self, texto: str, ruta_audio_fondo: str, ruta_salida: str) -> str:
        """Alias para generar_audio_bucle que mapea ruta_audio_fondo a ruta_cortina."""
        return self.generar_audio_bucle(texto, ruta_audio_fondo, ruta_salida)
    
    def close(self):
        """Cierra los controladores de fallback."""
        try:
            self.tts_controller.close()
            self.audio_processor.close()
        except Exception as e:
            print(f"Error al cerrar controladores: {e}")
