from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from models.libro import Libro
from models.usuario import Usuario
from services.crud_biblioteca import cargar_json, guardar_json


@dataclass
class Prestamo:
    """Representa un prestamo individual para reglas de negocio y persistencia."""

    id_libro: int
    id_usuario: int
    fecha_prestamo: date
    fecha_devolucion: date | None = None


class GestionPrestamos:
    """Gestiona prestamos de libros, validaciones y persistencia de historial."""

    def __init__(
        self,
        ruta_prestamos: str = "prestamos.json",
        base_dir: Path | None = None,
    ) -> None:
        # Requisito: usuarios en diccionario con el ID como clave.
        self.usuarios: dict[int, Usuario] = {}
        # Requisito: libros en lista.
        self.libros: list[Libro] = []
        # Lista de objetos de prestamo para encapsular la logica de negocio.
        self._prestamos: list[Prestamo] = []

        raiz = base_dir or Path(__file__).resolve().parents[2]
        self._ruta_prestamos = raiz / ruta_prestamos
        self._cargar_prestamos()

    def registrar_usuario(self, usuario: Usuario) -> None:
        """Registra un usuario nuevo evitando IDs duplicados."""
        if usuario.id in self.usuarios:
            raise ValueError(f"Ya existe un usuario con id {usuario.id}.")
        self.usuarios[usuario.id] = usuario

    def registrar_libro(self, libro: Libro) -> None:
        """Registra un libro nuevo evitando IDs duplicados."""
        if self.obtener_libro(libro.id) is not None:
            raise ValueError(f"Ya existe un libro con id {libro.id}.")
        self.libros.append(libro)

    def obtener_libro(self, id_libro: int) -> Libro | None:
        """Busca un libro por ID dentro de la lista de libros."""
        for libro in self.libros:
            if libro.id == id_libro:
                return libro
        return None

    def prestar_libro(self, id_libro: int, id_usuario: int, fecha_prestamo: date) -> None:
        """Registra un prestamo si el libro esta disponible y los IDs existen."""
        if fecha_prestamo is None:
            raise ValueError("La fecha de prestamo es obligatoria.")

        usuario = self.usuarios.get(id_usuario)
        if usuario is None:
            raise ValueError(f"Usuario {id_usuario} no encontrado.")

        libro = self.obtener_libro(id_libro)
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")

        # Validacion critica: no prestar si el libro ya esta prestado.
        if libro.estado == Libro.ESTADO_PRESTADO:
            raise ValueError("No se puede prestar: el libro ya esta Prestado.")

        libro.prestar()
        self._prestamos.append(
            Prestamo(
                id_libro=id_libro,
                id_usuario=id_usuario,
                fecha_prestamo=fecha_prestamo,
            )
        )
        self._guardar_prestamos()

    def devolver_libro(self, id_libro: int, fecha_devolucion: date) -> None:
        """Registra devolucion validando orden de fechas y estado del libro."""
        if fecha_devolucion is None:
            raise ValueError("La fecha de devolucion es obligatoria.")

        libro = self.obtener_libro(id_libro)
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")

        if libro.estado != Libro.ESTADO_PRESTADO:
            raise ValueError("No se puede devolver: el libro no esta Prestado.")

        fila_abierta = self._buscar_prestamo_abierto(id_libro)
        if fila_abierta is None:
            raise ValueError("No existe un prestamo activo para ese libro.")

        # Validacion critica: la devolucion debe ser posterior al prestamo.
        if fecha_devolucion <= fila_abierta.fecha_prestamo:
            raise ValueError("La fecha de devolucion debe ser posterior al prestamo.")

        fila_abierta.fecha_devolucion = fecha_devolucion
        libro.devolver()
        self._guardar_prestamos()

    def estado_actual_libro(self, id_libro: int) -> str:
        """Devuelve el estado actual de un libro (disponible o prestado)."""
        libro = self.obtener_libro(id_libro)
        if libro is None:
            raise ValueError(f"Libro {id_libro} no encontrado.")
        return libro.estado

    def obtener_historial(self) -> list[list[int | str | None]]:
        """Retorna una matriz tabular para reportes de prestamos."""
        return self.convertir_prestamos_a_matriz()

    def convertir_prestamos_a_matriz(
        self,
        prestamos: list[Prestamo] | None = None,
    ) -> list[list[int | str | None]]:
        """Convierte una lista de objetos Prestamo en matriz para reportes tabulares."""
        origen = prestamos if prestamos is not None else self._prestamos
        matriz: list[list[int | str | None]] = []

        for prestamo in origen:
            matriz.append(
                [
                    prestamo.id_libro,
                    prestamo.id_usuario,
                    prestamo.fecha_prestamo.isoformat(),
                    prestamo.fecha_devolucion.isoformat()
                    if prestamo.fecha_devolucion is not None
                    else None,
                ]
            )

        return matriz

    def libros_mas_prestados(self, limite: int = 5) -> list[tuple[int, int]]:
        """Retorna ranking de libros por cantidad de prestamos en formato (id_libro, total)."""
        matriz = self.convertir_prestamos_a_matriz()
        contador = Counter(int(fila[0]) for fila in matriz)
        return contador.most_common(limite)

    def usuarios_mas_activos(self, limite: int = 5) -> list[tuple[int, int]]:
        """Retorna ranking de usuarios por cantidad de prestamos en formato (id_usuario, total)."""
        matriz = self.convertir_prestamos_a_matriz()
        contador = Counter(int(fila[1]) for fila in matriz)
        return contador.most_common(limite)

    def _buscar_prestamo_abierto(self, id_libro: int) -> Prestamo | None:
        """Busca el ultimo prestamo abierto para un libro."""
        for prestamo in reversed(self._prestamos):
            if prestamo.id_libro == id_libro and prestamo.fecha_devolucion is None:
                return prestamo
        return None

    def _guardar_prestamos(self) -> None:
        """Guarda la lista de prestamos en JSON para persistencia de reportes."""
        datos = [
            {
                "id_libro": prestamo.id_libro,
                "id_usuario": prestamo.id_usuario,
                "fecha_prestamo": prestamo.fecha_prestamo.isoformat(),
                "fecha_devolucion": prestamo.fecha_devolucion.isoformat()
                if prestamo.fecha_devolucion is not None
                else None,
            }
            for prestamo in self._prestamos
        ]
        guardar_json(self._ruta_prestamos, datos)

    def _cargar_prestamos(self) -> None:
        """Carga prestamos desde JSON al iniciar el servicio."""
        datos = cargar_json(self._ruta_prestamos, [])
        self._prestamos = []

        for item in datos:
            fecha_devolucion_raw = item.get("fecha_devolucion")
            self._prestamos.append(
                Prestamo(
                    id_libro=int(item["id_libro"]),
                    id_usuario=int(item["id_usuario"]),
                    fecha_prestamo=date.fromisoformat(str(item["fecha_prestamo"])),
                    fecha_devolucion=date.fromisoformat(str(fecha_devolucion_raw))
                    if fecha_devolucion_raw
                    else None,
                )
            )
