# Responsable: Yajaira Aldana - Líder de Proyecto y Arquitecta

"""Modelo de libro del dominio biblioteca.

Encapsulamiento:
Todos los atributos internos se definen como privados para proteger el estado.
El uso de @property permite validar cada cambio y mantener reglas de negocio.

Polimorfismo:
Implementa `obtener_detalle()` con una salida especializada para objetos Libro.
"""

from __future__ import annotations

import re

class Libro:
    """Entidad de libro con metadatos bibliograficos y estado de circulacion."""

    ESTADO_DISPONIBLE = "disponible"
    ESTADO_PRESTADO = "prestado"

    _ID_REGEX = re.compile(r"^(?=.*[A-Za-z0-9])[A-Za-z0-9-]+$")

    def __init__(self, id_libro: str | int, titulo: str, autor: str, anio: int) -> None:
        """Inicializa un libro en estado disponible por defecto.

        Args:
            id_libro: Identificador unico del libro.
            titulo: Titulo principal.
            autor: Autor o autora de la obra.
            anio: Anio de publicacion.
        """
        self.id = id_libro
        self.__titulo = titulo
        self.__autor = autor
        self.__anio = anio
        self.__estado = self.ESTADO_DISPONIBLE

    @property
    def id(self) -> str:
        """Retorna el identificador encapsulado del libro."""
        return self.__id

    @id.setter
    def id(self, value: str | int) -> None:
        """Actualiza el ID validando formato (letras, numeros y guion '-')."""
        texto = str(value).strip()
        if not texto:
            raise ValueError("El id del libro es obligatorio.")
        if not self._ID_REGEX.fullmatch(texto):
            raise ValueError("ID invalido. Use letras, numeros y guion '-'. Ej: RO-253385")
        self.__id = texto

    @property
    def titulo(self) -> str:
        """Retorna el titulo del libro."""
        return self.__titulo

    @titulo.setter
    def titulo(self, value: str) -> None:
        """Actualiza el titulo validando dato obligatorio no vacio."""
        if not value or not value.strip():
            raise ValueError("El titulo no puede estar vacio.")
        self.__titulo = value.strip()

    @property
    def autor(self) -> str:
        """Retorna el autor del libro."""
        return self.__autor

    @autor.setter
    def autor(self, value: str) -> None:
        """Actualiza el autor validando dato obligatorio no vacio."""
        if not value or not value.strip():
            raise ValueError("El autor no puede estar vacio.")
        self.__autor = value.strip()

    @property
    def anio(self) -> int:
        """Retorna el anio de publicacion."""
        return self.__anio

    @anio.setter
    def anio(self, value: int) -> None:
        """Actualiza el anio validando que sea mayor a cero."""
        if value <= 0:
            raise ValueError("El anio debe ser mayor que 0.")
        self.__anio = value

    @property
    def estado(self) -> str:
        """Retorna el estado de disponibilidad del libro."""
        return self.__estado

    @estado.setter
    def estado(self, value: str) -> None:
        """Actualiza el estado aplicando valores permitidos de negocio."""
        estados_validos = {self.ESTADO_DISPONIBLE, self.ESTADO_PRESTADO}
        if value not in estados_validos:
            raise ValueError("Estado invalido. Use 'disponible' o 'prestado'.")
        self.__estado = value

    def prestar(self) -> None:
        """Marca el libro como prestado si actualmente esta disponible."""
        if self.estado == self.ESTADO_PRESTADO:
            raise ValueError("El libro ya esta prestado.")
        self.estado = self.ESTADO_PRESTADO

    def devolver(self) -> None:
        """Marca el libro como disponible si actualmente esta prestado."""
        if self.estado == self.ESTADO_DISPONIBLE:
            raise ValueError("El libro ya esta disponible.")
        self.estado = self.ESTADO_DISPONIBLE

    def obtener_detalle(self) -> str:
        """Devuelve detalle especializado de Libro (polimorfismo)."""
        return (
            f"Libro(id={self.id}, titulo='{self.titulo}', autor='{self.autor}', "
            f"anio={self.anio}, estado='{self.estado}')"
        )

    def mostrar_detalle(self) -> str:
        """Alias para mantener compatibilidad con llamadas existentes."""
        return self.obtener_detalle()
