# Carpeta de Cortinas Musicales

Esta carpeta contiene las pistas de audio de fondo (cortinas) utilizadas para la mezcla con los boletines de voz.

## Formatos Soportados

- MP3 (recomendado)
- WAV
- OGG

## Instrucciones

1. Coloca tus archivos de audio en esta carpeta
2. Nombra tus archivos de forma descriptiva, ej: `cortina_emergencia.mp3`
3. Referencia los archivos en el código usando la ruta relativa: `assets/audio/cortinas/tu_archivo.mp3`

## Ejemplo de Uso

```python
from core.use_cases import ProcesadorBoletin

procesador = ProcesadorBoletin()
procesador.generar_audio_bucle(
    texto="Mensaje de emergencia",
    ruta_cortina="assets/audio/cortinas/cortina_emergencia.mp3",
    ruta_salida="boletin_salida.wav"
)
```

## Notas

- Se recomienda usar cortinas de 30-60 segundos de duración
- El sistema hará loop automáticamente si la cortina es más corta que el boletín
- La música se atenuará automáticamente -18dB durante la voz (ducking)
