from ldap3 import Server, Connection, ALL, SUBTREE
from config.settings import LDAP_CONFIG

class LDAPClient:
    def __init__(self):
        self.config = LDAP_CONFIG
        
    def conectar(self):
        """Establece conexión con el servidor LDAP"""
        user_dn = f"{self.config['user_name']}@{self.config['domain_name']}"
        server = Server(self.config['server_name'], get_info=ALL)
        self.conn = Connection(server, user=user_dn, 
                             password=self.config['password'], 
                             auto_bind=True)
        return self.conn
    
    def obtener_equipos(self):
        """Obtiene todos los equipos de la OU configurada"""
        self.conectar()
        self.conn.search(
            self.config['ou_busqueda'], 
            '(objectClass=computer)', 
            attributes=['cn', 'operatingSystem', 'lastLogon'], 
            search_scope=SUBTREE
        )
        return self.conn.entries
    