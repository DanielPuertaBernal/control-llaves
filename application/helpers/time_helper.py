"""
Helper para conversiones de tiempo
Maneja conversiones entre diferentes formatos: HH:MM:SS, minutos, segundos
"""
from typing import Optional


class TimeHelper:
    """Utilidades para conversión y formateo de tiempo"""
    
    @staticmethod
    def hhmmss_to_seconds(valor: str) -> Optional[int]:
        """
        Convierte un string HH:MM:SS a segundos
        
        Args:
            valor: String en formato HH:MM:SS
            
        Returns:
            Segundos totales o None si es inválido
        """
        if valor is None:
            return None
        
        valor = str(valor).strip()
        if not valor or valor.lower() in ('n/a', 'na', ''):
            return None
        
        if valor == '0':
            return 0
        
        if ':' not in valor:
            return None
        
        partes = valor.split(':')
        if len(partes) != 3:
            return None
        
        try:
            horas = int(partes[0])
            minutos = int(partes[1])
            segundos = int(partes[2])
            return horas * 3600 + minutos * 60 + segundos
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def seconds_to_hhmmss(segundos: int) -> str:
        """
        Convierte segundos a formato HH:MM:SS
        
        Args:
            segundos: Segundos totales
            
        Returns:
            String en formato HH:MM:SS
        """
        if segundos is None or segundos < 0:
            return "00:00:00"
        
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60
        
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"
    
    @staticmethod
    def minutes_to_hhmm(minutos: float) -> str:
        """
        Convierte minutos a formato HH:MM
        
        Args:
            minutos: Minutos totales (puede ser decimal)
            
        Returns:
            String en formato HH:MM
        """
        if minutos is None or minutos < 0:
            return "00:00"
        
        horas = int(minutos // 60)
        mins = int(minutos % 60)
        
        return f"{horas:02d}:{mins:02d}"
    
    @staticmethod
    def seconds_to_minutes(segundos: Optional[int]) -> float:
        """
        Convierte segundos a minutos (con decimales)
        
        Args:
            segundos: Segundos totales
            
        Returns:
            Minutos con decimales
        """
        if segundos is None or segundos < 0:
            return 0.0
        
        return round(segundos / 60, 2)
    
    @staticmethod
    def minutes_to_seconds(minutos: float) -> int:
        """
        Convierte minutos a segundos
        
        Args:
            minutos: Minutos totales
            
        Returns:
            Segundos enteros
        """
        if minutos is None or minutos < 0:
            return 0
        
        return int(minutos * 60)
