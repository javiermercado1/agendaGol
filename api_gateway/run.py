import uvicorn
import os
import sys
import logging
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from app.config import settings

def setup_logging():
    """Configurar logging"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('gateway.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
        ]
    )

def main():
    """Función principal"""
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting API Gateway on {settings.gateway_host}:{settings.gateway_port}")
    logger.info(f"Services configuration: {list(settings.__dict__.keys())}")
    
    # Configuración de uvicorn
    config = {
        "app": "app.main:app",
        "host": settings.gateway_host,
        "port": settings.gateway_port,
        "workers": settings.gateway_workers,
        "log_level": settings.log_level.lower(),
        "access_log": True,
        "reload": os.getenv("DEVELOPMENT", "false").lower() == "true"
    }
    
    uvicorn.run(**config)

if __name__ == "__main__":
    main()
