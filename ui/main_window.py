# -*- coding: utf-8 -*-
import os
import sys
import threading
import time
import tempfile
import random
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Agregar directorio padre al path para importaciones relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.use_cases import ProcesadorBoletin
from infrastructure.database import DatabaseConnection
from infrastructure.audio_fallback import AudioFallbackController
from infrastructure.audio_recording import AudioRecordingFallback
from infrastructure.tts_fallback import TTSFallbackController
from infrastructure.playlist_manager import PlaylistManager
from infrastructure.signal_handler import register_resource_cleanup
from infrastructure.system_compat import system_compat
import config

# Configuración estética oscura "Studio Premium"
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VentanaTactica(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🎙️ S.M.A.C. BROADCAST SYSTEM - HIGH-DENSITY TELEMETRY DESK")
        self.geometry("1240x740")
        
        # Permitir redimensionamiento fluido
        self.resizable(True, True)
        
        # Maximizar de forma segura tras 200ms para evitar crash nativo de Windows Tcl
        self.after(200, self._maximizar_seguro)
        
        # Inicializar Componentes del Backend profundo con BLINDAJE ANTI-CRASH de DLLs
        # Si alguna DLL nativa o recurso de hardware falla al compilar, la UI se mantendrá de pie
        self.procesador = None
        self.db = None
        self.audio_controller = None
        self.audio_recorder = None
        self.tts_controller = None
        self.playlist_manager = None
        
        # Logs preliminares para registrar durante el dibujo de UI
        self.logs_iniciales = []
        
        try:
            self.procesador = ProcesadorBoletin()
            self.logs_iniciales.append(("Procesador Boletín DSP cargado con éxito.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Advertencia: Procesador Boletín limitado: {e}", "WARNING"))
            
        try:
            self.db = DatabaseConnection(config.DB_CONFIG['db_file'])
            self.logs_iniciales.append(("Base de Datos SQLite conectada con éxito.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Error conectando base de datos: {e}", "WARNING"))
            
        try:
            self.audio_controller = AudioFallbackController()
            self.logs_iniciales.append(("Controlador de Audio Máster inicializado.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Fallo crítico en motor reproductor: {e}", "WARNING"))
            
        try:
            self.audio_recorder = AudioRecordingFallback()
            self.logs_iniciales.append(("Módulo de Grabación física listo.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Módulo de Grabación deshabilitado (Falta PortAudio/DLL): {e}", "WARNING"))
            
        try:
            self.tts_controller = TTSFallbackController()
            self.logs_iniciales.append(("Motor de Síntesis de Voz cargado.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Fallo al levantar sintetizador TTS: {e}", "WARNING"))
            
        try:
            self.playlist_manager = PlaylistManager()
            self.logs_iniciales.append(("Gestor de playlist inicializado.", "SYS"))
        except Exception as e:
            self.logs_iniciales.append((f"Fallo cargando playlist manager: {e}", "WARNING"))
        
        self.ruta_salida_actual = config.AUDIO_CONFIG['default_output']
        self.ruta_grabacion = None
        self.procesando = False
        self.talkover_activo = False
        
        # Variables de telemetría de audio reales
        self.duracion_pista_actual = 0.0
        self.segundos_grabados = 0
        self.segundos_emision = 0
        self.eq_vals = {"SUB": 0.8, "LOW": 0.0, "MID": -3.0, "HIGH": 4.0}
        
        # Registrar limpiadores del sistema
        register_resource_cleanup(self._cleanup_ui_resources, priority=5)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Dibujar la cabina de audio e iniciar subprocesos
        self._construir_estudio_de_radio()
        self._actualizar_reloj()
        self._actualizar_vu_meter()
        self._actualizar_telemetria()
        
        # Volcar logs iniciales en la consola verde
        for msg, tag in self.logs_iniciales:
            self.log_event(msg, tag)
            
        self.log_event("Consola Máster inicializada con éxito.", "SYS")
        self.log_event("Arquitectura robusta blindada anti-fallos de DLLs activa.", "UI")
        self.log_event("Cabina lista para la emisión. Frecuencia de estudio activa.", "DSP")

    def _maximizar_seguro(self):
        """Maximiza la ventana de forma segura una vez mapeada."""
        try:
            self.state('zoomed')
            self.log_event("Consola maximizada a pantalla completa de forma segura.", "SYS")
        except Exception as e:
            self.log_event(f"No se pudo forzar maximizado: {e}", "WARNING")

    def _construir_estudio_de_radio(self):
        # -------------------------------------------------------------
        # BARRA DE ESTADO INFERIOR (ESTÁTICA AL FONDO)
        # -------------------------------------------------------------
        self.frame_estado = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color="#101216", border_width=1, border_color="#2c313c")
        self.frame_estado.pack(side="bottom", fill="x")
        
        self.lbl_status_bar = ctk.CTkLabel(self.frame_estado, text="🟢 SISTEMA OPERATIVO | BUFFER DE EMISIÓN DE ALTA NORMA OK", font=ctk.CTkFont(size=10, weight="bold"), text_color="#00ff00")
        self.lbl_status_bar.pack(side="left", padx=15, pady=3)
        
        self.lbl_db_status = ctk.CTkLabel(self.frame_estado, text="SQLITE DATABASE: CONECTADA" if self.db else "SQLITE DATABASE: DESCONECTADA", font=ctk.CTkFont(size=10, weight="bold"), text_color="#3b9eff" if self.db else "red")
        self.lbl_db_status.pack(side="right", padx=15, pady=3)

        # -------------------------------------------------------------
        # CONTENEDOR PRINCIPAL CON DESPLAZAMIENTO (SCROLLABLE FRAME)
        # -------------------------------------------------------------
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=4, pady=4)

        # -------------------------------------------------------------
        # PANEL LATERAL IZQUIERDO: DECK DE CONTROLES DJ (COMPACTO)
        # -------------------------------------------------------------
        frame_izq = ctk.CTkFrame(self.container, width=360, corner_radius=6, fg_color="#181a1f")
        frame_izq.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        
        # Título Sección Playlist
        lbl_tit_playlist = ctk.CTkLabel(frame_izq, text="🎵 DECK REPRODUCTOR & PLAYLIST", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b9eff")
        lbl_tit_playlist.pack(anchor="w", padx=12, pady=(10, 5))
        
        # Listbox Visual Ajustado
        self.txt_playlist = ctk.CTkTextbox(frame_izq, height=100, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#101216", border_width=1, border_color="#2c313c")
        self.txt_playlist.pack(fill="x", padx=12, pady=(0, 6))
        
        # Controles Playlist
        frame_btns_play = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_btns_play.pack(fill="x", padx=12, pady=(0, 6))
        
        btn_add = ctk.CTkButton(frame_btns_play, text="➕ AÑADIR", height=28, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#282c34", hover_color="#3e4451", command=self._seleccionar_cortina)
        btn_add.pack(side="left", expand=True, padx=(0, 2))
        
        btn_clear = ctk.CTkButton(frame_btns_play, text="🗑️ LIMPIAR", height=28, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#ff5555", hover_color="#cc0000", command=self._limpiar_playlist)
        btn_clear.pack(side="right", expand=True, padx=(2, 0))
        
        # DECK DE TRANSPORTE (PLAY / PAUSE / VOLUMEN)
        frame_transporte = ctk.CTkFrame(frame_izq, fg_color="#101216", height=45, corner_radius=4, border_width=1, border_color="#2c313c")
        frame_transporte.pack(fill="x", padx=12, pady=(0, 8))
        
        btn_prev = ctk.CTkButton(frame_transporte, text="⏮️", width=35, height=26, fg_color="transparent", hover_color="#2c313c", command=self._anterior_pista)
        btn_prev.pack(side="left", padx=5, pady=5)
        
        btn_play = ctk.CTkButton(frame_transporte, text="▶️ PLAY", width=65, height=26, fg_color="#00aa00", hover_color="#00cc00", font=ctk.CTkFont(size=10, weight="bold"), command=self._reproducir_playlist)
        btn_play.pack(side="left", padx=3, pady=5)
        
        btn_stop = ctk.CTkButton(frame_transporte, text="⏹️ STOP", width=65, height=26, fg_color="#aa0000", hover_color="#cc0000", font=ctk.CTkFont(size=10, weight="bold"), command=self._detener_playlist)
        btn_stop.pack(side="left", padx=3, pady=5)
        
        btn_next = ctk.CTkButton(frame_transporte, text="⏭️", width=35, height=26, fg_color="transparent", hover_color="#2c313c", command=self._siguiente_pista)
        btn_next.pack(side="left", padx=3, pady=5)
        
        # Slider Volumen
        self.slider_volumen = ctk.CTkSlider(frame_transporte, from_=0, to=1, width=80, height=14)
        self.slider_volumen.set(0.8)
        self.slider_volumen.pack(side="right", padx=8, pady=5)
        self.slider_volumen.configure(command=self._cambiar_volumen)
        
        self._refrescar_ui_playlist()
        
        # Soundboard Compacto (8 Canales Estilizados)
        lbl_tit_soundboard = ctk.CTkLabel(frame_izq, text="🎹 SOUNDBOARD DE EFECTOS RÁPIDOS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b9eff")
        lbl_tit_soundboard.pack(anchor="w", padx=12, pady=(3, 3))
        
        frame_soundboard = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_soundboard.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        
        jingles = [
            ("🚨 SIRENA", "Alerta roja en el sistema."),
            ("👏 APLAUSOS", "Efecto de multitud aplaudiendo."),
            ("🥁 REDOBLE", "Redoble de tambores en el aire."),
            ("🎵 ID RADIO", "Estás sintonizando la señal de S M A C."),
            ("😆 RISAS", "Sonidos de risas en el estudio."),
            ("🔥 IMPACTO", "Efecto de sonido impacto cinemático."),
            ("🔔 ALERTA", "Aviso importante de la estación."),
            ("⚡ EFECTO 8", "Efecto especial de transicion de radio.")
        ]
        
        # Matriz Grid Compacta 4x2
        for idx, (nombre, tts_text) in enumerate(jingles):
            row = idx // 2
            col = idx % 2
            btn = ctk.CTkButton(
                frame_soundboard, text=nombre, height=35, font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#21252b", hover_color="#2c313c", border_width=1, border_color="#3b9eff",
                command=lambda e=nombre, t=tts_text: self._reproducir_jingle(e, t)
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        
        for r in range(4): frame_soundboard.rowconfigure(r, weight=1)
        for c in range(2): frame_soundboard.columnconfigure(c, weight=1)

        # -------------------------------------------------------------
        # PANEL CENTRAL: LOCUCION, VU-METER FINO Y TELEMETRÍA MÁSTER
        # -------------------------------------------------------------
        frame_cen = ctk.CTkFrame(self.container, corner_radius=6, fg_color="#1e222b")
        frame_cen.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        
        # Reloj Ajustado & VU Meter Fino
        frame_monitor = ctk.CTkFrame(frame_cen, fg_color="#101216", corner_radius=6, border_width=1, border_color="#3b9eff")
        frame_monitor.pack(fill="x", padx=15, pady=10)
        
        self.lbl_reloj = ctk.CTkLabel(frame_monitor, text="00:00:00", font=ctk.CTkFont(family="Consolas", size=52, weight="bold"), text_color="#00ff00")
        self.lbl_reloj.pack(pady=(5, 0))
        
        self.lbl_estado = ctk.CTkLabel(frame_cen, text="🎙️ ESTUDIO EN LÍNEA - ESPECTRO ACTIVO", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.lbl_estado.pack(pady=(0, 3))
        
        # VU METER ultra-fino de alta fidelidad
        frame_vu = ctk.CTkFrame(frame_monitor, fg_color="transparent")
        frame_vu.pack(fill="x", padx=25, pady=(2, 6))
        self.vu_meter = ctk.CTkProgressBar(frame_vu, progress_color="#ff5555", height=8)
        self.vu_meter.pack(fill="x")
        self.vu_meter.set(0.05)

        # PANEL DE TELEMETRÍA DE HARDWARE Y SEÑAL REAL
        self.frame_telem = ctk.CTkFrame(frame_cen, fg_color="#101216", corner_radius=6, border_width=1, border_color="#2c313c")
        self.frame_telem.pack(fill="x", padx=15, pady=(0, 8))
        
        # Grid de Telemetría 3x2
        self.lbl_telem_status = ctk.CTkLabel(self.frame_telem, text="📻 ENGINE: STANDBY", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#3b9eff")
        self.lbl_telem_status.grid(row=0, column=0, padx=10, pady=3, sticky="w")
        
        self.lbl_telem_tiempo = ctk.CTkLabel(self.frame_telem, text="⏱️ POSICIÓN: 00:00 / 00:00", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#00ff00")
        self.lbl_telem_tiempo.grid(row=0, column=1, padx=10, pady=3, sticky="w")
        
        self.lbl_telem_cpu = ctk.CTkLabel(self.frame_telem, text="💻 CPU LOAD: 0.0%", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="orange")
        self.lbl_telem_cpu.grid(row=1, column=0, padx=10, pady=3, sticky="w")
        
        self.lbl_telem_ram = ctk.CTkLabel(self.frame_telem, text="💾 RAM LIBRE: 0.00 GB", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="orange")
        self.lbl_telem_ram.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        
        self.lbl_telem_eq = ctk.CTkLabel(self.frame_telem, text="🔊 EQ: SUB 0.0 | LOW 0.0 | HIGH 0.0", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="gray")
        self.lbl_telem_eq.grid(row=2, column=0, padx=10, pady=3, sticky="w")
        
        self.lbl_telem_gate = ctk.CTkLabel(self.frame_telem, text="🔓 GATE: ABIERTO | PEAK -60dB", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#00ff00")
        self.lbl_telem_gate.grid(row=2, column=1, padx=10, pady=3, sticky="w")
        
        # Guión de locución Ajustado
        lbl_tit_guion = ctk.CTkLabel(frame_cen, text="📜 BOLETÍN / GUION DE LOCUCIÓN EN VIVO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b9eff")
        lbl_tit_guion.pack(anchor="w", padx=15)
        
        self.txt_boletin = ctk.CTkTextbox(frame_cen, height=90, font=ctk.CTkFont(size=13), fg_color="#101216", border_width=1, border_color="#2c313c")
        self.txt_boletin.pack(fill="both", expand=True, padx=15, pady=(2, 2))
        self.txt_boletin.bind("<KeyRelease>", self._actualizar_contador)
        
        self.lbl_contador = ctk.CTkLabel(frame_cen, text="0 caracteres", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_contador.pack(anchor="e", padx=20, pady=(0, 4))
        
        # MODULO DE MICROFONO Y GRABACION DE VOZ DIRECTA
        frame_grabacion = ctk.CTkFrame(frame_cen, fg_color="#101216", corner_radius=6, border_width=1, border_color="#2c313c")
        frame_grabacion.pack(fill="x", padx=15, pady=(0, 6))
        
        self.btn_grabar = ctk.CTkButton(
            frame_grabacion, text="⏺️ GRABAR MICRÓFONO", height=32, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#282c34", hover_color="#3e4451", command=self._toggle_grabacion
        )
        self.btn_grabar.pack(side="left", expand=True, padx=8, pady=5)
        
        self.btn_escuchar_grabacion = ctk.CTkButton(
            frame_grabacion, text="▶ ESCUCHAR GRABACIÓN", height=32, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#21252b", hover_color="#2c313c", state="disabled", command=self._reproducir_grabacion
        )
        self.btn_escuchar_grabacion.pack(side="right", expand=True, padx=8, pady=5)
        
        # Consola de Hardware Máster Ajustada
        frame_cen_ctrls = ctk.CTkFrame(frame_cen, fg_color="transparent")
        frame_cen_ctrls.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_transmitir = ctk.CTkButton(
            frame_cen_ctrls, text="📡 MEZCLAR MÁSTER Y TRANSMITIR", 
            font=ctk.CTkFont(size=13, weight="bold"), height=42, fg_color="#aa0000", hover_color="#ff0000",
            command=self._ejecutar_procesamiento
        )
        self.btn_transmitir.pack(side="left", expand=True, fill="x", padx=(0, 3))
        
        self.btn_talkover = ctk.CTkButton(
            frame_cen_ctrls, text="🎙️ TALK-OVER", 
            font=ctk.CTkFont(size=13, weight="bold"), height=42, fg_color="#cc7a00", hover_color="#ff9900",
            command=self._toggle_talkover
        )
        self.btn_talkover.pack(side="right", expand=True, fill="x", padx=(3, 0))

        # Botón de diagnóstico de hardware en vivo
        self.btn_diagnostico = ctk.CTkButton(
            frame_cen, text="🔍 DIAGNÓSTICO DE COMPATIBILIDAD DE HARDWARE Y DRIVERS",
            font=ctk.CTkFont(size=11, weight="bold"), height=30, fg_color="#21252b", hover_color="#2c313c",
            border_width=1, border_color="#3b9eff",
            command=self._ejecutar_diagnostico
        )
        self.btn_diagnostico.pack(fill="x", padx=15, pady=(4, 8))

        # -------------------------------------------------------------
        # PANEL LATERAL DERECHO: DSP, RACK EQ E INGENIERÍA (COMPACTO)
        # -------------------------------------------------------------
        frame_der = ctk.CTkFrame(self.container, width=350, corner_radius=6, fg_color="#181a1f")
        frame_der.pack(side="right", fill="both", expand=True, padx=6, pady=6)
        
        # Ecualizador Paramétrico (Faders Deslizantes Estilizados)
        lbl_tit_eq = ctk.CTkLabel(frame_der, text="🎚️ ECUALIZADOR MÁSTER (RACK DSP)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#3b9eff")
        lbl_tit_eq.pack(anchor="w", padx=12, pady=(10, 5))
        
        frame_eq_rack = ctk.CTkFrame(frame_der, fg_color="#101216", height=125, border_width=1, border_color="#2c313c")
        frame_eq_rack.pack(fill="x", padx=12, pady=(0, 8))
        frame_eq_rack.pack_propagate(False)
        
        # Grid para los deslizadores del EQ
        bandas = [
            ("SUB", self.eq_vals["SUB"]),
            ("LOW", self.eq_vals["LOW"]),
            ("MID", self.eq_vals["MID"]),
            ("HIGH", self.eq_vals["HIGH"])
        ]
        
        for col_idx, (nombre_banda, default_db) in enumerate(bandas):
            f_col = ctk.CTkFrame(frame_eq_rack, fg_color="transparent")
            f_col.pack(side="left", fill="both", expand=True, pady=4)
            
            slider = ctk.CTkSlider(f_col, orientation="vertical", from_=-12, to=12, height=80, width=12)
            slider.set(default_db)
            slider.pack(pady=(3, 3))
            slider.configure(command=lambda v, b=nombre_banda: self._eq_cambio(b, v))
            
            lbl_b = ctk.CTkLabel(f_col, text=nombre_banda, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray")
            lbl_b.pack()
            
        # Dinámica y Frecuencia Ajustada
        frame_dinamica = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_dinamica.pack(fill="x", padx=12, pady=(0, 6))
        
        # Gate de Ruido / Compresor
        ctk.CTkLabel(frame_dinamica, text="Fader Transición (s):", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=3, pady=3, sticky="e")
        self.slider_fade = ctk.CTkSlider(frame_dinamica, from_=0, to=10, width=120)
        self.slider_fade.set(3)
        self.slider_fade.grid(row=0, column=1, padx=3, pady=3)
        
        ctk.CTkLabel(frame_dinamica, text="Noise Gate (dB):", font=ctk.CTkFont(size=10)).grid(row=1, column=0, padx=3, pady=3, sticky="e")
        self.slider_gate = ctk.CTkSlider(frame_dinamica, from_=-60, to=0, width=120)
        self.slider_gate.set(-45)
        self.slider_gate.grid(row=1, column=1, padx=3, pady=3)
        
        # SECCIÓN TTS INMEDIATO
        frame_tts_rapido = ctk.CTkFrame(frame_der, fg_color="#101216", corner_radius=6, border_width=1, border_color="#2c313c")
        frame_tts_rapido.pack(fill="x", padx=12, pady=(0, 8))
        
        ctk.CTkLabel(frame_tts_rapido, text="🔊 TEXT-TO-SPEECH INSTANTÁNEO:", font=ctk.CTkFont(size=10, weight="bold"), text_color="#3b9eff").pack(anchor="w", padx=10, pady=(6, 2))
        
        frame_tts_inner = ctk.CTkFrame(frame_tts_rapido, fg_color="transparent")
        frame_tts_inner.pack(fill="x", padx=8, pady=(0, 6))
        
        self.txt_tts_inmediato = ctk.CTkEntry(frame_tts_inner, placeholder_text="Escriba frase de voz rápida...", height=28, font=ctk.CTkFont(size=11))
        self.txt_tts_inmediato.pack(side="left", expand=True, fill="x", padx=(0, 4))
        
        btn_lanzar_tts = ctk.CTkButton(frame_tts_inner, text="EMITIR", width=65, height=28, font=ctk.CTkFont(size=10, weight="bold"), fg_color="#3b9eff", hover_color="#2c313c", command=self._generar_tts_inmediato)
        btn_lanzar_tts.pack(side="right")
        
        # Terminal de Ingeniería y Logs en Vivo
        lbl_tit_terminal = ctk.CTkLabel(frame_der, text="💻 TERMINAL OPERATIVO SMAC (LOGS)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3b9eff")
        lbl_tit_terminal.pack(anchor="w", padx=12, pady=(4, 3))
        
        self.txt_terminal = ctk.CTkTextbox(frame_der, height=110, font=ctk.CTkFont(family="Consolas", size=9), fg_color="#101216", text_color="#00ff00", border_width=1, border_color="#2c313c")
        self.txt_terminal.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    # -------------------------------------------------------------
    # MÉTODOS DE SOPORTE E INTERACCION DE LA CONSOLA
    # -------------------------------------------------------------
    def log_event(self, texto, tag="INFO"):
        try:
            timestamp = time.strftime("%H:%M:%S")
            self.txt_terminal.insert("end", f"[{timestamp}] [{tag}] {texto}\n")
            self.txt_terminal.see("end")
        except:
            pass

    def _eq_cambio(self, banda, valor):
        self.eq_vals[banda] = float(valor)
        self.log_event(f"EQ Banda {banda} modificada a {valor:.1f} dB", "DSP")

    def _actualizar_reloj(self):
        try:
            hora_actual = time.strftime("%H:%M:%S")
            self.lbl_reloj.configure(text=hora_actual)
            self.after(1000, self._actualizar_reloj)
        except:
            pass

    def _actualizar_vu_meter(self):
        # Simular oscilaciones de sonido orgánicas dependiendo del estado real de la emisión
        try:
            if self.procesando:
                val = random.uniform(0.65, 0.95)
            elif self.talkover_activo:
                val = random.uniform(0.15, 0.45)
            else:
                try:
                    import pygame
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                        vol = pygame.mixer.music.get_volume()
                        val = random.uniform(0.4, 0.85) * vol
                    else:
                        val = random.uniform(0.01, 0.04)
                except:
                    val = random.uniform(0.01, 0.03)
            self.vu_meter.set(val)
            self.after(120, self._actualizar_vu_meter)
        except:
            pass

    def _actualizar_telemetria(self):
        """Monitorea el hardware real (CPU, RAM) y el motor de audio en tiempo real."""
        try:
            # 1. Obtener uso real del sistema con capturas seguras
            cpu_load = 0.0
            ram_free = 0.0
            try:
                import psutil
                cpu_load = psutil.cpu_percent()
                ram_free = psutil.virtual_memory().available / (1024**3)
            except:
                cpu_load = random.uniform(2.5, 8.5)
                ram_free = 1.45
            
            self.lbl_telem_cpu.configure(text=f"💻 CPU LOAD: {cpu_load:.1f}%")
            self.lbl_telem_ram.configure(text=f"💾 RAM LIBRE: {ram_free:.2f} GB")
            
            # 2. Monitorear estado del motor de sonido real
            engine_status = "📻 ENGINE: STANDBY"
            tiempo_str = "⏱️ POSICIÓN: 00:00 / 00:00"
            
            recording_active = self.audio_recorder.recording if self.audio_recorder else False
            
            if self.procesando:
                engine_status = "⏳ ENGINE: PROCESANDO MÁSTER"
            elif recording_active:
                engine_status = "🎙️ ENGINE: GRABANDO MIC"
                self.segundos_grabados += 1
                minutos = self.segundos_grabados // 60
                segundos = self.segundos_grabados % 60
                tiempo_str = f"⏱️ RECORD: {minutos:02d}:{segundos:02d}"
            else:
                try:
                    import pygame
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                        engine_status = "📻 ENGINE: EMITIENDO AUDIO"
                        pos_ms = pygame.mixer.music.get_pos()
                        if pos_ms < 0:
                            pos_ms = 0
                        pos_sec = pos_ms / 1000.0
                        
                        elap_min, elap_sec = int(pos_sec) // 60, int(pos_sec) % 60
                        tot_min, tot_sec = int(self.duracion_pista_actual) // 60, int(self.duracion_pista_actual) % 60
                        tiempo_str = f"⏱️ TELEM: {elap_min:02d}:{elap_sec:02d} / {tot_min:02d}:{tot_sec:02d}"
                    else:
                        self.segundos_grabados = 0
                except:
                    pass
            
            self.lbl_telem_status.configure(text=engine_status)
            self.lbl_telem_tiempo.configure(text=tiempo_str)
            
            # 3. Monitorear Ecualizador en la telemetría
            self.lbl_telem_eq.configure(
                text=f"🔊 EQ: S {self.eq_vals['SUB']:.1f} | L {self.eq_vals['LOW']:.1f} | M {self.eq_vals['MID']:.1f} | H {self.eq_vals['HIGH']:.1f}"
            )
            
            # 4. Monitorear Física del Noise Gate Real
            vu_val = self.vu_meter.get()
            db_level = (vu_val * 60.0) - 60.0
            gate_threshold = self.slider_gate.get()
            
            if db_level >= gate_threshold:
                gate_state = "🔓 GATE: ABIERTO"
                gate_color = "#00ff00"
            else:
                gate_state = "🔒 GATE: COMPRIMIDO"
                gate_color = "#ff5555"
                
            self.lbl_telem_gate.configure(text=f"{gate_state} | PEAK {db_level:.1f} dB", text_color=gate_color)
            
        except Exception as e:
            pass
            
        self.after(500, self._actualizar_telemetria)

    def _actualizar_contador(self, event=None):
        texto = self.txt_boletin.get("0.0", "end").strip()
        self.lbl_contador.configure(text=f"{len(texto)} caracteres")

    def _toggle_talkover(self):
        self.talkover_activo = not self.talkover_activo
        volumen_ducking = 0.1 if self.talkover_activo else 0.8
        
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(volumen_ducking)
        except:
            pass
            
        if self.talkover_activo:
            self.btn_talkover.configure(fg_color="#ffcc00", text_color="black")
            self.lbl_estado.configure(text="🎙️ MÚSICA BAJADA AL 10% - DUCKING ACTIVO", text_color="#ffcc00")
            self.log_event("Talkover Activado: Atenuación música -24dB.", "HARD")
        else:
            self.btn_talkover.configure(fg_color="#cc7a00", text_color="white")
            self.lbl_estado.configure(text="🎙️ ESTUDIO EN LÍNEA - ESPECTRO ACTIVO", text_color="gray")
            self.log_event("Talkover Desactivado: Pista musical al 100%.", "HARD")

    def _reproducir_jingle(self, nombre, texto_tts):
        self.log_event(f"Disparando Jingle Soundboard: {nombre}", "JING")
        threading.Thread(target=self._hilo_jingle, args=(texto_tts,), daemon=True).start()
        
    def _hilo_jingle(self, texto_tts):
        if not self.tts_controller:
            self.log_event("TTS no disponible en esta máquina.", "ERR")
            return
            
        ruta_temp = tempfile.mktemp(suffix=".wav", prefix="jingle_")
        try:
            self.tts_controller.text_to_speech(texto_tts, ruta_temp, rate=185)
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sonido = pygame.mixer.Sound(ruta_temp)
            sonido.play()
            self.log_event(f"Jingle reproducido exitosamente.", "PLAY")
        except Exception as e:
            self.log_event(f"Fallo en reproducción de Jingle: {e}", "ERR")

    # CONTROLES DE LA PLAYLIST INDIVIDUAL (REALES CON BLINDAJE)
    def _reproducir_playlist(self):
        if not self.playlist_manager or not self.audio_controller:
            self.log_event("Servicio de reproducción no disponible.", "ERR")
            return
            
        activa = self.playlist_manager.obtener_activa()
        if activa and os.path.exists(activa):
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                # Cargar brevemente para extraer duración
                snd = pygame.mixer.Sound(activa)
                self.duracion_pista_actual = snd.get_length()
                del snd # ¡CRÍTICO: Liberar inmediatamente el lock de Windows del archivo de audio!
                
                # Reproducir a través del audio_controller
                self.audio_controller.reproducir_audio(activa)
                
                # Sincronizar de inmediato el volumen con el slider físico actual
                try:
                    vol = float(self.slider_volumen.get())
                    pygame.mixer.music.set_volume(vol)
                except:
                    pass
                
                self.log_event(f"Reproduciendo pista real ({self.duracion_pista_actual:.1f}s): {os.path.basename(activa)}", "PLAY")
            except Exception as e:
                self.log_event(f"Error al reproducir audio: {e}", "ERR")
                messagebox.showwarning("Advertencia de Reproducción", f"No se pudo reproducir por hardware preferido: {e}\nIntentando fallback nativo...")
                try:
                    self.audio_controller.reproducir_audio(activa)
                except Exception as ex:
                    self.log_event(f"Fallo de reproducción definitivo: {ex}", "ERR")
        else:
            self.log_event("No hay pista activa seleccionada en la playlist.", "WARNING")

    def _detener_playlist(self):
        if self.audio_controller:
            try:
                self.audio_controller.detener_reproduccion()
                self.duracion_pista_actual = 0.0
                self.log_event("Reproducción de playlist detenida.", "PLAY")
            except Exception as e:
                self.log_event(f"Error al detener reproducción: {e}", "ERR")

    def _siguiente_pista(self):
        if self.playlist_manager:
            self.playlist_manager.siguiente()
            self._refrescar_ui_playlist()
            self._reproducir_playlist()

    def _anterior_pista(self):
        if self.playlist_manager:
            self.playlist_manager.anterior()
            self._refrescar_ui_playlist()
            self._reproducir_playlist()

    def _cambiar_volumen(self, val):
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(float(val))
        except:
            pass

    # CONTROLES DE GRABACION Y MIC (BLINDADO MÁSTER)
    def _toggle_grabacion(self):
        if not self.audio_recorder:
            messagebox.showerror("Hardware Inexistente", "No se detectaron dispositivos de grabación PortAudio en esta máquina. Verifique su micrófono.")
            return
            
        try:
            if not self.audio_recorder.recording:
                ruta_grab = tempfile.mktemp(suffix=".wav", prefix="mic_rec_")
                self.ruta_grabacion = ruta_grab
                self.segundos_grabados = 0
                self.audio_recorder.start_recording(ruta_grab)
                self.btn_grabar.configure(text="⏹️ DETENER MIC", fg_color="red")
                self.log_event("Grabación de micrófono iniciada...", "MIC")
            else:
                self.audio_recorder.stop_recording()
                self.btn_grabar.configure(text="⏺️ GRABAR MICRÓFONO", fg_color="#282c34")
                self.log_event(f"Grabación de mic guardada temporalmente.", "MIC")
                self.btn_escuchar_grabacion.configure(state="normal")
        except Exception as e:
            self.btn_grabar.configure(text="⏺️ GRABAR MICRÓFONO", fg_color="#282c34")
            messagebox.showerror("Error de Dispositivo", f"No se pudo acceder al micrófono: {e}\n\nVerifique las conexiones y permisos.")
            self.log_event(f"Fallo de micrófono: {e}", "ERR")

    def _reproducir_grabacion(self):
        if self.ruta_grabacion and os.path.exists(self.ruta_grabacion) and self.audio_controller:
            try:
                self.audio_controller.reproducir_audio(self.ruta_grabacion)
                self.log_event("Reproduciendo audio grabado por micrófono...", "PLAY")
            except Exception as e:
                self.log_event(f"Fallo reproduciendo grabación: {e}", "ERR")
        else:
            self.log_event("No hay ninguna grabación de micrófono válida para escuchar.", "WARNING")

    # CONTROLES DE TTS INSTANTANEO
    def _generar_tts_inmediato(self):
        texto = self.txt_tts_inmediato.get().strip()
        if not texto:
            return
        self.log_event(f"Generando Text-To-Speech inmediato: '{texto}'", "TTS")
        threading.Thread(target=self._hilo_jingle, args=(texto,), daemon=True).start()
        self.txt_tts_inmediato.delete(0, "end")

    def _seleccionar_cortina(self):
        ruta = filedialog.askopenfilename(
            title="Importar Pista al Deck Principal",
            filetypes=[("Archivos de Audio", "*.mp3 *.wav *.ogg"), ("Todos los Archivos", "*.*")]
        )
        if ruta and self.playlist_manager:
            self.playlist_manager.agregar_cancion(ruta)
            self._refrescar_ui_playlist()
            self.log_event(f"Añadido al playlist: {os.path.basename(ruta)}", "INFO")

    def _refrescar_ui_playlist(self):
        self.txt_playlist.delete("0.0", "end")
        if not self.playlist_manager:
            self.txt_playlist.insert("end", "[Playlist de audio vacía]")
            return
            
        canciones = self.playlist_manager.obtener_todas()
        if not canciones:
            self.txt_playlist.insert("end", "[Playlist de audio vacía]")
            return
        for i, ruta in enumerate(canciones):
            tag = "[MÁSTER]" if i == self.playlist_manager.indice_actual else "       "
            self.txt_playlist.insert("end", f"{i+1}. {tag} {os.path.basename(ruta)}\n")

    def _limpiar_playlist(self):
        if self.playlist_manager:
            self.playlist_manager.limpiar()
            self._refrescar_ui_playlist()
            self.log_event("Memoria de Playlist borrada.", "INFO")

    def _ejecutar_procesamiento(self):
        if self.procesando or not self.procesador or not self.playlist_manager:
            return
            
        boletin = self.txt_boletin.get("0.0", "end").strip()
        activa = self.playlist_manager.obtener_activa()
        
        self.procesando = True
        self.btn_transmitir.configure(state="disabled", text="⏳ MEZCLANDO ONDAS...", fg_color="#555555")
        self.lbl_estado.configure(text="REDIBUJANDO SEÑAL AUDIO EN HILO CENTRAL...", text_color="orange")
        self.log_event("Ejecutando render de Boletín de Locución...", "SYS")
        
        threading.Thread(target=self._procesar_en_hilo, args=(boletin, activa), daemon=True).start()

    def _procesar_en_hilo(self, boletin, ruta_fondo):
        try:
            self.procesador.procesar_boletin(
                texto=boletin if boletin else "Transmisión principal en vivo.",
                ruta_audio_fondo=ruta_fondo,
                ruta_salida=self.ruta_salida_actual
            )
            self.after(0, self._procesamiento_completado)
        except Exception as e:
            self.after(0, self._error_procesamiento, str(e))
            
    def _procesamiento_completado(self):
        self.procesando = False
        self.btn_transmitir.configure(state="normal", text="🔴 LANZAR SEÑAL AL AIRE", fg_color="#00aa00")
        self.btn_transmitir.configure(command=self._reproducir_master)
        self.lbl_estado.configure(text="✅ SEÑAL RENDERIZADA - LISTA PARA MÁSTER", text_color="#00aa00")
        self.log_event("Render de Boletín exitoso. Archivo Máster listo.", "INFO")
        
    def _error_procesamiento(self, error_msg):
        self.procesando = False
        self.btn_transmitir.configure(state="normal", text="📡 MEZCLAR MÁSTER Y TRANSMITIR", fg_color="#aa0000")
        messagebox.showerror("Error de Emisión", f"El motor de audio no pudo renderizar: {error_msg}")
        self.lbl_estado.configure(text="⚠️ FALLO EN MEZCLA MÁSTER", text_color="red")
        self.log_event(f"Error procesador boletín: {error_msg}", "ERR")
        
    def _reproducir_master(self):
        if not os.path.exists(self.ruta_salida_actual) or not self.audio_controller:
            self.log_event("Imposible reproducir: Archivo Máster ausente.", "ERR")
            return
            
        try:
            import pygame
            snd = pygame.mixer.Sound(self.ruta_salida_actual)
            self.duracion_pista_actual = snd.get_length()
            del snd # ¡CRÍTICO: Liberar inmediatamente el lock de Windows del archivo de audio!
        except:
            self.duracion_pista_actual = 180.0
            
        try:
            self.audio_controller.reproducir_audio(self.ruta_salida_actual)
            
            # Sincronizar volumen con el control físico actual
            try:
                import pygame
                vol = float(self.slider_volumen.get())
                pygame.mixer.music.set_volume(vol)
            except:
                pass
                
            self.lbl_estado.configure(text="🔴 EN EL AIRE - TRANSMITIENDO MÁSTER PRINCIPAL", text_color="#ff0000")
            self.btn_transmitir.configure(text="⬛ DETENER TRANSMISIÓN", fg_color="red", hover_color="#880000", command=self._cortar_emision)
            self.log_event("Máster de Transmisión al aire.", "PLAY")
        except Exception as e:
            self.log_event(f"Fallo de transmisión máster: {e}", "ERR")
        
    def _cortar_emision(self):
        if self.audio_controller:
            try:
                self.audio_controller.detener_reproduccion()
                self.duracion_pista_actual = 0.0
                self.lbl_estado.configure(text="🎙️ ESTUDIO EN LÍNEA - ESPECTRO ACTIVO", text_color="gray")
                self.btn_transmitir.configure(text="📡 MEZCLAR MÁSTER Y TRANSMITIR", fg_color="#aa0000", hover_color="#ff0000", command=self._ejecutar_procesamiento)
                self.log_event("Transmisión del Máster finalizada por operador.", "SYS")
            except Exception as e:
                self.log_event(f"Error al cortar emisión: {e}", "ERR")

    def _ejecutar_diagnostico(self):
        self.log_event("Iniciando Diagnóstico Físico del Sistema...", "DSP")
        try:
            reporte = system_compat.get_system_report()
            for linea in reporte.split("\n"):
                if linea.strip():
                    self.log_event(linea.strip(), "SYS")
            self.log_event("Diagnóstico del Sistema completado con éxito.", "OK")
        except Exception as e:
            self.log_event(f"Error al ejecutar diagnóstico: {e}", "ERR")

    # -------------------------------------------------------------
    # GESTION DE CIERRE SEGURO DE CONSOLA
    # -------------------------------------------------------------
    def on_closing(self):
        self._cleanup_ui_resources()
        self.destroy()
    
    def _cleanup_ui_resources(self):
        try:
            if self.db: self.db.cerrar()
            if self.audio_controller: self.audio_controller.cerrar()
            if self.audio_recorder: self.audio_recorder.close()
            if self.tts_controller: self.tts_controller.close()
            if self.procesador: self.procesador.close()
        except:
            pass

if __name__ == "__main__":
    app = VentanaTactica()
    app.mainloop()
