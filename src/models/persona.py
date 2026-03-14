# Responsable: Yajaira Aldana - Líder de Proyecto y Arquitecta

"""Modelo base de personas.

Este modulo establece la base de la jerarquia de usuarios del sistema.
Aplica Encapsulamiento mediante atributos privados y usa @property
para exponer acceso controlado (lectura/escritura con validacion).
"""

from __future__ import annotations

from abc import ABC

import re


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

    _ID_REGEX = re.compile(r"^(?=.*[A-Za-z0-9])[A-Za-z0-9-]+$")

    def __init__(self, id_persona: str | int, nombre: str) -> None:
        """Inicializa una persona con identificador y nombre validados por setters.

        Args:
            id_persona: Identificador unico de la persona.
            nombre: Nombre completo o visible en la aplicacion.
        """
        self.id = id_persona
        self.__nombre = nombre

    @property
    def id(self) -> str:
        """Obtiene el ID encapsulado de la persona.

        @property se usa para exponer lectura segura sin romper el encapsulamiento.
        """
        return self.__id

    @id.setter
    def id(self, value: str | int) -> None:
        """Actualiza el ID validando formato (letras, numeros y guion '-')."""
        texto = str(value).strip()
        if not texto:
            raise ValueError("El id es obligatorio.")
        if not self._ID_REGEX.fullmatch(texto):
            raise ValueError("ID invalido. Use letras, numeros y guion '-'. Ej: RO-253385")
        self.__id = texto

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
