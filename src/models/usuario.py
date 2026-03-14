# Responsable: Yajaira Aldana - Líder de Proyecto y Arquitecta

"""Modelo de usuario.

Demuestra Herencia al extender `Persona`, Encapsulamiento con atributos privados
y Polimorfismo al sobreescribir `obtener_detalle()`.
"""

from models.persona import Persona


class Usuario(Persona):
    """Entidad concreta de usuario del sistema.

    Herencia:
    Reutiliza identidad y nombre desde `Persona`.

    Encapsulamiento:
    Mantiene `__max_prestamos` como privado, exponiendolo con @property para
    aplicar validaciones al actualizar el limite permitido.
    """

    def __init__(self, id_persona: int, nombre: str, max_prestamos: int = 3) -> None:
        """Crea un usuario con limite maximo de prestamos.

        Args:
            id_persona: Identificador unico heredado de Persona.
            nombre: Nombre visible del usuario.
            max_prestamos: Cupo maximo de libros prestados en simultaneo.
        """
        super().__init__(id_persona, nombre)
        self.__max_prestamos = max_prestamos

    @property
    def max_prestamos(self) -> int:
        """Retorna el limite de prestamos del usuario."""
        return self.__max_prestamos

    @max_prestamos.setter
    def max_prestamos(self, value: int) -> None:
        """Actualiza el limite de prestamos validando que sea mayor que cero."""
        if value <= 0:
            raise ValueError("max_prestamos debe ser mayor que 0.")
        self.__max_prestamos = value

    def obtener_detalle(self) -> str:
        """Sobreescribe el detalle general con informacion especifica de Usuario.

        Polimorfismo:
        Codigo cliente puede invocar el mismo metodo en distintos modelos
        (`Persona`, `Usuario`, `Libro`) y obtener salidas adaptadas a cada clase.
        """
        return (
            f"Usuario(id={self.id}, nombre='{self.nombre}', "
            f"max_prestamos={self.max_prestamos})"
        )

    def mostrar_detalle(self) -> str:
        """Mantiene compatibilidad de nombre de metodo con versiones anteriores."""
        return self.obtener_detalle()
