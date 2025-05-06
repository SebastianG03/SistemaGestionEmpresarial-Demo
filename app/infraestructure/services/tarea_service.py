"""
Módulo de servicios para el sistema de gestión de tareas.
Contiene la lógica de negocio para manipular las tareas.
"""
from datetime import datetime
from typing import List, Optional, Dict
import json
import os
from pydantic import ValidationError

from entities.models.tarea import Tarea
from entities.enums.enums import PrioridadEnum, EstadoEnum
from infraestructure.services.log_service import LogManager, Timer


class TareaService:
    """
    Servicio para gestionar las operaciones con tareas.
    
    Proporciona métodos para agregar, buscar, listar y actualizar tareas.
    Implementa validaciones y manejo de errores.
    """
    # Límite máximo de tareas
    MAX_TAREAS = 50000
    
    def __init__(self, log_manager: LogManager):
        """
        Inicializa el servicio con un administrador de logs.
        
        Args:
            log_manager: Instancia de LogManager para registrar operaciones
        """
        self.tareas: Dict[int, Tarea] = {}
        self.log_manager = log_manager
        self.siguiente_id = 1
        # Cargar tareas existentes si hay
        self.cargar_tareas()
    
    def cargar_tareas(self):
        """Carga las tareas desde el archivo de almacenamiento si existe."""
        archivo_tareas = "tareas.json"
        if os.path.exists(archivo_tareas):
            try:
                with open(archivo_tareas, "r", encoding="utf-8") as file:
                    datos = json.load(file)
                    
                    # Procesar el ID máximo
                    if datos.get("siguiente_id"):
                        self.siguiente_id = datos["siguiente_id"]
                    
                    # Procesar las tareas
                    if datos.get("tareas"):
                        for tarea_dict in datos["tareas"]:
                            # Convertir la fecha de string a datetime
                            if "fecha_vencimiento" in tarea_dict:
                                tarea_dict["fecha_vencimiento"] = datetime.fromisoformat(tarea_dict["fecha_vencimiento"])
                            
                            try:
                                tarea = Tarea(**tarea_dict)
                                self.tareas[tarea.id] = tarea
                            except ValidationError as e:
                                self.log_manager.log_error(f"Error al cargar tarea: {e}")
            except Exception as e:
                self.log_manager.log_error(f"Error al cargar tareas: {e}")
                print(f"Error al cargar tareas: {e}")
    
    def guardar_tareas(self):
        """Guarda las tareas en un archivo JSON."""
        archivo_tareas = "tareas.json"
        try:
            # Convertir las tareas a formato serializable
            tareas_serializable = [
                {**tarea.dict(), "fecha_vencimiento": tarea.fecha_vencimiento.isoformat()}
                for tarea in self.tareas.values()
            ]
            
            datos = {
                "siguiente_id": self.siguiente_id,
                "tareas": tareas_serializable
            }
            
            with open(archivo_tareas, "w", encoding="utf-8") as file:
                json.dump(datos, file, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_manager.log_error(f"Error al guardar tareas: {e}")
            print(f"Error al guardar tareas: {e}")
    
    def agregar_tarea(self, titulo: str, descripcion: str, prioridad: str, 
                     fecha_vencimiento: datetime) -> Optional[Tarea]:
        """
        Agrega una nueva tarea al sistema.
        
        Args:
            titulo: Título de la tarea
            descripcion: Descripción detallada
            prioridad: Nivel de prioridad (alta, media, baja)
            fecha_vencimiento: Fecha límite para completar la tarea
        
        Returns:
            La tarea creada si fue exitoso, None si hubo un error
            
        Raises:
            ValueError: Si hay un error de validación en los datos
        """
        with Timer("Agregar tarea", self.log_manager):
            # Verificar límite de tareas
            if len(self.tareas) >= self.MAX_TAREAS:
                mensaje = f"Se ha alcanzado el límite máximo de {self.MAX_TAREAS} tareas"
                self.log_manager.log_error(mensaje)
                raise ValueError(mensaje)
            
            try:
                # Crear la nueva tarea
                nueva_tarea = Tarea(
                    id=self.siguiente_id,
                    titulo=titulo,
                    descripcion=descripcion,
                    prioridad=PrioridadEnum(prioridad.lower()),
                    estado=EstadoEnum.PENDIENTE,
                    fecha_vencimiento=fecha_vencimiento
                )
                
                # Añadir la tarea a la colección
                self.tareas[self.siguiente_id] = nueva_tarea
                self.log_manager.log_data_operation("Tarea agregada", f"ID: {self.siguiente_id}, Título: {titulo}")
                
                # Incrementar el ID para la próxima tarea
                self.siguiente_id += 1
                
                # Guardar los cambios
                self.guardar_tareas()
                
                return nueva_tarea
                
            except ValidationError as e:
                mensaje_error = f"Error de validación: {str(e)}"
                self.log_manager.log_error(mensaje_error)
                raise ValueError(mensaje_error)
            
            except Exception as e:
                mensaje_error = f"Error al agregar tarea: {str(e)}"
                self.log_manager.log_error(mensaje_error)
                raise ValueError(mensaje_error)
    
    def buscar_tarea_por_id(self, tarea_id: int) -> Optional[Tarea]:
        """
        Busca una tarea por su ID.
        
        Args:
            tarea_id: ID de la tarea a buscar
        
        Returns:
            La tarea encontrada o None si no existe
        """
        with Timer("Buscar tarea por ID", self.log_manager):
            return self.tareas.get(tarea_id)
    
    def listar_tareas_por_prioridad(self, ascendente: bool = True) -> List[Tarea]:
        """
        Lista todas las tareas ordenadas por prioridad.
        
        Args:
            ascendente: Si es True, ordena de menor a mayor prioridad (baja a alta)
                        Si es False, ordena de mayor a menor prioridad (alta a baja)
        
        Returns:
            Lista de tareas ordenadas por prioridad
        """
        with Timer("Listar tareas por prioridad", self.log_manager):
            # Mapeo de prioridades a valores numéricos para ordenamiento
            prioridad_valor = {
                PrioridadEnum.BAJA: 1,
                PrioridadEnum.MEDIA: 2,
                PrioridadEnum.ALTA: 3
            }
            
            # Obtener todas las tareas como una lista
            tareas_lista = list(self.tareas.values())
            
            # Ordenar según el criterio
            if ascendente:
                # Ordenar de menor a mayor prioridad (baja -> alta)
                tareas_ordenadas = sorted(tareas_lista, key=lambda t: prioridad_valor[t.prioridad])
            else:
                # Ordenar de mayor a menor prioridad (alta -> baja)
                tareas_ordenadas = sorted(tareas_lista, key=lambda t: prioridad_valor[t.prioridad], reverse=True)
            
            return tareas_ordenadas
    
    def listar_tareas_por_vencimiento(self) -> List[Tarea]:
        """
        Lista todas las tareas ordenadas por fecha de vencimiento, 
        con las más próximas a vencer primero.
        
        Returns:
            Lista de tareas ordenadas por fecha de vencimiento
        """
        with Timer("Listar tareas por vencimiento", self.log_manager):
            # Filtrar solo tareas no completadas y ordenar por fecha de vencimiento
            tareas_pendientes = [tarea for tarea in self.tareas.values() 
                                if tarea.estado != EstadoEnum.COMPLETADA]
            
            return sorted(tareas_pendientes, key=lambda t: t.fecha_vencimiento)
    
    def actualizar_estado_tarea(self, tarea_id: int, nuevo_estado: str) -> Optional[Tarea]:
        """
        Actualiza el estado de una tarea.
        
        Args:
            tarea_id: ID de la tarea a actualizar
            nuevo_estado: Nuevo estado para la tarea
        
        Returns:
            La tarea actualizada o None si no se encontró
            
        Raises:
            ValueError: Si el estado proporcionado no es válido
        """
        with Timer("Actualizar estado de tarea", self.log_manager):
            # Verificar que la tarea existe
            tarea = self.tareas.get(tarea_id)
            if not tarea:
                return None
            
            try:
                # Validar y actualizar el estado
                estado_enum = EstadoEnum(nuevo_estado.lower())
                tarea.estado = estado_enum
                
                # Registrar la operación
                self.log_manager.log_data_operation(
                    "Estado de tarea actualizado", 
                    f"ID: {tarea_id}, Nuevo estado: {nuevo_estado}"
                )
                
                # Guardar los cambios
                self.guardar_tareas()
                
                return tarea
                
            except ValueError:
                mensaje_error = f"Estado no válido: {nuevo_estado}"
                self.log_manager.log_error(mensaje_error)
                raise ValueError(mensaje_error)