import sys
from services.inventory_service import InventoryService
from utils.logger import setup_logger

# Logger para el módulo principal
logger = setup_logger(__name__)

def main():
    """Función principal de la aplicación"""
    try:
        logger.info("🎯 Iniciando aplicación de inventario LDAP")
        
        inventory_service = InventoryService()
        exito = inventory_service.generar_inventario()
        
        if exito:
            logger.info("🎊 Proceso completado exitosamente")
            sys.exit(0)
        else:
            logger.error("💥 Proceso completado con errores")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"💥 Error crítico no manejado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()