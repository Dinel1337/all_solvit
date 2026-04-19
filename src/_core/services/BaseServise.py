import logging
from src.config import DEBUG

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GREY = '\033[90m'

class ColoredFormatter(logging.Formatter):
    """Форматтер с цветами для разных уровней"""
    
    def format(self, record):
        level_color = {
            logging.DEBUG: Colors.GREY,
            logging.INFO: Colors.GREEN,
            logging.WARNING: Colors.YELLOW,
            logging.ERROR: Colors.RED,
            logging.CRITICAL: Colors.RED + Colors.RESET + Colors.RED
        }.get(record.levelno, Colors.RESET)
        
        name_color = Colors.CYAN
        
        original_msg = record.msg
        original_name = record.name
        
        record.name = f"{name_color}{original_name}{Colors.RESET}"
        record.msg = f"{level_color}{original_msg}{Colors.RESET}"
        
        result = super().format(record)
        
        record.name = original_name
        record.msg = original_msg
        
        return result


class LoggerService:
    """Базовый сервис с красивым логгером"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            level = logging.INFO if DEBUG else logging.ERROR
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(level)
            self.logger.propagate = False