from ldap.client import LDAPClient
from ldap.models import EquipoLDAP
from config.settings import FILTRO_FECHA

class InventoryService:
    def __init__(self):
        self.ldap_client = LDAPClient()
    
    def generar_inventario(self):
        """Genera el reporte de inventario completo"""
        try:
            equipos_ldap = self.ldap_client.obtener_equipos()
            equipos_filtrados = self._filtrar_equipos(equipos_ldap)
            self._imprimir_reporte(equipos_filtrados)
            
        except Exception as e:
            print(f"❌ Error generando inventario: {e}")
    
    def _filtrar_equipos(self, equipos_ldap):
        """Filtra equipos por fecha de último logon"""
        equipos = []
        for equipo_ldap in equipos_ldap:
            equipo = EquipoLDAP.from_ldap_entry(equipo_ldap)
            if equipo.last_logon and equipo.last_logon >= FILTRO_FECHA:
                equipos.append(equipo)
        return equipos
    
    def _imprimir_reporte(self, equipos):
        """Imprime el reporte formateado"""
        print("🖥️ INVENTARIO COMBINADO LDAP + HARDWARE")
        print("=" * 60)
        
        for equipo in equipos:
            fecha_formateada = equipo.last_logon.strftime("%d/%m/%Y %H:%M:%S")
            print(f"\n🔍 {equipo.nombre}")
            print(f"   📊 Last Log: {fecha_formateada}")
            
        print(f"\n📈 Total equipos en AD: {len(equipos)}")