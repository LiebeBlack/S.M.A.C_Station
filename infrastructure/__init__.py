# -*- coding: utf-8 -*-
from infrastructure.database import DatabaseConnection
from infrastructure.audio_fallback import AudioFallbackController
from infrastructure.audio_recording import AudioRecordingFallback
from infrastructure.tts_fallback import TTSFallbackController
from infrastructure.audio_processing_fallback import AudioProcessingFallback
from infrastructure.system_compat import system_compat, setup_signal_handlers
from infrastructure.system_checker import system_checker
from infrastructure.ui_fallback import UIFallback, check_ui_dependencies
from infrastructure.signal_handler import resource_cleanup, register_resource_cleanup
from infrastructure.localization import i18n

__all__ = [
    'DatabaseConnection',
    'AudioFallbackController',
    'AudioRecordingFallback',
    'TTSFallbackController',
    'AudioProcessingFallback',
    'system_compat',
    'setup_signal_handlers',
    'system_checker',
    'UIFallback',
    'check_ui_dependencies',
    'resource_cleanup',
    'register_resource_cleanup',
    'i18n'
]
