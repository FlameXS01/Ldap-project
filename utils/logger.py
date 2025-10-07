import logging
import sys
from pathlib import Path
from config.settings import settings

def setup_logger(name: str = None) -> logging.Logger:
    """
    Configura y retorna un logger con formato consistente
    
    Args:
        name: Nombre del logger (usualemente __name__)
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name or __name__)
    
    # Evitar múltiples handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger