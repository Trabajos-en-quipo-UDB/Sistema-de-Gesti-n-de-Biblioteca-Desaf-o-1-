from models.libro import Libro
from models.usuario import Usuario


class GestorBiblioteca:
    """Coordina operaciones basicas de usuarios y libros."""

    @staticmethod
    def _normalizar_id(valor: str | int) -> str:
        return str(valor).strip()

    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._libros: dict[str, Libro] = {}
        self._prestamos: dict[str, str] = {}

    def registrar_usuario(self, usuario: Usuario) -> None:
        if usuario.id in self._usuarios:
            raise ValueError(f"Ya existe un usuario con id {usuario.id}.")
        self._usuarios[usuario.id] = usuario

    def agregar_libro(self, libro: Libro) -> None:
        if libro.id in self._libros:
            raise ValueError(f"Ya existe un libro con id {libro.id}.")
        self._libros[libro.id] = libro

    def prestar_libro(self, id_usuario: str | int, id_libro: str | int) -> None:
        id_usuario_norm = self._normalizar_id(id_usuario)
        id_libro_norm = self._normalizar_id(id_libro)

        usuario = self._usuarios.get(id_usuario_norm)
        libro = self._libros.get(id_libro_norm)

        if usuario is None:
            raise ValueError(f"Usuario {id_usuario_norm} no encontrado.")
        if libro is None:
            raise ValueError(f"Libro {id_libro_norm} no encontrado.")
        if libro.estado == Libro.ESTADO_PRESTADO:
            raise ValueError("El libro no esta disponible.")

        cantidad_prestamos = sum(1 for uid in self._prestamos.values() if uid == id_usuario_norm)
        if cantidad_prestamos >= usuario.max_prestamos:
            raise ValueError("El usuario alcanzo su limite de prestamos.")

        libro.prestar()
        self._prestamos[id_libro_norm] = id_usuario_norm

    def devolver_libro(self, id_libro: str | int) -> None:
        id_libro_norm = self._normalizar_id(id_libro)
        libro = self._libros.get(id_libro_norm)
        if libro is None:
            raise ValueError(f"Libro {id_libro_norm} no encontrado.")
        if libro.estado == Libro.ESTADO_DISPONIBLE:
            raise ValueError("El libro ya esta disponible.")

        libro.devolver()
        self._prestamos.pop(id_libro_norm, None)

    def listar_detalles(self) -> list[str]:
        elementos = [*self._usuarios.values(), *self._libros.values()]
        # Polimorfismo: cada objeto responde a mostrar_detalle segun su clase.
        return [elemento.mostrar_detalle() for elemento in elementos]
