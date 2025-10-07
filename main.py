from services.inventory_service import InventoryService

def main():
    inventory_service = InventoryService()
    inventory_service.generar_inventario()

if __name__ == "__main__":
    main()