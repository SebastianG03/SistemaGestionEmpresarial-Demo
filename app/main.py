"""
Programa principal del sistema de gestión de tareas.
Maneja la interfaz de usuario y la interacción con los servicios.
"""
import os
import sys
from datetime import datetime
from typing import Optional

from entities.models.tarea import Tarea
from entities.enums.enums import PrioridadEnum, EstadoEnum
from infraestructure.services.tarea_service import TareaService
from infraestructure.services.log_service import LogManager, Timer


class SistemaTareas:
    """
    Clase principal que maneja la interfaz de usuario del sistema de tareas.
    """
    
    def __init__(self):
        """Inicializa el sistema de tareas."""
        self.log_manager = LogManager()
        self.tarea_service = TareaService(self.log_manager)
        self.ejecutando = True
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_banner(self):
        """Muestra un banner decorativo para el sistema."""
        print("=" * 60)
        print("           SISTEMA DE GESTIÓN DE TAREAS")
        print("=" * 60)
        print()
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema."""
        self.limpiar_pantalla()
        self.mostrar_banner()
        
        print("1. Agregar nueva tarea")
        print("2. Buscar tarea por ID")
        print("3. Listar tareas por prioridad")
        print("4. Listar tareas próximas a vencer")
        print("5. Actualizar estado de una tarea")
        print("0. Salir")
        print()
        
        return self.obtener_opcion("Seleccione una opción: ", rango_valido=range(6))
    
    def obtener_opcion(self, mensaje: str, rango_valido=None) -> int:
        """
        Solicita al usuario una opción numérica.
        
        Args:
            mensaje: Texto a mostrar al usuario
            rango_valido: Rango de valores aceptables
        
        Returns:
            Opción numérica seleccionada
        """
        while True:
            try:
                opcion = input(mensaje)
                valor = int(opcion)
                
                if rango_valido is not None and valor not in rango_valido:
                    print(f"Error: Debe ingresar un número entre {min(rango_valido)} y {max(rango_valido)}")
                    continue
                    
                return valor
            except ValueError:
                self.log_manager.log_error(f"Entrada inválida: {opcion}")
                print("Error: Debe ingresar un número válido")
    
    def obtener_fecha(self, mensaje: str) -> datetime:
        """
        Solicita al usuario una fecha.
        
        Args:
            mensaje: Texto a mostrar al usuario
        
        Returns:
            Objeto datetime con la fecha ingresada
        """
        while True:
            try:
                fecha_str = input(mensaje + " (YYYY-MM-DD HH:MM): ")
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                
                # Validar que la fecha no sea en el pasado
                if fecha < datetime.now():
                    print("Error: La fecha no puede ser en el pasado")
                    continue
                    
                return fecha
            except ValueError:
                self.log_manager.log_error(f"Formato de fecha inválido: {fecha_str}")
                print("Error: Formato de fecha inválido. Use YYYY-MM-DD HH:MM")
    
    def mostrar_tarea(self, tarea: Tarea):
        """
        Muestra los detalles de una tarea.
        
        Args:
            tarea: Tarea a mostrar
        """
        print("\n" + "-" * 50)
        print(f"ID: {tarea.id}")
        print(f"Título: {tarea.titulo}")
        print(f"Descripción: {tarea.descripcion}")
        print(f"Prioridad: {tarea.prioridad.value}")
        print(f"Estado: {tarea.estado.value}")
        print(f"Fecha de vencimiento: {tarea.fecha_vencimiento.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 50 + "\n")
    
    def agregar_tarea(self):
        """Gestiona el proceso de agregar una nueva tarea."""
        self.limpiar_pantalla()
        print("=== AGREGAR NUEVA TAREA ===\n")
        
        try:
            # Solicitar datos de la tarea
            titulo = input("Título (máx. 70 caracteres): ")
            descripcion = input("Descripción: ")
            
            print("\nPrioridad:")
            print("1. Alta")
            print("2. Media")
            print("3. Baja")
            opcion_prioridad = self.obtener_opcion("Seleccione la prioridad: ", range(1, 4))
            
            # Mapear opción a valor de prioridad
            prioridades = ["alta", "media", "baja"]
            prioridad = prioridades[opcion_prioridad - 1]
            
            # Obtener fecha de vencimiento
            fecha_vencimiento = self.obtener_fecha("Fecha de vencimiento")
            
            # Intentar crear la tarea
            with Timer("Agregar tarea (interfaz)", self.log_manager):
                nueva_tarea = self.tarea_service.agregar_tarea(
                    titulo, descripcion, prioridad, fecha_vencimiento
                )
                
                print("\n¡Tarea agregada con éxito!")
                self.mostrar_tarea(nueva_tarea)
        
        except ValueError as e:
            print(f"\nError: {str(e)}")
        
        input("\nPresione Enter para continuar...")
    
    def buscar_tarea(self):
        """Gestiona el proceso de búsqueda de una tarea por ID."""
        self.limpiar_pantalla()
        print("=== BUSCAR TAREA POR ID ===\n")
        
        try:
            tarea_id = self.obtener_opcion("Ingrese el ID de la tarea: ")
            
            with Timer("Buscar tarea (interfaz)", self.log_manager):
                tarea = self.tarea_service.buscar_tarea_por_id(tarea_id)
                
                if tarea:
                    print("\nTarea encontrada:")
                    self.mostrar_tarea(tarea)
                else:
                    print(f"\nNo se encontró ninguna tarea con ID {tarea_id}")
        
        except ValueError as e:
            print(f"\nError: {str(e)}")
        
        input("\nPresione Enter para continuar...")
    
    def listar_tareas_por_prioridad(self):
        """Gestiona el proceso de listar tareas por prioridad."""
        self.limpiar_pantalla()
        print("=== LISTAR TAREAS POR PRIORIDAD ===\n")
        
        print("Orden de prioridad:")
        print("1. Ascendente (Baja → Media → Alta)")
        print("2. Descendente (Alta → Media → Baja)")
        opcion = self.obtener_opcion("Seleccione el orden: ", range(1, 3))
        
        ascendente = opcion == 1
        
        with Timer("Listar tareas por prioridad (interfaz)", self.log_manager):
            tareas = self.tarea_service.listar_tareas_por_prioridad(ascendente)
            
            if not tareas:
                print("\nNo hay tareas registradas en el sistema")
            else:
                print(f"\nSe encontraron {len(tareas)} tareas:")
                for tarea in tareas:
                    self.mostrar_tarea(tarea)
        
        input("\nPresione Enter para continuar...")
    
    def listar_tareas_por_vencimiento(self):
        """Gestiona el proceso de listar tareas próximas a vencer."""
        self.limpiar_pantalla()
        print("=== LISTAR TAREAS PRÓXIMAS A VENCER ===\n")
        
        with Timer("Listar tareas por vencimiento (interfaz)", self.log_manager):
            tareas = self.tarea_service.listar_tareas_por_vencimiento()
            
            if not tareas:
                print("\nNo hay tareas pendientes o en progreso")
            else:
                print(f"\nSe encontraron {len(tareas)} tareas pendientes o en progreso:")
                for tarea in tareas:
                    self.mostrar_tarea(tarea)
        
        input("\nPresione Enter para continuar...")
    
    def actualizar_estado_tarea(self):
        """Gestiona el proceso de actualización del estado de una tarea."""
        self.limpiar_pantalla()
        print("=== ACTUALIZAR ESTADO DE TAREA ===\n")
        
        try:
            tarea_id = self.obtener_opcion("Ingrese el ID de la tarea: ")
            
            # Verificar que la tarea existe
            tarea = self.tarea_service.buscar_tarea_por_id(tarea_id)
            if not tarea:
                print(f"\nNo se encontró ninguna tarea con ID {tarea_id}")
                input("\nPresione Enter para continuar...")
                return
            
            # Mostrar la tarea actual
            print("\nTarea actual:")
            self.mostrar_tarea(tarea)
            
            # Solicitar el nuevo estado
            print("\nSeleccione el nuevo estado:")
            print("1. Pendiente")
            print("2. En progreso")
            print("3. Completada")
            opcion_estado = self.obtener_opcion("Seleccione el estado: ", range(1, 4))
            
            # Mapear opción a valor de estado
            estados = ["pendiente", "en progreso", "completada"]
            nuevo_estado = estados[opcion_estado - 1]
            
            # Actualizar el estado
            with Timer("Actualizar estado (interfaz)", self.log_manager):
                tarea_actualizada = self.tarea_service.actualizar_estado_tarea(tarea_id, nuevo_estado)
                
                print("\n¡Estado actualizado con éxito!")
                self.mostrar_tarea(tarea_actualizada)
        
        except ValueError as e:
            print(f"\nError: {str(e)}")
        
        input("\nPresione Enter para continuar...")
    
    def ejecutar(self):
        """Ejecuta el bucle principal del programa."""
        try:
            while self.ejecutando:
                opcion = self.mostrar_menu_principal()
                
                if opcion == 0:
                    # Salir
                    self.ejecutando = False
                    print("\n¡Gracias por usar el Sistema de Gestión de Tareas!")
                elif opcion == 1:
                    # Agregar tarea
                    self.agregar_tarea()
                elif opcion == 2:
                    # Buscar tarea
                    self.buscar_tarea()
                elif opcion == 3:
                    # Listar por prioridad
                    self.listar_tareas_por_prioridad()
                elif opcion == 4:
                    # Listar por vencimiento
                    self.listar_tareas_por_vencimiento()
                elif opcion == 5:
                    # Actualizar estado
                    self.actualizar_estado_tarea()
        
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido por el usuario")
        except Exception as e:
            print(f"\nError inesperado: {str(e)}")
            self.log_manager.log_error(f"Error inesperado: {str(e)}")
        finally:
            print("\n¡Hasta pronto!")


if __name__ == "__main__":
    sistema = SistemaTareas()
    sistema.ejecutar()