from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class EquipoLDAP:
    nombre: str
    sistema_operativo: Optional[str]
    last_logon: Optional[datetime]
    
    @classmethod
    def from_ldap_entry(cls, entry):
        """Crea un objeto EquipoLDAP desde una entrada LDAP"""
        last_logon = cls._parse_last_logon(entry.lastLogon.value)
        return cls(
            nombre=entry.cn.value,
            sistema_operativo=getattr(entry, 'operatingSystem', None),
            last_logon=last_logon
        )
    
    @staticmethod
    def _parse_last_logon(fecha_string):
        """Convierte el string de lastLogon a datetime"""
        if isinstance(fecha_string, datetime):
            return fecha_string
        elif isinstance(fecha_string, str):
            try:
                # Limpiar el string (remover timezone y milisegundos)
                fecha_limpia = fecha_string.split('+')[0].split('.')[0]
                # Convertir a datetime
                return datetime.strptime(fecha_limpia, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"⚠️ Error convirtiendo fecha: {fecha_string} - {e}")
                return None
        return None