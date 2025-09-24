
import logging
from logging.handlers import RotatingFileHandler
import uvicorn
from app.main import app

# Setup file logging
log_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
)

file_handler = RotatingFileHandler(
    'logs/backend.log', 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Add file handler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5200,
        reload=True,
        access_log=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelprefix)s %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "formatter": "default", 
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/backend.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default", "file"],
            },
        }
    )
