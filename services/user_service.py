from ldap.client import LDAPClient
from ldap.models import UsuarioLDAP
from config.settings import settings
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)

class UserService:
    def __init__(self):
        self.ldap_client = LDAPClient()
        self.filtro_fecha = settings.FILTRO_FECHA

    def activos_en_fecha(self) -> bool:
        """Genera el reporte de usuarios completo"""
        try:
            logger.info("🚀 Iniciando proceso...")
            logger.info(f"📅 Filtro de fecha: {self.filtro_fecha.strftime('%d/%m/%Y')}")
            
            usuarios_ldap = self.ldap_client.obtener_usuarios()
            
            if not usuarios_ldap:
                logger.warning("⚠️ No se encontraron usuarios en LDAP")
                return False
            
            usuarios_filtrados = self._filtrar_usuarios_fecha(usuarios_ldap)
            self._generar_reporte(usuarios_filtrados)
            
            logger.info(f"✅ Inventario completado. {len(usuarios_filtrados)} usuarios procesados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generando inventario: {e}", exc_info=True)
            return False
        finally:
            self.ldap_client.cerrar_conexion()

    def _filtrar_usuarios_fecha(self, usuarios_ldap):
        """Filtra usuarios por fecha de último logon"""
        users = []
        user_filtrados_por_fecha = 0
            
        for user in usuarios_ldap:
            if user.last_logon:
                if user.last_logon >= self.filtro_fecha:
                    users.append(user)
                    user_filtrados_por_fecha += 1
            else:
                logger.warning(f"⚠️ Usuario {user.nombre} sin fecha de último logon")
            
        logger.info(f"📊 Filtro aplicado: {user_filtrados_por_fecha} usuarios después del {self.filtro_fecha.strftime('%d/%m/%Y')}")
        return users
    
    def _generar_reporte(self, usuarios):
        """Genera el reporte formateado"""
        if not usuarios:
            logger.warning("📭 No hay usuarios que cumplan con el filtro")
            return
        
        # Log del reporte
        logger.info("=" * 60)
        
        for user in usuarios:
            fecha_string = user.last_logon            
            if fecha_string:
                if isinstance(fecha_string, str):
                    try:
                        fecha_limpia = fecha_string.split('+')[0].split('.')[0]
                        fecha_dt = datetime.strptime(fecha_limpia, "%Y-%m-%d %H:%M:%S")
                        fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        fecha_formateada = f"ERROR: {str(e)}"
                elif isinstance(fecha_string, datetime):
                    fecha_formateada = fecha_string.strftime("%d/%m/%Y %H:%M:%S")
                else:
                    fecha_formateada = f"TIPO NO SOPORTADO: {type(fecha_string)}"
            else:
                fecha_formateada = "NUNCA / NO DISPONIBLE"
            
            logger.info(f"🔍 {user.nombre} - Last Log: {fecha_formateada}")
            
        logger.info("=" * 60)
        logger.info(f"📈 Total usuarios en AD: {len(usuarios)}")
       

    def listar_usuarios(self):
        """Genera el reporte de usuarios completo"""
        try:
            logger.info("🚀 Iniciando proceso...")

            usuarios_ldap = self.ldap_client.obtener_usuarios()

            if not usuarios_ldap:
                logger.warning("⚠️ No se encontraron usuarios en LDAP")
                return False

            self._generar_reporte(usuarios_ldap)
            return True
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuarios: {e}", exc_info=True)
            return False
        finally:
            self.ldap_client.cerrar_conexion()