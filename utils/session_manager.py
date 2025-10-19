"""Менеджер сессий пользователей"""

from typing import Dict, Optional
from models import UserSession


class SessionManager:
    """Управление сеансами пользователей"""
    
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
    
    def get_session(self, user_id: int) -> UserSession:
        """Получает или создает сессию пользователя"""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        return self._sessions[user_id]
    
    def has_session(self, user_id: int) -> bool:
        """Проверяет наличие сессии"""
        return user_id in self._sessions
    
    def clear_session(self, user_id: int):
        """Очищает сессию пользователя"""
        if user_id in self._sessions:
            del self._sessions[user_id]
    
    def get_all_sessions(self) -> Dict[int, UserSession]:
        """Возвращает все активные сессии"""
        return self._sessions.copy()


# Глобальный экземпляр менеджера сессий
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Получает глобальный экземпляр менеджера сессий"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

