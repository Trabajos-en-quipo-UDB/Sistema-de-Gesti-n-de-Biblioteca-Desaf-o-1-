# Responsable: Yajaira Aldana - Líder de Proyecto y Arquitecta

"""Modelo base de personas.

Este modulo establece la base de la jerarquia de usuarios del sistema.
Aplica Encapsulamiento mediante atributos privados y usa @property
para exponer acceso controlado (lectura/escritura con validacion).
"""

from abc import ABC


class Persona(ABC):
    """Clase base para entidades tipo persona.

    Herencia:
    Esta clase se utiliza como superclase de modelos concretos, por ejemplo `Usuario`.

    Encapsulamiento:
    Los atributos `__id` y `__nombre` son privados para evitar modificaciones directas
    que rompan reglas de negocio. El acceso se realiza con @property para validar
    datos y mantener consistencia del dominio.

    Polimorfismo:
    Define `obtener_detalle()` como comportamiento general que puede ser
    sobreescrito por subclases para devolver representaciones especializadas.
    """

    def __init__(self, id_persona: int, nombre: str) -> None:
        """Inicializa una persona con identificador y nombre validados por setters.

        Args:
            id_persona: Identificador unico de la persona.
            nombre: Nombre completo o visible en la aplicacion.
        """
        self.__id = id_persona
        self.__nombre = nombre

    @property
    def id(self) -> int:
        """Obtiene el ID encapsulado de la persona.

        @property se usa para exponer lectura segura sin romper el encapsulamiento.
        """
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        """Actualiza el ID validando que sea un entero positivo.

        Se usa setter para centralizar reglas de integridad de datos.
        """
        if value <= 0:
            raise ValueError("El id debe ser mayor que 0.")
        self.__id = value

    @property
    def nombre(self) -> str:
        """Obtiene el nombre encapsulado de la persona."""
        return self.__nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        """Actualiza el nombre evitando valores vacios o con solo espacios."""
        if not value or not value.strip():
            raise ValueError("El nombre no puede estar vacio.")
        self.__nombre = value.strip()

    def obtener_detalle(self) -> str:
        """Devuelve una descripcion general de la persona.

        Este metodo es el punto de extension polimorfico. Las subclases pueden
        sobreescribirlo para mostrar campos propios sin cambiar el codigo cliente.
        """
        return f"Persona(id={self.id}, nombre='{self.nombre}')"

    def mostrar_detalle(self) -> str:
        """Alias de compatibilidad para codigo legado.

        Permite mantener llamadas existentes a `mostrar_detalle()` reutilizando
        la implementacion actual de `obtener_detalle()`.
        """
        return self.obtener_detalle()
