from datetime import datetime, date, time
import pytz

def localize_datetime(dt: datetime, timezone: pytz.BaseTzInfo) -> datetime:
    """
    Asegura que un objeto datetime tenga la zona horaria correcta.
    """
    if dt.tzinfo is None:
        return timezone.localize(dt)
    return dt.astimezone(timezone)

def get_day_range(day: date, timezone: pytz.BaseTzInfo) -> tuple[str, str]:
    """
    Calcula el inicio y fin de un día específico en formato ISO RFC3339.
    
    Args:
        day (date): El día deseado.
        timezone (pytz.BaseTzInfo): La zona horaria local.
        
    Returns:
        tuple[str, str]: (ISO start_time, ISO end_time)
    """
    start_dt = timezone.localize(datetime.combine(day, time.min))
    end_dt = timezone.localize(datetime.combine(day, time.max))
    return start_dt.isoformat(), end_dt.isoformat()

def format_google_date(date_str: str | None) -> str:
    """
    Limpia las fechas raras que devuelve Google Calendar API.
    
    Args:
        date_str: String de fecha ISO (ej: '2023-10-01T10:00:00Z').
        
    Returns:
        str: Fecha formateada como 'YYYY-MM-DD HH:MM:SS'.
    """
    if not date_str:
        return ""
    try:
        # Reemplaza Z (Zulu) por el offset UTC para compatibilidad
        clean_date = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_date)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Si es una fecha "todo el día" (YYYY-MM-DD), le agrega ceros
        return f"{date_str} 00:00:00"

def get_now_formatted() -> str:
    """Retorna la fecha y hora actual para el contexto de la IA."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S %A')