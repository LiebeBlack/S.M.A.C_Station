# -*- coding: utf-8 -*-
"""
Script de Compilación Automatizado para S.M.A.C. Broadcast System
Detecta dependencias dinámicamente, instala componentes físicos y empaqueta.
"""
import os
import sys
import subprocess
import shutil

def log_msg(texto, symbol="[*]"):
    print(f"\n{symbol} {texto}")

def compilar():
    log_msg("=== S.M.A.C. COMPILADOR AUTOMÁTICO DE ALTO RENDIMIENTO ===", "🎙️")

    # 1. Verificar si PyInstaller está instalado
    try:
        import PyInstaller
        log_msg("PyInstaller detectado con éxito.", "✅")
    except ImportError:
        log_msg("PyInstaller NO está instalado en este entorno de Python.", "⚠️")
        log_msg("Instalando PyInstaller de forma segura...", "⚙️")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            log_msg("PyInstaller instalado correctamente.", "✅")
        except Exception as e:
            log_msg(f"Fallo al instalar PyInstaller: {e}", "❌")
            return

    # 2. Localizar dinámicamente la ruta de customtkinter
    try:
        import customtkinter
        ctk_dir = os.path.dirname(customtkinter.__file__)
        log_msg(f"CustomTkinter detectado en: {ctk_dir}", "✅")
    except ImportError:
        log_msg("CustomTkinter no está instalado en este entorno.", "❌")
        log_msg("Por favor, instala los requisitos primero: pip install -r requisitos.txt", "💡")
        return

    # 3. Instalar y verificar 'tbb' para reparar físicamente 'tbb12.dll'
    try:
        import tbb
        log_msg("Intel TBB detectado con éxito.", "✅")
    except ImportError:
        log_msg("Intel TBB no está instalado. Resolviendo tbb12.dll físicamente...", "⚙️")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "tbb"], check=True)
            log_msg("Intel TBB instalado correctamente.", "✅")
        except Exception as e:
            log_msg(f"Fallo al instalar TBB: {e}", "❌")

    # 4. Instalar y verificar 'imageio-ffmpeg' para reparar físicamente FFmpeg
    try:
        import imageio_ffmpeg
        log_msg("Controlador FFmpeg estático detectado con éxito.", "✅")
    except ImportError:
        log_msg("Controlador FFmpeg no está instalado. Resolviendo FFmpeg físicamente...", "⚙️")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"], check=True)
            log_msg("Controlador FFmpeg instalado correctamente.", "✅")
        except Exception as e:
            log_msg(f"Fallo al instalar imageio-ffmpeg: {e}", "❌")

    # 5. Asegurar que exista la base de datos en la raíz
    db_file = "smac_station.db"
    if not os.path.exists(db_file):
        log_msg(f"Creando base de datos vacía {db_file} para incluir en el compilado...", "💾")
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            conn.execute("CREATE TABLE IF NOT EXISTS configuraciones (clave TEXT PRIMARY KEY, valor TEXT)")
            conn.commit()
            conn.close()
            log_msg("Base de datos local creada con éxito.", "✅")
        except Exception as e:
            log_msg(f"No se pudo crear la base de datos preliminar: {e}", "⚠️")

    # 6. Construir comando de PyInstaller (¡Modo Real Multi-archivo!)
    log_msg("Construyendo comando de compilación robusto con assets dinámicos...", "🛠️")
    
    script_principal = "main.py"
    nombre_app = "SMAC_Broadcast_Station"
    
    # Argumentos base
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",    # Compilación multi-archivo (directorio completo, inicio ultra-rápido)
        "--windowed",  # Oculta la terminal detrás del programa (modo GUI nativo)
        f"--name={nombre_app}",
        # Importaciones ocultas críticas para que carguen los backends dinámicos
        "--hidden-import=customtkinter",
        "--hidden-import=psutil",
        "--hidden-import=sounddevice",
        "--hidden-import=soundfile",
        "--hidden-import=librosa",
        "--hidden-import=pygame",
        "--hidden-import=gtts",
        "--hidden-import=pydub",
        "--hidden-import=sqlite3",
    ]

    # Agregar carpeta de CustomTkinter a los datos empaquetados
    args.append(f'--add-data={ctk_dir};customtkinter')
    
    if os.path.exists(db_file):
        args.append(f'--add-data={db_file};.')
        
    if os.path.exists("config.py"):
        args.append(f'--add-data=config.py;.')

    args.append(script_principal)

    log_msg("Comando generado para ejecución de empaquetado:", "💬")
    print(" ".join(args))

    # 7. Ejecutar PyInstaller
    log_msg("Iniciando compilación (esto puede tomar 1 o 2 minutos)...", "🚀")
    try:
        subprocess.run(args, check=True)
        
        dst_dir = os.path.abspath(f"dist/{nombre_app}")
        
        # A. RESOLVER FÍSICAMENTE 'python314.dll'
        try:
            dll_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
            src_dll = os.path.join(sys.base_prefix, dll_name)
            dst_dll = os.path.join(dst_dir, dll_name)
            
            if os.path.exists(src_dll) and os.path.exists(dst_dir):
                if not os.path.exists(dst_dll):
                    log_msg(f"Físicamente reparado: Copiando {dll_name} al directorio de salida...", "⚙️")
                    shutil.copy2(src_dll, dst_dll)
                    log_msg("DLL de Python copiado con éxito.", "✅")
            else:
                src_sys32 = os.path.join("C:\\Windows\\System32", dll_name)
                if os.path.exists(src_sys32) and os.path.exists(dst_dir) and not os.path.exists(dst_dll):
                    log_msg(f"Físicamente reparado: Copiando {dll_name} desde System32...", "⚙️")
                    shutil.copy2(src_sys32, dst_dll)
                    log_msg("DLL de Python copiado con éxito.", "✅")
        except Exception as dll_err:
            log_msg(f"Aviso en verificación de Python DLL: {dll_err}", "⚠️")

        # B. RESOLVER FÍSICAMENTE 'tbb12.dll'
        try:
            tbb_dll_found = False
            
            # Buscar directamente en el sistema de archivos (sys.path) para evitar cacheo de importaciones
            for path in sys.path:
                tbb_dir = os.path.join(path, "tbb")
                if os.path.exists(tbb_dir) and os.path.isdir(tbb_dir):
                    for root, dirs, files in os.walk(tbb_dir):
                        if "tbb12.dll" in files:
                            src_tbb = os.path.join(root, "tbb12.dll")
                            dst_tbb = os.path.join(dst_dir, "tbb12.dll")
                            shutil.copy2(src_tbb, dst_tbb)
                            log_msg(f"Físicamente reparado: tbb12.dll copiado desde {src_tbb}", "✅")
                            tbb_dll_found = True
                            break
                if tbb_dll_found:
                    break
            
            # Plan de respaldo: Importar recargando caché si no se halló por disco
            if not tbb_dll_found:
                try:
                    import importlib
                    importlib.invalidate_caches()
                    import tbb
                    tbb_base = os.path.dirname(tbb.__file__)
                    for root, dirs, files in os.walk(tbb_base):
                        if "tbb12.dll" in files:
                            src_tbb = os.path.join(root, "tbb12.dll")
                            dst_tbb = os.path.join(dst_dir, "tbb12.dll")
                            shutil.copy2(src_tbb, dst_tbb)
                            log_msg(f"Físicamente reparado (vía import): tbb12.dll copiado desde {src_tbb}", "✅")
                            tbb_dll_found = True
                            break
                except ImportError:
                    pass
            
            if not tbb_dll_found:
                log_msg("No se localizó tbb12.dll en la carpeta del módulo 'tbb' ni en el sistema.", "⚠️")
        except Exception as tbb_err:
            log_msg(f"No se pudo resolver físicamente tbb12.dll: {tbb_err}", "⚠️")

        # C. RESOLVER FÍSICAMENTE 'ffmpeg.exe' y 'ffprobe.exe'
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if os.path.exists(ffmpeg_exe):
                # Copiar a la raíz para ejecución de desarrollo
                shutil.copy2(ffmpeg_exe, os.path.join(os.getcwd(), "ffmpeg.exe"))
                # Copiar al dist para producción
                shutil.copy2(ffmpeg_exe, os.path.join(dst_dir, "ffmpeg.exe"))
                
                # También resolver ffprobe.exe (suele estar al lado de ffmpeg en imageio-ffmpeg)
                ffmpeg_dir = os.path.dirname(ffmpeg_exe)
                ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
                if not os.path.exists(ffprobe_exe):
                    # Si no existe, buscamos archivos .exe en ese directorio
                    for f in os.listdir(ffmpeg_dir):
                        if f.startswith("ffprobe") and f.endswith(".exe"):
                            ffprobe_exe = os.path.join(ffmpeg_dir, f)
                            break
                
                if os.path.exists(ffprobe_exe):
                    shutil.copy2(ffprobe_exe, os.path.join(os.getcwd(), "ffprobe.exe"))
                    shutil.copy2(ffprobe_exe, os.path.join(dst_dir, "ffprobe.exe"))
                
                log_msg("Físicamente reparado: FFmpeg y FFprobe binarios estáticos copiados a raíz y dist/", "✅")
        except Exception as ffmpeg_err:
            log_msg(f"No se pudo resolver físicamente FFmpeg: {ffmpeg_err}", "⚠️")

        log_msg("===================================================", "🎉")
        log_msg("¡COMPILACIÓN COMPLETADA EXITOSAMENTE!", "🏆")
        log_msg(f"Tu ejecutable autónomo está listo en:", "📁")
        ruta_dist = os.path.abspath(f"dist/{nombre_app}/{nombre_app}.exe")
        print(f"👉 {ruta_dist}")
        log_msg("Puedes distribuir la carpeta completa de dist/ para usar en cualquier PC.", "💡")
        log_msg("===================================================", "🎉")
    except subprocess.CalledProcessError as e:
        log_msg(f"Fallo durante la ejecución de PyInstaller: {e}", "❌")
    except Exception as e:
        log_msg(f"Error inesperado al compilar: {e}", "❌")

if __name__ == "__main__":
    compilar()
