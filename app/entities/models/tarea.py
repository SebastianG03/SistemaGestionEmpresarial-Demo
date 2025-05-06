from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from entities.enums.enums import PrioridadEnum, EstadoEnum

class Tarea(BaseModel):
    """
    Modelo de datos para una tarea.
    
    Atributos:
        id: Identificador único de la tarea
        titulo: Título descriptivo de la tarea (máximo 70 caracteres)
        descripcion: Descripción detallada de la tarea
        prioridad: Nivel de prioridad (alta, media, baja)
        estado: Estado actual de la tarea (pendiente, en progreso, completada)
        fecha_vencimiento: Fecha límite para completar la tarea
    """
    id: int
    titulo: str = Field(..., max_length=70)
    descripcion: str
    prioridad: PrioridadEnum
    estado: EstadoEnum = EstadoEnum.PENDIENTE
    fecha_vencimiento: datetime
    
    @field_validator('titulo')
    def titulo_no_vacio(cls, v):
        """Valida que el título no esté vacío."""
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v
    
    @field_validator('fecha_vencimiento')
    def fecha_valida(cls, v):
        """Valida que la fecha de vencimiento sea válida."""
        if v < datetime.now():
            raise ValueError("La fecha de vencimiento no puede ser en el pasado")
        return v
    
    class Config:
        """Configuración del modelo."""
        schema_extra = {
            "example": {
                "id": 1,
                "titulo": "Completar informe trimestral",
                "descripcion": "Finalizar el informe financiero del Q3",
                "prioridad": "alta",
                "estado": "pendiente",
                "fecha_vencimiento": "2025-05-15T23:59:59"
            }
        }