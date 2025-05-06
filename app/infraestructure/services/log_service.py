"""
Módulo de utilidades para el sistema de gestión de tareas.
Contiene funciones para manejar logs y medición de tiempo.
"""
import time
import os
from datetime import datetime


class LogManager:
    """
    Gestor de logs para el sistema.
    Permite registrar acciones, errores y advertencias en archivos diferentes.
    """
    
    def __init__(self):
        """Inicializa las rutas de los archivos de log."""
        self.log_dir = "logs"
        self.ensure_log_directory_exists()
        self.action_log_path = os.path.join(self.log_dir, "acciones.log")
        self.error_log_path = os.path.join(self.log_dir, "errores.log")
        self.data_log_path = os.path.join(self.log_dir, "datos.log")
    
    def ensure_log_directory_exists(self):
        """Asegura que el directorio de logs exista."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_action(self, action, duration_ms):
        """
        Registra una acción realizada y su duración.
        
        Args:
            action: Descripción de la acción
            duration_ms: Duración en milisegundos
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Acción: {action} - Duración: {duration_ms:.2f} ms\n"
        
        with open(self.action_log_path, "a", encoding="utf-8") as file:
            file.write(log_entry)
    
    def log_error(self, error_message):
        """
        Registra un error ocurrido.
        
        Args:
            error_message: Mensaje descriptivo del error
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - ERROR: {error_message}\n"
        
        with open(self.error_log_path, "a", encoding="utf-8") as file:
            file.write(log_entry)
    
    def log_data_operation(self, operation, data_info):
        """
        Registra operaciones con datos.
        
        Args:
            operation: Tipo de operación realizada
            data_info: Información sobre los datos afectados
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {operation}: {data_info}\n"
        
        with open(self.data_log_path, "a", encoding="utf-8") as file:
            file.write(log_entry)


class Timer:
    """
    Clase para medir el tiempo de ejecución de operaciones.
    Utiliza un context manager para facilitar su uso.
    """
    
    def __init__(self, action, log_manager):
        """
        Inicializa el temporizador.
        
        Args:
            action: Descripción de la acción a medir
            log_manager: Instancia de LogManager para registrar los tiempos
        """
        self.action = action
        self.log_manager = log_manager
        self.start_time = None
    
    def __enter__(self):
        """Inicia el cronómetro al entrar en el contexto."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Calcula el tiempo transcurrido al salir del contexto y lo registra.
        
        Args:
            exc_type: Tipo de excepción, si ocurrió alguna
            exc_val: Valor de la excepción, si ocurrió alguna
            exc_tb: Traceback de la excepción, si ocurrió alguna
        """
        duration_ms = (time.time() - self.start_time) * 1000
        self.log_manager.log_action(self.action, duration_ms)
        # Si el tiempo es mayor a un segundo, mostrar advertencia
        if duration_ms > 1000:
            print(f"¡Advertencia! La acción '{self.action}' tomó más de 1 segundo ({duration_ms:.2f} ms)")