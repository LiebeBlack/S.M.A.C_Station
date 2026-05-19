# -*- coding: utf-8 -*-
"""
Sistema de Localización e Internacionalización (i18n)
Soporta múltiples idiomas con fallback automático.
"""
import os
import locale
import json
from typing import Dict, Optional
from infrastructure.system_compat import system_compat

class Localization:
    """Gestiona la localización e internacionalización de la aplicación."""
    
    def __init__(self):
        self.current_locale = self._detect_system_locale()
        self.translations = {}
        self.available_locales = ['es', 'en', 'pt', 'fr', 'de']
        self._load_translations()
    
    def _detect_system_locale(self) -> str:
        """Detecta el locale del sistema."""
        try:
            # Intentar obtener locale del sistema
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extraer código de idioma (ej: 'es_ES' -> 'es')
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in self.available_locales:
                    return lang_code
        except:
            pass
        
        # Fallback a español por defecto
        return 'es'
    
    def _load_translations(self):
        """Carga las traducciones para todos los idiomas disponibles."""
        
        # Español (por defecto)
        self.translations['es'] = {
            'app_title': 'S.M.A.C. - Estación de Control Operacional',
            'console_title': 'CONSOLA DE EMISIÓN TÁCTICA OFFLINE',
            'music_curtain': '🎵 Cortina Musical:',
            'select_file': 'Seleccionar Archivo',
            'official_bulletin': '📝 Boletín Oficial:',
            'bulletin_placeholder': 'Escriba aquí el boletín oficial de servicios o contingencia...',
            'characters': 'caracteres',
            'generate_emergency': 'GENERAR COMUNICADO DE EMERGENCIA',
            'playback_controls': '🔊 Controles de Reproducción:',
            'play': '▶ Reproducir',
            'stop': '⏹ Detener',
            'volume': 'Volumen:',
            'history': '📋 Historial de Boletines:',
            'load_selected': 'Cargar Seleccionado',
            'delete': 'Eliminar',
            'update': 'Actualizar',
            'none_selected': 'Ningún boletín seleccionado',
            'status_ready': 'Estado: Terminal Listo / Espectro en Reserva',
            'status_processing': 'Procesando señales, aplicando filtros...',
            'status_success': 'Éxito: Comunicado masterizado',
            'status_error': 'Error',
            'config': '⚙ Configuración',
            'audio_config': '🎵 Configuración de Audio',
            'tts_rate': 'Velocidad TTS:',
            'ducking_db': 'Atenuación Ducking (dB):',
            'ui_config': '🖥️ Configuración de Interfaz',
            'appearance_mode': 'Modo de Apariencia:',
            'color_theme': 'Tema de Color:',
            'filter_config': '🛡️ Configuración de Filtro',
            'forbidden_terms': 'Términos Prohibidos (uno por línea):',
            'save_changes': 'Guardar Cambios',
            'cancel': 'Cancelar',
            'warning_empty_text': 'Por favor, ingrese el texto del boletín.',
            'error_file_not_found': 'No se encuentra el archivo',
            'error_no_audio': 'No hay archivo de audio generado para reproducir.',
            'error_no_selection': 'Por favor, seleccione un boletín del historial.',
            'confirm_delete': '¿Está seguro de eliminar este boletín del historial?',
            'success_saved': 'Configuración guardada correctamente.',
            'success_deleted': 'Boletín eliminado correctamente.',
            'success_loaded': 'Boletín cargado',
            'error_numeric': 'Por favor, ingrese valores numéricos válidos.',
            'mode_dark': 'Dark',
            'mode_light': 'Light',
            'mode_system': 'System',
            'theme_blue': 'blue',
            'theme_dark_blue': 'dark-blue',
            'theme_green': 'green',
        }
        
        # Inglés
        self.translations['en'] = {
            'app_title': 'S.M.A.C. - Operational Control Station',
            'console_title': 'OFFLINE TACTICAL EMISSION CONSOLE',
            'music_curtain': '🎵 Music Curtain:',
            'select_file': 'Select File',
            'official_bulletin': '📝 Official Bulletin:',
            'bulletin_placeholder': 'Write the official service or contingency bulletin here...',
            'characters': 'characters',
            'generate_emergency': 'GENERATE EMERGENCY COMMUNICATION',
            'playback_controls': '🔊 Playback Controls:',
            'play': '▶ Play',
            'stop': '⏹ Stop',
            'volume': 'Volume:',
            'history': '📋 Bulletin History:',
            'load_selected': 'Load Selected',
            'delete': 'Delete',
            'update': 'Update',
            'none_selected': 'No bulletin selected',
            'status_ready': 'Status: Terminal Ready / Spectrum in Reserve',
            'status_processing': 'Processing signals, applying filters...',
            'status_success': 'Success: Communication mastered',
            'status_error': 'Error',
            'config': '⚙ Configuration',
            'audio_config': '🎵 Audio Configuration',
            'tts_rate': 'TTS Rate:',
            'ducking_db': 'Ducking Attenuation (dB):',
            'ui_config': '🖥️ Interface Configuration',
            'appearance_mode': 'Appearance Mode:',
            'color_theme': 'Color Theme:',
            'filter_config': '🛡️ Filter Configuration',
            'forbidden_terms': 'Forbidden Terms (one per line):',
            'save_changes': 'Save Changes',
            'cancel': 'Cancel',
            'warning_empty_text': 'Please enter the bulletin text.',
            'error_file_not_found': 'File not found',
            'error_no_audio': 'No generated audio file to play.',
            'error_no_selection': 'Please select a bulletin from history.',
            'confirm_delete': 'Are you sure you want to delete this bulletin?',
            'success_saved': 'Configuration saved successfully.',
            'success_deleted': 'Bulletin deleted successfully.',
            'success_loaded': 'Bulletin loaded',
            'error_numeric': 'Please enter valid numeric values.',
            'mode_dark': 'Dark',
            'mode_light': 'Light',
            'mode_system': 'System',
            'theme_blue': 'blue',
            'theme_dark_blue': 'dark-blue',
            'theme_green': 'green',
        }
        
        # Portugués
        self.translations['pt'] = {
            'app_title': 'S.M.A.C. - Estação de Controle Operacional',
            'console_title': 'CONSOLE DE EMISSÃO TÁTICA OFFLINE',
            'music_curtain': '🎵 Cortina Musical:',
            'select_file': 'Selecionar Arquivo',
            'official_bulletin': '📝 Boletim Oficial:',
            'bulletin_placeholder': 'Escreva o boletim oficial de serviços ou contingência...',
            'characters': 'caracteres',
            'generate_emergency': 'GERAR COMUNICADO DE EMERGÊNCIA',
            'playback_controls': '🔊 Controles de Reprodução:',
            'play': '▶ Reproduzir',
            'stop': '⏹ Parar',
            'volume': 'Volume:',
            'history': '📋 Histórico de Boletins:',
            'load_selected': 'Carregar Selecionado',
            'delete': 'Excluir',
            'update': 'Atualizar',
            'none_selected': 'Nenhum boletim selecionado',
            'status_ready': 'Status: Terminal Pronto / Espectro em Reserva',
            'status_processing': 'Processando sinais, aplicando filtros...',
            'status_success': 'Sucesso: Comunicado masterizado',
            'status_error': 'Erro',
            'config': '⚙ Configuração',
            'audio_config': '🎵 Configuração de Áudio',
            'tts_rate': 'Taxa TTS:',
            'ducking_db': 'Atenuação Ducking (dB):',
            'ui_config': '🖥️ Configuração de Interface',
            'appearance_mode': 'Modo de Aparência:',
            'color_theme': 'Tema de Cor:',
            'filter_config': '🛡️ Configuração de Filtro',
            'forbidden_terms': 'Termos Proibidos (um por linha):',
            'save_changes': 'Salvar Alterações',
            'cancel': 'Cancelar',
            'warning_empty_text': 'Por favor, insira o texto do boletim.',
            'error_file_not_found': 'Arquivo não encontrado',
            'error_no_audio': 'Nenhum arquivo de áudio gerado para reproduzir.',
            'error_no_selection': 'Por favor, selecione um boletim do histórico.',
            'confirm_delete': 'Tem certeza que deseja excluir este boletim?',
            'success_saved': 'Configuração salva com sucesso.',
            'success_deleted': 'Boletim excluído com sucesso.',
            'success_loaded': 'Boletim carregado',
            'error_numeric': 'Por favor, insira valores numéricos válidos.',
            'mode_dark': 'Dark',
            'mode_light': 'Light',
            'mode_system': 'System',
            'theme_blue': 'blue',
            'theme_dark_blue': 'dark-blue',
            'theme_green': 'green',
        }
        
        # Francés
        self.translations['fr'] = {
            'app_title': 'S.M.A.C. - Station de Contrôle Opérationnel',
            'console_title': 'CONSOLE D\'ÉMISSION TACTIQUE HORS LIGNE',
            'music_curtain': '🎵 Rideau Musical:',
            'select_file': 'Sélectionner Fichier',
            'official_bulletin': '📝 Bulletin Officiel:',
            'bulletin_placeholder': 'Écrivez le bulletin officiciel des services ou de la contingence...',
            'characters': 'caractères',
            'generate_emergency': 'GÉNÉRER COMMUNICATION D\'URGENCE',
            'playback_controls': '🔊 Contrôles de Lecture:',
            'play': '▶ Lire',
            'stop': '⏹ Arrêter',
            'volume': 'Volume:',
            'history': '📋 Historique des Bulletins:',
            'load_selected': 'Charger Sélectionné',
            'delete': 'Supprimer',
            'update': 'Mettre à jour',
            'none_selected': 'Aucun bulletin sélectionné',
            'status_ready': 'Statut: Terminal Prêt / Spectre en Réserve',
            'status_processing': 'Traitement des signaux, application des filtres...',
            'status_success': 'Succès: Communication masterisée',
            'status_error': 'Erreur',
            'config': '⚙ Configuration',
            'audio_config': '🎵 Configuration Audio',
            'tts_rate': 'Taux TTS:',
            'ducking_db': 'Atténuation Ducking (dB):',
            'ui_config': '🖥️ Configuration de l\'Interface',
            'appearance_mode': 'Mode d\'Apparence:',
            'color_theme': 'Thème de Couleur:',
            'filter_config': '🛡️ Configuration du Filtre',
            'forbidden_terms': 'Termes Interdits (un par ligne):',
            'save_changes': 'Enregistrer Modifications',
            'cancel': 'Annuler',
            'warning_empty_text': 'Veuillez entrer le texte du bulletin.',
            'error_file_not_found': 'Fichier non trouvé',
            'error_no_audio': 'Aucun fichier audio généré à lire.',
            'error_no_selection': 'Veuillez sélectionner un bulletin de l\'historique.',
            'confirm_delete': 'Êtes-vous sûr de vouloir supprimer ce bulletin?',
            'success_saved': 'Configuration enregistrée avec succès.',
            'success_deleted': 'Bulletin supprimé avec succès.',
            'success_loaded': 'Bulletin chargé',
            'error_numeric': 'Veuillez entrer des valeurs numériques valides.',
            'mode_dark': 'Dark',
            'mode_light': 'Light',
            'mode_system': 'System',
            'theme_blue': 'blue',
            'theme_dark_blue': 'dark-blue',
            'theme_green': 'green',
        }
        
        # Alemán
        self.translations['de'] = {
            'app_title': 'S.M.A.C. - Operative Kontrollstation',
            'console_title': 'TAKTISCHE OFFLINE-EMISSIONSKONSOLE',
            'music_curtain': '🎵 Musik-Vorhang:',
            'select_file': 'Datei Auswählen',
            'official_bulletin': '📝 Amtliches Bulletin:',
            'bulletin_placeholder': 'Schreiben Sie das amtliche Dienst- oder Notfallbulletin...',
            'characters': 'Zeichen',
            'generate_emergency': 'NOTFALLKOMMUNIKATION ERSTELLEN',
            'playback_controls': '🔊 Wiedergabesteuerung:',
            'play': '▶ Abspielen',
            'stop': '⏹ Stop',
            'volume': 'Lautstärke:',
            'history': '📋 Bulletin-Historie:',
            'load_selected': 'Ausgewähltes Laden',
            'delete': 'Löschen',
            'update': 'Aktualisieren',
            'none_selected': 'Kein Bulletin ausgewählt',
            'status_ready': 'Status: Terminal Bereit / Spektrum in Reserve',
            'status_processing': 'Signale verarbeiten, Filter anwenden...',
            'status_success': 'Erfolg: Kommunikation gemastert',
            'status_error': 'Fehler',
            'config': '⚙ Konfiguration',
            'audio_config': '🎵 Audio-Konfiguration',
            'tts_rate': 'TTS-Rate:',
            'ducking_db': 'Ducking-Dämpfung (dB):',
            'ui_config': '🖥️ Schnittstellenkonfiguration',
            'appearance_mode': 'Erscheinungsmodus:',
            'color_theme': 'Farbschema:',
            'filter_config': '🛡️ Filterkonfiguration',
            'forbidden_terms': 'Verbotene Begriffe (einer pro Zeile):',
            'save_changes': 'Änderungen Speichern',
            'cancel': 'Abbrechen',
            'warning_empty_text': 'Bitte geben Sie den Bulletin-Text ein.',
            'error_file_not_found': 'Datei nicht gefunden',
            'error_no_audio': 'Keine generierte Audiodatei zum Abspielen.',
            'error_no_selection': 'Bitte wählen Sie ein Bulletin aus dem Verlauf.',
            'confirm_delete': 'Sind Sie sicher, dass Sie dieses Bulletin löschen möchten?',
            'success_saved': 'Konfiguration erfolgreich gespeichert.',
            'success_deleted': 'Bulletin erfolgreich gelöscht.',
            'success_loaded': 'Bulletin geladen',
            'error_numeric': 'Bitte geben Sie gültige numerische Werte ein.',
            'mode_dark': 'Dark',
            'mode_light': 'Light',
            'mode_system': 'System',
            'theme_blue': 'blue',
            'theme_dark_blue': 'dark-blue',
            'theme_green': 'green',
        }
    
    def get(self, key: str, locale: Optional[str] = None) -> str:
        """Retorna la traducción de una clave."""
        if locale is None:
            locale = self.current_locale
        
        # Si el locale no está disponible, usar español como fallback
        if locale not in self.translations:
            locale = 'es'
        
        # Si la clave no existe en el locale, intentar en español
        if key not in self.translations[locale]:
            if key in self.translations['es']:
                return self.translations['es'][key]
            else:
                # Retornar la clave misma como último fallback
                return key
        
        return self.translations[locale][key]
    
    def set_locale(self, locale: str):
        """Establece el locale actual."""
        if locale in self.available_locales:
            self.current_locale = locale
        else:
            print(f"Locale '{locale}' no disponible. Usando '{self.current_locale}'.")
    
    def get_available_locales(self) -> list:
        """Retorna los locales disponibles."""
        return self.available_locales
    
    def get_current_locale(self) -> str:
        """Retorna el locale actual."""
        return self.current_locale


# Instancia global de localización
i18n = Localization()
