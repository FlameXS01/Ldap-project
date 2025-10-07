from datetime import datetime, timezone
import os 
# Configuración LDAP

LDAP_CONFIG = {
    'server_name': 'dc3.cimex.com.cu',
    'domain_name': 'cimex.com.cu',
    'user_name': 'admsilenierpr',
    'password': 'admin0124*',
    'ou_busqueda': 'OU=SI-PC,OU=SI-Sucursal Sancti Spíritus,OU=Domain Computers,DC=cimex,DC=com,DC=cu'
}

# Configuración de filtros
FILTRO_FECHA = datetime(2025, 10, 7, tzinfo=timezone.utc)