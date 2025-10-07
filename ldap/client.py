from ldap3 import Server, Connection, ALL, SUBTREE
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LDAPClient:
    def __init__(self):
        self.config = {
            'server_name': settings.LDAP_SERVER,
            'domain_name': settings.LDAP_DOMAIN,
            'user_name': settings.LDAP_USERNAME,
            'password': settings.LDAP_PASSWORD,
            'ou_busqueda': settings.LDAP_OU
        }
        self.conn = None
        
    def conectar(self) -> bool:
        """Establece conexión con el servidor LDAP"""
        try:
            user_dn = f"{self.config['user_name']}@{self.config['domain_name']}"
            server = Server(self.config['server_name'], get_info=ALL)
            self.conn = Connection(
                server, 
                user=user_dn, 
                password=self.config['password'], 
                auto_bind=True
            )
            
            logger.info(f"✅ Conexión LDAP establecida con {self.config['server_name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a LDAP: {e}")
            return False
    
    def obtener_equipos(self):
        """Obtiene todos los equipos de la OU configurada"""
        try:
            if not self.conn or not self.conn.bound:
                if not self.conectar():
                    return []
            
            self.conn.search(
                self.config['ou_busqueda'], 
                '(objectClass=computer)', 
                attributes=['cn', 'operatingSystem', 'lastLogon'], 
                search_scope=SUBTREE
            )
            
            logger.info(f"🔍 Búsqueda LDAP completada. {len(self.conn.entries)} equipos encontrados")
            return self.conn.entries
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda LDAP: {e}")
            return []
    
    def cerrar_conexion(self):
        """Cierra la conexión LDAP"""
        if self.conn:
            self.conn.unbind()
            logger.info("🔒 Conexión LDAP cerrada")