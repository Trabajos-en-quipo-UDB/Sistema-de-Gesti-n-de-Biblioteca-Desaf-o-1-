from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.libro import Libro
from models.usuario import Usuario


def cargar_json(ruta: Path, valor_por_defecto: Any) -> Any:
    """Carga un archivo JSON y devuelve un valor por defecto si no existe o esta vacio."""
    if not ruta.exists():
        return valor_por_defecto

    contenido = ruta.read_text(encoding="utf-8").strip()
    if not contenido:
        return valor_por_defecto

    return json.loads(contenido)


def guardar_json(ruta: Path, datos: Any) -> None:
    """Guarda datos serializables en un archivo JSON con formato legible."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class BibliotecaCRUD:
    """Servicio CRUD para usuarios y libros con persistencia automatica en JSON."""

    def __init__(
        self,
        ruta_usuarios: str = "usuarios.json",
        ruta_libros: str = "libros.json",
        base_dir: Path | None = None,
    ) -> None:
        """Inicializa la coleccion en memoria y carga los datos persistidos."""
        raiz = base_dir or Path(__file__).resolve().parents[2]
        self._ruta_usuarios = raiz / ruta_usuarios
        self._ruta_libros = raiz / ruta_libros

        # Requisito: usuarios como diccionario con ID como clave.
        self.usuarios: dict[int, Usuario] = {}
        # Requisito: libros como lista.
        self.libros: list[Libro] = []

        self.cargar_datos()

    def cargar_datos(self) -> None:
        """Carga usuarios y libros desde JSON a objetos de dominio."""
        self.usuarios = self._cargar_usuarios()
        self.libros = self._cargar_libros()

    def guardar_datos(self) -> None:
        """Persiste el estado actual de usuarios y libros en archivos JSON."""
        self._guardar_usuarios()
        self._guardar_libros()

    def crear_usuario(self, usuario: Usuario) -> None:
        """Crea un usuario y persiste el cambio automaticamente."""
        if usuario.id in self.usuarios:
            raise ValueError(f"Ya existe un usuario con id {usuario.id}.")
        self.usuarios[usuario.id] = usuario
        self._guardar_usuarios()

    def obtener_usuario(self, id_usuario: int) -> Usuario | None:
        """Obtiene un usuario por su ID o None si no existe."""
        return self.usuarios.get(id_usuario)

    def listar_usuarios(self) -> list[Usuario]:
        """Retorna todos los usuarios en una lista para iteracion o respuesta API."""
        return list(self.usuarios.values())

    def actualizar_usuario(
        self,
        id_usuario: int,
        nombre: str | None = None,
        max_prestamos: int | None = None,
    ) -> Usuario:
        """Actualiza campos de un usuario existente y guarda automaticamente."""
        usuario = self.obtener_usuario(id_usuario)
        if usuario is None:
            raise ValueError(f"Usuario {id_usuario} no encontrado.")

        if nombre is not None:
            usuario.nombre = nombre
        if max_prestamos is not None:
            usuario.max_prestamos = max_prestamos

        self._guardar_usuarios()
        return usuario

    def eliminar_usuario(self, id_usuario: int) -> Usuario:
        """Elimina un usuario por ID y persiste el cambio."""
        usuario = self.obtener_usuario(id_usuario)
        if usuario is None:
            raise ValueError(f"Usuario {id_usuario} no encontrado.")

        usuario_eliminado = self.usuarios.pop(id_usuario)
        self._guardar_usuarios()
        return usuario_eliminado

    def crear_libro(self, libro: Libro) -> None:
        """Agrega un libro a la lista y persiste automaticamente."""
        if self.obtener_libro(libro.id) is not None:
            raise ValueError(f"Ya existe un libro con id {libro.id}.")
        self.libros.append(libro)
        self._guardar_libros()

    def obtener_libro(self, id_libro: int) -> Libro | None:
        """Busca y devuelve un libro por ID en la lista de libros."""
        for libro in self.libros:
            if libro.id == id_libro:
                return libro
        return None

    def listar_libros(self) -> list[Libro]:
        """Retorna una copia superficial de la lista de libros."""
        return list(self.libros)

    def actualizar_libro(
        self,
        id_libro: int,
        titulo: str | None = None,
        autor: str | None = None,
        anio: int | None = None,
        estado: str | None = None,
    ) -> Libro:
        """Actualiza datos de un libro y guarda automaticamente."""
        libro = self.obtener_libro(id_libro)
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")

        if titulo is not None:
            libro.titulo = titulo
        if autor is not None:
            libro.autor = autor
        if anio is not None:
            libro.anio = anio
        if estado is not None:
            libro.estado = estado

        self._guardar_libros()
        return libro

    def eliminar_libro(self, id_libro: int) -> Libro:
        """Elimina un libro de la lista por ID y persiste el cambio."""
        indice = self._indice_libro(id_libro)
        if indice is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")

        libro_eliminado = self.libros.pop(indice)
        self._guardar_libros()
        return libro_eliminado

    def _indice_libro(self, id_libro: int) -> int | None:
        """Devuelve el indice del libro en la lista o None si no existe."""
        for indice, libro in enumerate(self.libros):
            if libro.id == id_libro:
                return indice
        return None

    def _guardar_usuarios(self) -> None:
        """Serializa usuarios en disco como lista JSON para facilitar interoperabilidad."""
        datos = [
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "max_prestamos": usuario.max_prestamos,
            }
            for usuario in self.listar_usuarios()
        ]
        guardar_json(self._ruta_usuarios, datos)

    def _guardar_libros(self) -> None:
        """Serializa libros en disco como lista JSON."""
        datos = [
            {
                "id": libro.id,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "anio": libro.anio,
                "estado": libro.estado,
            }
            for libro in self.listar_libros()
        ]
        guardar_json(self._ruta_libros, datos)

    def _cargar_usuarios(self) -> dict[int, Usuario]:
        """Reconstruye el diccionario de usuarios desde usuarios.json."""
        datos = cargar_json(self._ruta_usuarios, [])
        usuarios: dict[int, Usuario] = {}

        for item in datos:
            usuario = Usuario(
                id_persona=int(item["id"]),
                nombre=str(item["nombre"]),
                max_prestamos=int(item.get("max_prestamos", 3)),
            )
            usuarios[usuario.id] = usuario

        return usuarios

    def _cargar_libros(self) -> list[Libro]:
        """Reconstruye la lista de libros desde libros.json."""
        datos = cargar_json(self._ruta_libros, [])
        libros: list[Libro] = []

        for item in datos:
            libro = Libro(
                id_libro=int(item["id"]),
                titulo=str(item["titulo"]),
                autor=str(item["autor"]),
                anio=int(item["anio"]),
            )
            libro.estado = str(item.get("estado", Libro.ESTADO_DISPONIBLE))
            libros.append(libro)

        return libros
