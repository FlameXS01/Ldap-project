import subprocess
from typing import List
from ldap.client import LDAPClient
from ldap.models import EquipoLDAP
from config.settings import settings
from utils.logger import setup_logger
from datetime import datetime

from utils.remote_scripts import habilitar_servicios_remotos




logger = setup_logger(__name__)

class InventoryService:
    def __init__(self):
        self.ldap_client = LDAPClient()
        self.filtro_fecha = settings.FILTRO_FECHA
    
    
    def activas_en_fecha(self) -> bool:
        """Genera el reporte de inventario completo"""
        try:
            logger.info("🚀 Iniciando proceso de inventario...")
            logger.info(f"📅 Filtro de fecha: {self.filtro_fecha.strftime('%d/%m/%Y')}")
            
            equipos_ldap = self.ldap_client.obtener_equipos()
            
            if not equipos_ldap:
                logger.warning("⚠️ No se encontraron equipos en LDAP")
                return False
            
            equipos_filtrados = self._filtrar_equipos_fecha(equipos_ldap)
            self._generar_reporte(equipos_filtrados)
            
            logger.info(f"✅ Inventario completado. {len(equipos_filtrados)} equipos procesados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generando inventario: {e}", exc_info=True)
            return False
        finally:
            self.ldap_client.cerrar_conexion()
    
    def _filtrar_equipos_fecha(self, equipos_ldap):
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

    def _buscar_por_nombre(self, equipos: List[EquipoLDAP], nombre_equipo: str) -> bool:
        for i, equipo in enumerate(equipos):
            if equipo.nombre == nombre_equipo.upper():
                return True
        return False

    def enviar_mensaje_netmsg(self, computadora: str, mensaje: str) -> bool:
        pc = self._buscar_por_nombre(self.ldap_client.obtener_equipos(), computadora)
        if pc :
            try:
                comando = f'msg /SERVER:{computadora} * "{mensaje}"'
                resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
                logger.info("=" * 60)
                logger.info("Mensaje enviado satisfactoriamente")
                return True
            except subprocess.CalledProcessError as e:
                # Capturamos la salida de error
                error_output = e.stderr.strip() if e.stderr else "Sin mensaje de error"
                logger.error(f"Error al enviar mensaje a {computadora}: {e}\n. Detalles: {error_output}")
                return False
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout al enviar mensaje a {computadora}")
                return False
            except Exception as e:
                logger.error(f"Error inesperado al enviar mensaje a {computadora}: {e}")
                return False
        else:      
            logger.error("No se completó el proceso: PC no encontrada en el directorio")    
            return False
        
    def enviar_mensaje_powershell(self, computadora: str, mensaje: str, titulo: str = "Mensaje del Sistema") -> bool:
        """Envía mensaje usando PowerShell sin requerir RPC"""
        try:
            # Script PowerShell mejorado
            script_ps = f"""
            try {{
                # Verificar si la PC está disponible
                if (Test-Connection -ComputerName "{computadora}" -Count 1 -Quiet) {{
                    # Crear un mensaje usando .NET (no requiere servicios de red)
                    Add-Type -AssemblyName System.Windows.Forms
                    
                    # Para enviar a una PC remota necesitamos una aproximación diferente
                    # En lugar de MessageBox (que es local), usamos una alternativa
                    $mensaje = "{mensaje}"
                    $titulo = "{titulo}"
                    
                    # Intentar crear un mensaje en la PC remota via WMI o Scheduled Task
                    # Esta es una alternativa que funciona en más entornos
                    $command = "msg * '$mensaje' /TIME:30"
                    
                    # Ejecutar comando remoto via WMI
                    $process = Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c $command" -ComputerName "{computadora}" -ErrorAction Stop
                    
                    if ($process.ReturnValue -eq 0) {{
                        Write-Output "SUCCESS: Mensaje programado para enviarse"
                        exit 0
                    }} else {{
                        Write-Output "ERROR: No se pudo crear el proceso remoto"
                        exit 1
                    }}
                }} else {{
                    Write-Output "ERROR: PC no disponible"
                    exit 1
                }}
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
                exit 1
            }}
            """
            
            resultado = subprocess.run(
                ["powershell", "-Command", script_ps],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"DEBUG - stdout: {resultado.stdout}")
            print(f"DEBUG - stderr: {resultado.stderr}")
            print(f"DEBUG - returncode: {resultado.returncode}")
            
            if resultado.returncode == 0 and "SUCCESS" in resultado.stdout:
                logger.info(f"✅ Mensaje enviado a {computadora} via PowerShell")
                return True
            else:
                logger.error(f"❌ Error PowerShell: {resultado.stderr or resultado.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Timeout en PowerShell para {computadora}")
            return False
        except Exception as e:
            logger.error(f"💥 Error inesperado en PowerShell: {e}")
            return False
        
    def enviar_mensaje_wmi(self, computadora: str, mensaje: str) -> bool:
        """Envía mensaje usando WMI directamente - CORREGIDO"""
        try:
            # Primero verificar si WMI está disponible
            test_script = f'Get-WmiObject -Class Win32_ComputerSystem -ComputerName "{computadora}" -ErrorAction Stop'
            test_result = subprocess.run(
                ["powershell", "-Command", test_script],
                capture_output=True,
                text=True
            )
            
            if test_result.returncode != 0:
                logger.error(f"❌ WMI no disponible en {computadora}")
                return False
            
            # ESCAPAR correctamente el mensaje para PowerShell
            mensaje_escapado = mensaje.replace('"', '`"').replace("'", "`'")
            
            # Script PowerShell CORREGIDO
            script_ps = f"""
    try {{
        $process = [WMIClass]\"\\\\{computadora}\\root\\cimv2:Win32_Process\"
        $command = \"msg * `\"{mensaje_escapado}`\" /TIME:60\"
        $result = $process.Create($command)
        
        if ($result.ReturnValue -eq 0) {{
            Write-Output "SUCCESS"
            exit 0
        }} else {{
            Write-Output "ERROR: Código $($result.ReturnValue)"
            exit 1
        }}
    }} catch {{
        Write-Output "ERROR: $($_.Exception.Message)"
        exit 1
    }}
    """
            
            resultado = subprocess.run(
                ["powershell", "-Command", script_ps],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"DEBUG WMI - stdout: {resultado.stdout}")
            print(f"DEBUG WMI - stderr: {resultado.stderr}")
            print(f"DEBUG WMI - returncode: {resultado.returncode}")
            
            if resultado.returncode == 0:
                logger.info(f"✅ Mensaje enviado via WMI a {computadora}")
                return True
            else:
                logger.error(f"❌ Error WMI: {resultado.stderr or resultado.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Error WMI: {e}")
            return False

    def envio_forzado(self, computadora: str, mensaje: str):
        try:
            habilitar_servicios_remotos(computadora)

            done = self.enviar_mensaje_netmsg(computadora, mensaje)
            if not done:
                done = self.enviar_mensaje_powershell(computadora, mensaje)
            if not done:
                done = self.enviar_mensaje_wmi(computadora, mensaje)
            
        except Exception as e:
            raise e
        
            
