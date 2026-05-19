# -*- coding: utf-8 -*-
"""
Fallbacks para UI cuando faltan dependencias
Proporciona alternativas cuando CustomTkinter no está disponible.
"""
import sys
from typing import Optional
from infrastructure.system_compat import system_compat

class UIFallback:
    """Gestiona fallbacks de UI cuando faltan dependencias."""
    
    def __init__(self):
        self.available_toolkits = self._detect_ui_toolkits()
        self.current_toolkit = self._select_best_toolkit()
    
    def _detect_ui_toolkits(self) -> list:
        """Detecta toolkits de UI disponibles."""
        toolkits = []
        
        # Detectar CustomTkinter
        try:
            import customtkinter
            toolkits.append('customtkinter')
        except ImportError:
            pass
        
        # Detectar Tkinter (built-in)
        try:
            import tkinter
            toolkits.append('tkinter')
        except ImportError:
            pass
        
        # Detectar PyQt5
        try:
            import PyQt5
            toolkits.append('pyqt5')
        except ImportError:
            pass
        
        # Detectar PyQt6
        try:
            import PyQt6
            toolkits.append('pyqt6')
        except ImportError:
            pass
        
        # Detectar PySide2
        try:
            import PySide2
            toolkits.append('pyside2')
        except ImportError:
            pass
        
        # Detectar PySide6
        try:
            import PySide6
            toolkits.append('pyside6')
        except ImportError:
            pass
        
        return toolkits
    
    def _select_best_toolkit(self) -> str:
        """Selecciona el mejor toolkit disponible."""
        priority = ['customtkinter', 'tkinter', 'pyqt5', 'pyqt6', 'pyside2', 'pyside6']
        
        for toolkit in priority:
            if toolkit in self.available_toolkits:
                return toolkit
        
        return None
    
    def get_ui_class(self):
        """Retorna la clase de UI apropiada."""
        if self.current_toolkit == 'customtkinter':
            return self._get_customtkinter_ui()
        elif self.current_toolkit == 'tkinter':
            return self._get_tkinter_ui()
        elif self.current_toolkit in ['pyqt5', 'pyqt6']:
            return self._get_pyqt_ui()
        elif self.current_toolkit in ['pyside2', 'pyside6']:
            return self._get_pyside_ui()
        else:
            return self._get_console_ui()
    
    def _get_customtkinter_ui(self):
        """Retorna UI con CustomTkinter."""
        from ui.main_window import VentanaTactica
        return VentanaTactica
    
    def _get_tkinter_ui(self):
        """Retorna UI fallback con Tkinter estándar."""
        import tkinter as tk
        from tkinter import messagebox, filedialog
        
        class VentanaTacticaFallback(tk.Tk):
            def __init__(self):
                super().__init__()
                self.title("S.M.A.C. - Modo Compatibilidad (Tkinter)")
                self.geometry("600x400")
                self._crear_interfaz()
            
            def _crear_interfaz(self):
                lbl = tk.Label(self, text="S.M.A.C. - Modo Compatibilidad", font=("Arial", 14, "bold"))
                lbl.pack(pady=20)
                
                lbl_info = tk.Label(
                    self,
                    text="CustomTkinter no está disponible.\nUsando Tkinter estándar como fallback.\n\nFuncionalidades limitadas.",
                    justify="center"
                )
                lbl_info.pack(pady=20)
                
                btn = tk.Button(self, text="Instalar CustomTkinter", command=self._mostrar_instrucciones)
                btn.pack(pady=10)
            
            def _mostrar_instrucciones(self):
                messagebox.showinfo(
                    "Instrucciones",
                    "Para obtener la experiencia completa:\n\n"
                    "pip install customtkinter==5.2.2"
                )
        
        return VentanaTacticaFallback
    
    def _get_pyqt_ui(self):
        """Retorna UI fallback con PyQt."""
        try:
            if self.current_toolkit == 'pyqt5':
                from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
            else:
                from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
            
            class VentanaTacticaPyQt(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("S.M.A.C. - Modo Compatibilidad (PyQt)")
                    self.setGeometry(100, 100, 600, 400)
                    self._crear_interfaz()
                
                def _crear_interfaz(self):
                    widget = QWidget()
                    layout = QVBoxLayout()
                    
                    lbl = QLabel("S.M.A.C. - Modo Compatibilidad")
                    lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
                    layout.addWidget(lbl)
                    
                    lbl_info = QLabel(
                        "CustomTkinter no está disponible.\n"
                        "Usando PyQt como fallback.\n\n"
                        "Funcionalidades limitadas."
                    )
                    layout.addWidget(lbl_info)
                    
                    btn = QPushButton("Instalar CustomTkinter")
                    btn.clicked.connect(self._mostrar_instrucciones)
                    layout.addWidget(btn)
                    
                    widget.setLayout(layout)
                    self.setCentralWidget(widget)
                
                def _mostrar_instrucciones(self):
                    QMessageBox.information(
                        self,
                        "Instrucciones",
                        "Para obtener la experiencia completa:\n\n"
                        "pip install customtkinter==5.2.2"
                    )
            
            return VentanaTacticaPyQt
        except Exception as e:
            print(f"Error inicializando PyQt: {e}")
            return self._get_console_ui()
    
    def _get_pyside_ui(self):
        """Retorna UI fallback con PySide."""
        try:
            if self.current_toolkit == 'pyside2':
                from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
            else:
                from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
            
            class VentanaTacticaPySide(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("S.M.A.C. - Modo Compatibilidad (PySide)")
                    self.setGeometry(100, 100, 600, 400)
                    self._crear_interfaz()
                
                def _crear_interfaz(self):
                    widget = QWidget()
                    layout = QVBoxLayout()
                    
                    lbl = QLabel("S.M.A.C. - Modo Compatibilidad")
                    lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
                    layout.addWidget(lbl)
                    
                    lbl_info = QLabel(
                        "CustomTkinter no está disponible.\n"
                        "Usando PySide como fallback.\n\n"
                        "Funcionalidades limitadas."
                    )
                    layout.addWidget(lbl_info)
                    
                    btn = QPushButton("Instalar CustomTkinter")
                    btn.clicked.connect(self._mostrar_instrucciones)
                    layout.addWidget(btn)
                    
                    widget.setLayout(layout)
                    self.setCentralWidget(widget)
                
                def _mostrar_instrucciones(self):
                    QMessageBox.information(
                        self,
                        "Instrucciones",
                        "Para obtener la experiencia completa:\n\n"
                        "pip install customtkinter==5.2.2"
                    )
            
            return VentanaTacticaPySide
        except Exception as e:
            print(f"Error inicializando PySide: {e}")
            return self._get_console_ui()
    
    def _get_console_ui(self):
        """Retorna UI de consola como último fallback."""
        class ConsoleUI:
            def __init__(self):
                self.running = True
            
            def mainloop(self):
                print("\n" + "="*50)
                print("S.M.A.C. - Estación de Control Operacional")
                print("Modo Consola (Sin GUI disponible)")
                print("="*50 + "\n")
                
                print("Advertencia: No se detectaron toolkits de GUI.")
                print("Para la experiencia completa, instale:")
                print("  pip install customtkinter==5.2.2")
                print("\nOpciones disponibles:")
                print("  1. Ver reporte de compatibilidad")
                print("  2. Salir")
                
                while self.running:
                    try:
                        opcion = input("\nSeleccione una opción (1-2): ")
                        
                        if opcion == '1':
                            from infrastructure.system_compat import system_compat
                            print(system_compat.get_system_report())
                        elif opcion == '2':
                            print("Saliendo...")
                            self.running = False
                        else:
                            print("Opción inválida.")
                    except KeyboardInterrupt:
                        print("\nSaliendo...")
                        self.running = False
                    except Exception as e:
                        print(f"Error: {e}")
        
            def destroy(self):
                self.running = False
        
        return ConsoleUI


def check_ui_dependencies() -> tuple:
    """Verifica dependencias de UI y retorna (disponible, toolkit, advertencias)."""
    warnings = []
    
    ui_fallback = UIFallback()
    
    if not ui_fallback.available_toolkits:
        warnings.append("No se detectaron toolkits de GUI disponibles.")
        warnings.append("El sistema funcionará en modo consola.")
        return (False, None, warnings)
    
    if 'customtkinter' not in ui_fallback.available_toolkits:
        warnings.append("CustomTkinter no está instalado.")
        warnings.append("Usando fallback: " + ui_fallback.current_toolkit)
        warnings.append("Para la experiencia completa: pip install customtkinter==5.2.2")
        return (True, ui_fallback.current_toolkit, warnings)
    
    return (True, 'customtkinter', [])
