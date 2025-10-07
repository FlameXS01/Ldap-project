import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación desde variables de entorno"""
    
    def __init__(self):
        # LDAP Configuration
        self.LDAP_SERVER = os.getenv('LDAP_SERVER')
        self.LDAP_DOMAIN = os.getenv('LDAP_DOMAIN')
        self.LDAP_USERNAME = os.getenv('LDAP_USERNAME')
        self.LDAP_PASSWORD = os.getenv('LDAP_PASSWORD')
        self.LDAP_OU_EQUIPOS = os.getenv('LDAP_OU_EQUIPOS')
        self.LDAP_OU_USUARIOS = os.getenv('LDAP_OU_USUARIOS')
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'inventario_ldap.log')
        
        # Filtro de fecha
        fecha_str = os.getenv('FILTRO_FECHA', '2025-10-07')
        self.FILTRO_FECHA = datetime.strptime(fecha_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        # Validar configuración requerida
        self._validar_configuracion()
    
    def _validar_configuracion(self):
        """Valida que todas las configuraciones requeridas estén presentes"""
        required_vars = [
            'LDAP_SERVER', 'LDAP_DOMAIN', 'LDAP_USERNAME', 
            'LDAP_PASSWORD', 'LDAP_OU_USUARIOS', 'LDAP_OU_EQUIPOS'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Faltan variables de entorno requeridas: {', '.join(missing_vars)}")

# Instancia global de configuración
settings = Settings()