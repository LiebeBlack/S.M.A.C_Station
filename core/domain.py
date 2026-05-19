# -*- coding: utf-8 -*-

class FiltroContenido:
    def __init__(self):
        # Lista negra inicial de términos excluidos para garantizar neutralidad
        self._blacklist = [
            "partido", "vota", "candidato", "oposicion", 
            "oficialismo", "consigna", "comicios", "militante"
        ]

    def validar_texto(self, texto: str) -> bool:
        """
        Analiza el texto ingresado por el operador.
        Retorna True si es apto, False si viola el protocolo de neutralidad.
        """
        palabras = texto.lower().split()
        for palabra in palabras:
            # Limpieza básica de signos de puntuación
            palabra_limpia = ''.join(e for e in palabra if e.isalnum())
            if palabra_limpia in self._blacklist:
                return False
        return True
