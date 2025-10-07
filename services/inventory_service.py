from ldap.client import LDAPClient
from ldap.models import EquipoLDAP
from config.settings import settings
from utils.logger import setup_logger
from datetime import datetime

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
        
        for equipo in equipos_ldap:
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
            fecha_string = equipo.last_logon
            
            # Manejar diferentes tipos de fecha
            if fecha_string:
                if isinstance(fecha_string, str):
                    # Convertir string a datetime primero
                    try:
                        # Limpiar el string (remover timezone y milisegundos)
                        fecha_limpia = fecha_string.split('+')[0].split('.')[0]
                        # Convertir a datetime
                        fecha_dt = datetime.strptime(fecha_limpia, "%Y-%m-%d %H:%M:%S")
                        # Ahora formatear
                        fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        fecha_formateada = f"ERROR: {str(e)}"
                elif isinstance(fecha_string, datetime):
                    # Ya es datetime, formatear directamente
                    fecha_formateada = fecha_string.strftime("%d/%m/%Y %H:%M:%S")
                else:
                    fecha_formateada = f"TIPO NO SOPORTADO: {type(fecha_string)}"
            else:
                fecha_formateada = "NUNCA / NO DISPONIBLE"
            
            logger.info(f"🔍 {equipo.nombre} - Last Log: {fecha_formateada}")
            
        logger.info("=" * 60)
        logger.info(f"📈 Total equipos en AD: {len(equipos)}")
            

    def listar_ordenadores(self):
        """Genera el reporte de ordenadores completo"""
        try:
            logger.info("🚀 Iniciando proceso de inventario...")

            equipos_ldap = self.ldap_client.obtener_equipos()

            if not equipos_ldap:
                logger.warning("⚠️ No se encontraron equipos en LDAP")
                return False

            self._generar_reporte(equipos_ldap)
            return True
        except Exception as e:
            logger.error(f"❌ Error obteniendo equipos: {e}", exc_info=True)
            return False
        finally:
            self.ldap_client.cerrar_conexion()