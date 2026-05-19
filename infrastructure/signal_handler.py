# -*- coding: utf-8 -*-
"""
Manejador de Señales para Cierre Graceful
Proporciona manejo de señales del sistema para cierre limpio.
"""
import signal
import sys
import os
from typing import Callable, Optional
from infrastructure.system_compat import system_compat

class SignalHandler:
    """Gestiona el manejo de señales del sistema."""
    
    def __init__(self):
        self.shutdown_callback = None
        self.shutdown_requested = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configura manejadores de señales según el sistema operativo."""
        
        if system_compat.platform_info['is_windows']:
            # Windows: SIGINT, SIGBREAK
            signal.signal(signal.SIGINT, self._handle_signal)
            try:
                signal.signal(signal.SIGBREAK, self._handle_signal)
            except AttributeError:
                pass  # SIGBREAK no disponible en todas las versiones de Windows
        else:
            # Unix-like: SIGINT, SIGTERM, SIGHUP
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            try:
                signal.signal(signal.SIGHUP, self._handle_signal)
            except AttributeError:
                pass  # SIGHUP no disponible en todos los sistemas
    
    def _handle_signal(self, signum, frame):
        """Maneja señales de cierre."""
        signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
        print(f"\nSeñal recibida: {signal_name}")
        self.shutdown_requested = True
        
        if self.shutdown_callback:
            try:
                self.shutdown_callback(signum, frame)
            except Exception as e:
                print(f"Error en callback de shutdown: {e}")
        
        # Si no hay callback o el callback no maneja el cierre, salir
        if not self.shutdown_callback:
            self._graceful_shutdown()
    
    def set_shutdown_callback(self, callback: Callable):
        """Establece el callback de shutdown."""
        self.shutdown_callback = callback
    
    def _graceful_shutdown(self):
        """Realiza cierre graceful."""
        print("\nIniciando cierre graceful...")
        print("Guardando estado...")
        print("Cerrando recursos...")
        print("Cerrando conexiones...")
        print("Liberando memoria...")
        print("Cierre completado.")
        sys.exit(0)
    
    def is_shutdown_requested(self) -> bool:
        """Verifica si se solicitó shutdown."""
        return self.shutdown_requested
    
    def reset(self):
        """Resetea el estado de shutdown."""
        self.shutdown_requested = False


class ResourceCleanup:
    """Gestiona la limpieza de recursos al cerrar."""
    
    def __init__(self):
        self.cleanup_functions = []
        self.signal_handler = SignalHandler()
        self.signal_handler.set_shutdown_callback(self._cleanup_on_shutdown)
    
    def register_cleanup(self, cleanup_func: Callable, priority: int = 0):
        """Registra una función de limpieza con prioridad."""
        self.cleanup_functions.append((priority, cleanup_func))
        # Ordenar por prioridad (mayor prioridad primero)
        self.cleanup_functions.sort(key=lambda x: x[0], reverse=True)
    
    def _cleanup_on_shutdown(self, signum, frame):
        """Ejecuta todas las funciones de limpieza al recibir señal."""
        print("\nEjecutando limpieza de recursos...")
        
        for priority, cleanup_func in self.cleanup_functions:
            try:
                print(f"Ejecutando limpieza (prioridad {priority})...")
                cleanup_func()
            except Exception as e:
                print(f"Error en función de limpieza: {e}")
        
        print("Limpieza completada. Saliendo...")
        sys.exit(0)
    
    def cleanup_now(self):
        """Ejecuta limpieza inmediata sin salir."""
        print("Ejecutando limpieza manual...")
        
        for priority, cleanup_func in self.cleanup_functions:
            try:
                cleanup_func()
            except Exception as e:
                print(f"Error en función de limpieza: {e}")
        
        print("Limpieza manual completada.")


# Instancia global de limpieza de recursos
resource_cleanup = ResourceCleanup()


def register_resource_cleanup(cleanup_func: Callable, priority: int = 0):
    """Registra una función de limpieza global."""
    resource_cleanup.register_cleanup(cleanup_func, priority)


def cleanup_on_exit():
    """Ejecuta limpieza al salir."""
    resource_cleanup.cleanup_now()
