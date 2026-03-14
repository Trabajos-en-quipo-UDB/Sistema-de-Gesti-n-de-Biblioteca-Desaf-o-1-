from models.libro import Libro
from models.usuario import Usuario


class GestorBiblioteca:
    """Coordina operaciones basicas de usuarios y libros."""

    def __init__(self) -> None:
        self._usuarios: dict[int, Usuario] = {}
        self._libros: dict[int, Libro] = {}
        self._prestamos: dict[int, int] = {}

    def registrar_usuario(self, usuario: Usuario) -> None:
        if usuario.id in self._usuarios:
            raise ValueError(f"Ya existe un usuario con id {usuario.id}.")
        self._usuarios[usuario.id] = usuario

    def agregar_libro(self, libro: Libro) -> None:
        if libro.id in self._libros:
            raise ValueError(f"Ya existe un libro con id {libro.id}.")
        self._libros[libro.id] = libro

    def prestar_libro(self, id_usuario: int, id_libro: int) -> None:
        usuario = self._usuarios.get(id_usuario)
        libro = self._libros.get(id_libro)

        if usuario is None:
            raise ValueError(f"Usuario {id_usuario} no encontrado.")
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")
        if libro.estado == Libro.ESTADO_PRESTADO:
            raise ValueError("El libro no esta disponible.")

        cantidad_prestamos = sum(1 for uid in self._prestamos.values() if uid == id_usuario)
        if cantidad_prestamos >= usuario.max_prestamos:
            raise ValueError("El usuario alcanzo su limite de prestamos.")

        libro.prestar()
        self._prestamos[id_libro] = id_usuario

    def devolver_libro(self, id_libro: int) -> None:
        libro = self._libros.get(id_libro)
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")
        if libro.estado == Libro.ESTADO_DISPONIBLE:
            raise ValueError("El libro ya esta disponible.")

        libro.devolver()
        self._prestamos.pop(id_libro, None)

    def listar_detalles(self) -> list[str]:
        elementos = [*self._usuarios.values(), *self._libros.values()]
        # Polimorfismo: cada objeto responde a mostrar_detalle segun su clase.
        return [elemento.mostrar_detalle() for elemento in elementos]
