# -*- coding: utf-8 -*-
import os
import sys

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.system_checker import system_checker
from infrastructure.ui_fallback import UIFallback, check_ui_dependencies
from infrastructure.signal_handler import resource_cleanup, register_resource_cleanup

def main():
    """Función principal con fallbacks y verificación de compatibilidad."""
    
    print("\n" + "="*60)
    print("S.M.A.C. - Estación de Control Operacional")
    print("Iniciando sistema con verificación de compatibilidad...")
    print("="*60 + "\n")
    
    # Ejecutar verificación del sistema
    print("Verificando compatibilidad del sistema...")
    results = system_checker.run_all_checks()
    
    # Mostrar reporte si hay advertencias o errores
    if results['overall_status'] in ['warning', 'critical']:
        print(system_checker.generate_report(results))
        
        if results['overall_status'] == 'critical':
            print("\n❌ El sistema tiene fallas críticas.")
            print("Por favor, instale las dependencias faltantes:")
            for cmd in system_checker.get_installation_commands():
                print(f"  {cmd}")
            input("\nPresione Enter para salir...")
            sys.exit(1)
    else:
        print("✅ Sistema compatible.")
    
    # Verificar UI
    print("\nVerificando interfaz gráfica...")
    ui_available, ui_toolkit, ui_warnings = check_ui_dependencies()
    
    if not ui_available:
        print("⚠️ CustomTkinter no disponible. Usando fallback.")
        for warning in ui_warnings:
            print(f"  {warning}")
    
    # Crear archivo dummy si no existe
    if not os.path.exists("cortina_base.mp3"):
        print("Creando archivo de audio placeholder...")
        with open("cortina_base.mp3", "wb") as f:
            f.write(b'\x00' * 1000)
    
    # Registrar limpieza de recursos
    def cleanup_resources():
        print("Limpiando recursos...")
    
    register_resource_cleanup(cleanup_resources, priority=10)
    
    # Iniciar aplicación con fallbacks
    print("\nIniciando aplicación...")
    
    try:
        if ui_available and ui_toolkit == 'customtkinter':
            from ui.main_window import VentanaTactica
            app = VentanaTactica()
        else:
            ui_fallback = UIFallback()
            UI_Class = ui_fallback.get_ui_class()
            app = UI_Class()
        
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n\nInterrupción del usuario. Cerrando...")
        resource_cleanup.cleanup_now()
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")
        print("\nPara diagnóstico, ejecute con verificación detallada:")
        print("  python -c \"from infrastructure.system_checker import system_checker; print(system_checker.generate_report())\"")
        resource_cleanup.cleanup_now()
        input("\nPresione Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()
