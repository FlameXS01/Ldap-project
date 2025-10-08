import subprocess
from typing import Optional
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

def habilitar_powershell_remoting(computadora: str) -> bool:
    """Habilita PowerShell Remoting en una PC remota"""
    try:
        script_ps = f"""
        try {{       
            # Habilitar PowerShell Remoting usando WMI
            $win32process = [WMIClass]"\\\\{computadora}\\root\\cimv2:Win32_Process"
            $result = $win32process.Create("powershell -Command Enable-PSRemoting -Force")

            if ($result.ReturnValue -eq 0) {{
                Write-Output "SUCCESS"
                exit 0
            }} else {{
                Write-Output "ERROR: No se pudo habilitar PowerShell Remoting"
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
            timeout=120
        )

        if resultado.returncode == 0:
            logger.info(f"✅ PowerShell Remoting habilitado en {computadora}")
            return True
        else:
            logger.error(f"❌ Error al habilitar PowerShell Remoting: {resultado.stderr or resultado.stdout}")
            return False

    except Exception as e:
        logger.error(f"💥 Error al habilitar PowerShell Remoting: {e}")
        return False

def habilitar_wmi(computadora: str, password: Optional[str] = settings.LADM_PASSWORD ) -> bool:
    try:
        usuario = f"{computadora}\\administrador"
        
        if password:
            script_ps = f"""
            try {{
                # Crear credenciales - FORMATO CORREGIDO
                $secPassword = ConvertTo-SecureString "{password}" -AsPlainText -Force
                $credential = New-Object System.Management.Automation.PSCredential("{usuario}", $secPassword)
                
                Write-Output "🔐 Intentando conectar a {computadora} como {usuario}"
                
                # PRIMERO: Verificar si podemos conectarnos con estas credenciales
                Write-Output "🔍 Probando conectividad básica..."
                $testBasic = Invoke-Command -ComputerName "{computadora}" -Credential $credential -ScriptBlock {{
                    hostname
                }} -ErrorAction SilentlyContinue
                
                if (-not $testBasic) {{
                    Write-Output "❌ No se pudo conectar con las credenciales proporcionadas"
                    exit 1
                }}
                
                Write-Output "✅ Conexión básica exitosa"
                
                # SEGUNDO: Habilitar servicios usando Invoke-Command (más confiable)
                Write-Output "🛠️ Configurando servicios..."
                $serviceResult = Invoke-Command -ComputerName "{computadora}" -Credential $credential -ScriptBlock {{
                    # Servicios a configurar
                    $services = @('winmgmt', 'RemoteRegistry')
                    
                    foreach ($service in $services) {{
                        try {{
                            # Configurar inicio automático
                            Set-Service -Name $service -StartupType Automatic -ErrorAction SilentlyContinue
                            
                            # Iniciar servicio
                            Start-Service -Name $service -ErrorAction SilentlyContinue
                            
                            # Verificar estado
                            $serviceStatus = Get-Service -Name $service
                            Write-Output "✅ $service : $($serviceStatus.Status)"
                        }} catch {{
                            Write-Output "⚠️ $service : Error - $($_.Exception.Message)"
                        }}
                    }}
                    
                    return $true
                }} -ErrorAction SilentlyContinue
                
                if (-not $serviceResult) {{
                    Write-Output "❌ No se pudieron configurar los servicios"
                    exit 1
                }}
                
                # TERCERO: Configurar firewall
                Write-Output "🔥 Configurando firewall..."
                $firewallResult = Invoke-Command -ComputerName "{computadora}" -Credential $credential -ScriptBlock {{
                    try {{
                        netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
                        Write-Output "✅ Reglas de firewall configuradas"
                        return $true
                    }} catch {{
                        Write-Output "⚠️ Error configurando firewall: $($_.Exception.Message)"
                        return $false
                    }}
                }} -ErrorAction SilentlyContinue
                
                # CUARTO: Verificar que WMI funciona
                Write-Output "🔍 Verificando WMI..."
                Start-Sleep -Seconds 5  # Dar tiempo a que los servicios se inicien
                
                $testWMI = Get-WmiObject -Class Win32_ComputerSystem -ComputerName "{computadora}" -Credential $credential -ErrorAction SilentlyContinue
                if ($testWMI) {{
                    Write-Output "✅ WMI habilitado y funcionando correctamente"
                    Write-Output "SUCCESS"
                    exit 0
                }} else {{
                    Write-Output "❌ WMI no responde después de la configuración"
                    exit 1
                }}
                
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
                exit 1
            }}
            """
        else:
            # Script sin credenciales
            script_ps = f"""
            try {{
                Write-Output "❌ No se proporcionó contraseña"
                exit 1
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
                exit 1
            }}
            """

        # Ejecutar con timeout mayor
        resultado = subprocess.run(
            ["powershell", "-Command", script_ps],
            capture_output=True,
            text=True,
            timeout=120  # Aumentar timeout a 120 segundos
        )

        print(f"DEBUG WMI CORREGIDO - stdout: {resultado.stdout}")
        print(f"DEBUG WMI CORREGIDO - stderr: {resultado.stderr}")
        print(f"DEBUG WMI CORREGIDO - returncode: {resultado.returncode}")

        if resultado.returncode == 0:
            logger.info(f"✅ WMI habilitado en {computadora}")
            return True
        else:
            logger.error(f"❌ Error habilitando WMI: {resultado.stderr or resultado.stdout}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Timeout habilitando WMI en {computadora}")
        return False
    except Exception as e:
        logger.error(f"💥 Error inesperado habilitando WMI: {e}")
        return False
    
def habilitar_servicio_messenger( computadora: str) -> bool:
    """Habilita el servicio Messenger en una PC remota"""
    try:
        script_ps = f"""
        try {{

            # Primero, intentamos obtener el servicio
            $service = Get-WmiObject -Class Win32_Service -Filter "Name='Messenger'" -ComputerName "{computadora}" -ErrorAction SilentlyContinue
            if ($service -eq $null) {{
                Write-Output "ERROR: Servicio Messenger no encontrado. Puede que no esté disponible en esta versión de Windows."
                exit 1
            }}

            if ($service.State -ne 'Running') {{
                $service.StartService()
                Start-Sleep -Seconds 3
            }}

            if ($service.State -eq 'Running') {{
                Write-Output "SUCCESS"
                exit 0
            }} else {{
                Write-Output "ERROR: No se pudo iniciar el servicio Messenger"
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

        if resultado.returncode == 0:
            logger.info(f"✅ Servicio Messenger habilitado en {computadora}")
            return True
        else:
            logger.error(f"❌ Error al habilitar Messenger: {resultado.stderr or resultado.stdout}")
            return False

    except Exception as e:
        logger.error(f"💥 Error al habilitar Messenger: {e}")
        return False
    
def habilitar_servicios_remotos( computadora: str) -> bool:
    """Intenta habilitar todos los servicios remotos necesarios"""
    servicios_habilitados = []

    # Intentar habilitar WMI
    if habilitar_wmi(computadora):
        servicios_habilitados.append("WMI")
    else:
        logger.warning(f"⚠️ No se pudo habilitar WMI en {computadora}")

    # Intentar habilitar PowerShell Remoting
    if habilitar_powershell_remoting(computadora):
        servicios_habilitados.append("PowerShell Remoting")
    else:
        logger.warning(f"⚠️ No se pudo habilitar PowerShell Remoting en {computadora}")

    # Intentar habilitar Messenger (puede fallar en Windows modernos)
    if habilitar_servicio_messenger(computadora):
        servicios_habilitados.append("Messenger")
    else:
        logger.warning(f"⚠️ No se pudo habilitar Messenger en {computadora}")

    if servicios_habilitados:
        logger.info(f"✅ Servicios habilitados en {computadora}: {', '.join(servicios_habilitados)}")
        return True
    else:
        logger.error(f"❌ No se pudo habilitar ningún servicio en {computadora}")
        return False