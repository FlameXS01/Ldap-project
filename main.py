import sys
from services.inventory_service import InventoryService
from services.user_service import UserService
from utils.logger import setup_logger

# Logger para el módulo principal
logger = setup_logger(__name__)

def main():
    """Función principal de la aplicación"""

    inventory_service = InventoryService()
    user_service = UserService()

    def salir():
        print("\n👋 Saliendo del sistema...")
        logger.info("Aplicación cerrada por el usuario")
        sys.exit(0)
    
    def env_sms():
        print("\n" + "=" * 60)
        pc_name = input('Diga el nombre de la pc a enviar el sms: ')
        sms = input('Entre el mensaje a enviar: ')
        iss=inventory_service.envio_forzado(pc_name, sms)


    opciones = {
        1: inventory_service.activas_en_fecha,  # lastLogon con filtro
        2: inventory_service.listar_ordenadores,# todas las PC
        3: user_service.activos_en_fecha,       # por implementar
        4: user_service.listar_usuarios,  
        5: env_sms,                             # por implementar
        0: salir                                # función local para salir
    }


    print("=" * 60)
    con = True

    while con:
        print("\n" + "=" * 60)
        print("🎯 SISTEMA DE LDAP")
        print("=" * 60)
        print("Seleccionar 1 para Last Logon (equipos activos en fecha)")
        print("Seleccionar 2 para todas las PC")
        print("Seleccionar 3 para Last Logon Usuarios en fecha")
        print("Seleccionar 4 para todos los usuarios")
        print("Seleccionar 5 para mandar un sms")
        print("Seleccionar 0 para salir")
        print("=" * 60)

        try:
            op = int(input("👉 Seleccione una opción: "))

            if op in opciones:
                # Ejecutar la función correspondiente
                opciones[op]()
            else:
                print(f"\n❌ ERROR: Opción {op} no válida")
                print("Por favor, seleccione una opción entre 0 y 5")

        except ValueError:
            print(f"\n❌ ERROR: No es un número válido")
            print("Por favor, ingrese un número entre 0 y 5")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Aplicación interrumpida por el usuario")
            logger.info("Aplicación interrumpida por el usuario (Ctrl+C)")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n💥 ERROR inesperado: {e}")
            logger.error(f"Error en menú principal: {e}", exc_info=True)

if __name__ == "__main__":
    main()