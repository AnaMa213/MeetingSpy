import logging
from logging.config import dictConfig


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors based on log levels.
    """
    # Couleurs ANSI pour différents niveaux de log
    COLORS = {
        "DEBUG": "\033[94m",  # Bleu clair
        "INFO": "\033[92m",   # Vert
        "WARNING": "\033[93m", # Jaune
        "ERROR": "\033[91m",   # Rouge
        "CRITICAL": "\033[95m", # Violet
    }
    RESET = "\033[0m"  # Réinitialisation de la couleur

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)
    

def setup_logging():
    """
    Configure the logging settings for the application.

    This function sets up the logging configuration using a dictionary-based
    approach. It defines two formatters: a colored formatter for console output
    and a default formatter for file output. The logging handlers include a 
    console handler that uses ANSI color codes to highlight log levels, and a 
    file handler that writes log messages to 'application.log'. The root logger
    is configured to capture log messages at the DEBUG level and higher.
    """
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",  # Utiliser le formatteur avec couleurs
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "application.log",
                "mode": "a",
                "formatter": "default",  # Pas de couleurs dans les fichiers
            },
        },
        "root": {
            "level": "DEBUG",  # Capturer tous les logs DEBUG et supérieurs
            "handlers": ["console", "file"],
        },
    })

    logging.getLogger().info("Logging is configured.")
    logging.getLogger().debug("Logging DEBUG is configured.")
