# -*- coding: utf-8 -*-
import sqlite3
from typing import Optional, List, Dict, Tuple

class DatabaseConnection:
    """Gestiona la conexión local a SQLite para persistencia de boletines."""
    
    def __init__(self, db_path: str = "smac_station.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.connect()
    
    def connect(self) -> sqlite3.Connection:
        """Establece conexión con la base de datos local."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self._crear_tablas()
        return self.connection
    
    def _crear_tablas(self):
        """Crea las tablas necesarias si no existen."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boletines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                ruta_audio TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
    
    def guardar_boletin(self, texto: str, ruta_audio: str) -> int:
        """Guarda un boletín en la base de datos."""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO boletines (texto, ruta_audio) VALUES (?, ?)",
            (texto, ruta_audio)
        )
        self.connection.commit()
        return cursor.lastrowid
    
    def obtener_todos_boletines(self, limite: int = 10) -> List[Tuple[int, str, str, str]]:
        """Obtiene todos los boletines, ordenados por fecha descendente."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, texto, ruta_audio, fecha_creacion FROM boletines ORDER BY fecha_creacion DESC LIMIT ?",
            (limite,)
        )
        return cursor.fetchall()
    
    def obtener_boletin_por_id(self, id_boletin: int) -> Optional[Tuple[int, str, str, str]]:
        """Obtiene un boletín específico por su ID."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, texto, ruta_audio, fecha_creacion FROM boletines WHERE id = ?",
            (id_boletin,)
        )
        return cursor.fetchone()
    
    def eliminar_boletin(self, id_boletin: int) -> bool:
        """Elimina un boletín por su ID."""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM boletines WHERE id = ?", (id_boletin,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def actualizar_boletin(self, id_boletin: int, texto: str = None, ruta_audio: str = None) -> bool:
        """Actualiza un boletín existente."""
        if texto is None and ruta_audio is None:
            return False
        
        updates = []
        params = []
        
        if texto is not None:
            updates.append("texto = ?")
            params.append(texto)
        
        if ruta_audio is not None:
            updates.append("ruta_audio = ?")
            params.append(ruta_audio)
        
        params.append(id_boletin)
        
        cursor = self.connection.cursor()
        cursor.execute(
            f"UPDATE boletines SET {', '.join(updates)} WHERE id = ?",
            params
        )
        self.connection.commit()
        return cursor.rowcount > 0
    
    def buscar_boletines(self, termino: str, limite: int = 10) -> List[Tuple[int, str, str, str]]:
        """Busca boletines que contengan el término especificado."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, texto, ruta_audio, fecha_creacion FROM boletines WHERE texto LIKE ? ORDER BY fecha_creacion DESC LIMIT ?",
            (f"%{termino}%", limite)
        )
        return cursor.fetchall()
    
    def contar_boletines(self) -> int:
        """Cuenta el total de boletines en la base de datos."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM boletines")
        return cursor.fetchone()[0]
    
    def cerrar(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
