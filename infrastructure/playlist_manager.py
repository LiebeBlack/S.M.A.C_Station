# -*- coding: utf-8 -*-
"""
Motor Backend para la gestión de Playlist Musical (Queue).
Permite administrar canciones, colas de reproducción y metadatos.
"""
import os

class PlaylistManager:
    def __init__(self):
        self.canciones = []
        self.indice_actual = 0
        self.modo_loop = True

    def agregar_cancion(self, ruta: str) -> bool:
        if os.path.exists(ruta):
            self.canciones.append(ruta)
            return True
        return False

    def eliminar_cancion(self, index: int):
        if 0 <= index < len(self.canciones):
            self.canciones.pop(index)
            if self.indice_actual >= len(self.canciones):
                self.indice_actual = 0

    def limpiar(self):
        self.canciones.clear()
        self.indice_actual = 0

    def mover_cancion(self, old_index: int, new_index: int):
        if 0 <= old_index < len(self.canciones) and 0 <= new_index < len(self.canciones):
            cancion = self.canciones.pop(old_index)
            self.canciones.insert(new_index, cancion)
            # Ajustar índice actual si es necesario
            if self.indice_actual == old_index:
                self.indice_actual = new_index
            elif old_index < self.indice_actual <= new_index:
                self.indice_actual -= 1
            elif new_index <= self.indice_actual < old_index:
                self.indice_actual += 1

    def siguiente(self) -> str:
        if not self.canciones:
            return None
        self.indice_actual += 1
        if self.indice_actual >= len(self.canciones):
            if self.modo_loop:
                self.indice_actual = 0
            else:
                self.indice_actual = len(self.canciones) - 1
        return self.obtener_activa()

    def anterior(self) -> str:
        if not self.canciones:
            return None
        self.indice_actual -= 1
        if self.indice_actual < 0:
            if self.modo_loop:
                self.indice_actual = len(self.canciones) - 1
            else:
                self.indice_actual = 0
        return self.obtener_activa()

    def set_activa(self, index: int):
        if 0 <= index < len(self.canciones):
            self.indice_actual = index

    def obtener_activa(self) -> str:
        if 0 <= self.indice_actual < len(self.canciones):
            return self.canciones[self.indice_actual]
        return None
        
    def obtener_todas(self) -> list:
        return self.canciones
