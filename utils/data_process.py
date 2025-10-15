import os

def cargar_equipos_desde_archivo():
    """
    Carga los nombres de equipos desde un archivo de texto
    Retorna una lista con los nombres
    """

    nombre_archivo="data.txt"
    equipos = []
    
    try:
        # Obtener la ruta del directorio donde está este script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(directorio_actual, nombre_archivo)
        
        
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                equipo = linea.strip()
                if equipo: 
                    equipos.append(equipo)
        
        print(f"✅ Se cargaron {len(equipos)} equipos desde: {nombre_archivo}")
        return equipos
        
    except FileNotFoundError:
        print(f"❌ El archivo '{ruta_archivo}' no existe")
        # Mostrar archivos en el directorio para debug
        archivos = os.listdir(directorio_actual)
        print(f"📁 Archivos en el directorio: {archivos}")
        return []
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return []



