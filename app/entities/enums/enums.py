from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator


class PrioridadEnum(str, Enum):
    """Enumeración para los posibles valores de prioridad de una tarea."""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoEnum(str, Enum):
    """Enumeración para los posibles estados de una tarea."""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en progreso"
    COMPLETADA = "completada"