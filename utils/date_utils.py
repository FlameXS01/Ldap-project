from datetime import datetime

def formatear_fecha(fecha: datetime) -> str:
    """Formatea una fecha para mostrar en reports"""
    return fecha.strftime("%d/%m/%Y %H:%M:%S")