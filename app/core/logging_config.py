import logging
import sys
from pathlib import Path


def setup_logging():
    """Configura el sistema de logging para toda la aplicación"""

    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configuración del formato
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # Escribir a archivo
            logging.FileHandler("logs/app.log"),
            # Mostrar en consola
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Configurar nivel para uvicorn
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
