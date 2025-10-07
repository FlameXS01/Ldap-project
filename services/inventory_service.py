from ldap.client import LDAPClient
from ldap.models import EquipoLDAP
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class InventoryService:
    def __init__(self):
        self.ldap_client = LDAPClient()
        self.filtro_fecha = settings.FILTRO_FECHA
    
    def generar_inventario(self) -> bool:
        """Genera el reporte de inventario completo"""
        try:
            logger.info("🚀 Iniciando proceso de inventario...")
            logger.info(f"📅 Filtro de fecha: {self.filtro_fecha.strftime('%d/%m/%Y')}")
            
            equipos_ldap = self.ldap_client.obtener_equipos()
            
            if not equipos_ldap:
                logger.warning("⚠️ No se encontraron equipos en LDAP")
                return False
            
            equipos_filtrados = self._filtrar_equipos(equipos_ldap)
            self._generar_reporte(equipos_filtrados)
            
            logger.info(f"✅ Inventario completado. {len(equipos_filtrados)} equipos procesados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generando inventario: {e}", exc_info=True)
            return False
        finally:
            self.ldap_client.cerrar_conexion()
    
    def _filtrar_equipos(self, equipos_ldap):
        """Filtra equipos por fecha de último logon"""
        equipos = []
        equipos_filtrados_por_fecha = 0
        
        for equipo_ldap in equipos_ldap:
            equipo = EquipoLDAP.from_ldap_entry(equipo_ldap)
            
            if equipo.last_logon:
                if equipo.last_logon >= self.filtro_fecha:
                    equipos.append(equipo)
                    equipos_filtrados_por_fecha += 1
            else:
                logger.warning(f"⚠️ Equipo {equipo.nombre} sin fecha de último logon")
        
        logger.info(f"📊 Filtro aplicado: {equipos_filtrados_por_fecha} equipos después del {self.filtro_fecha.strftime('%d/%m/%Y')}")
        return equipos
    
    def _generar_reporte(self, equipos):
        """Genera el reporte formateado"""
        if not equipos:
            logger.warning("📭 No hay equipos que cumplan con el filtro")
            return
        
        # Log del reporte
        logger.info("=" * 60)
        logger.info("🖥️ INVENTARIO COMBINADO LDAP + HARDWARE")
        logger.info("=" * 60)
        
        for equipo in equipos:
            fecha_formateada = equipo.last_logon.strftime("%d/%m/%Y %H:%M:%S")
            logger.info(f"🔍 {equipo.nombre} - Last Log: {fecha_formateada}")
            
        logger.info("=" * 60)
        logger.info(f"📈 Total equipos en AD: {len(equipos)}")