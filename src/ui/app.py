# Responsable: Oscar Monterrosa - Desarrollador Frontend y Visualización

"""Base de interfaz para la aplicacion de biblioteca.

Jerarquia de UI en customtkinter:
1. `BibliotecaApp` hereda de `ctk.CTk` y representa la ventana raiz.
2. Dentro de la raiz se construye una cabecera superior y un `CTkTabview` central.
3. Cada pestaña (`Libros`, `Usuarios`, `Préstamos`, `Estadísticas`) contiene
    formularios y paneles de salida que se organizan por grilla para mantener
    una lectura clara de izquierda a derecha.

Relacion con `ui/main_gui.py`:
- Este archivo define la base funcional completa (layout, CRUD y eventos).
- `main_gui.py` especializa/ajusta la parte de visualizacion estadistica,
  reutilizando esta base sin duplicar el resto de la interfaz.
"""

from __future__ import annotations

from datetime import date
import re
from tkinter import messagebox, ttk

import customtkinter as ctk
import matplotlib.backends.backend_tkagg
from matplotlib.figure import Figure

from models.libro import Libro
from models.usuario import Usuario
from services.crud_biblioteca import BibliotecaCRUD
from services.gestion_prestamos import GestionPrestamos


class BibliotecaApp(ctk.CTk):
    """Interfaz principal para gestionar libros, usuarios, prestamos y estadisticas.

    Esta clase prioriza una experiencia clara, fluida e intuitiva mediante:
    - Distribucion predecible (cabecera + tabs + barra de estado).
    - Controles agrupados por tarea (formularios y listados por dominio).
    - Retroalimentacion visual inmediata tras cada accion del usuario.
    """

    def __init__(self) -> None:
        """Inicializa la ventana principal de customtkinter.

        Se usa modo `light` y tema `blue` porque mejoran contraste y legibilidad
        en formularios de escritorio academicos: campos y botones son faciles de
        distinguir, reduciendo carga cognitiva para tareas CRUD repetitivas.
        """
        super().__init__()
        # Configuracion base de ventana para asegurar espacio comodo de trabajo.
        self.title("Sistema de Biblioteca")
        self.geometry("1180x760")
        self.minsize(1050, 700)

        # Tema visual elegido para mantener una interfaz clara e intuitiva.
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Servicios de datos y negocio que alimentan las vistas de la UI.
        self.crud = BibliotecaCRUD()
        self.prestamos = GestionPrestamos()
        self._sincronizar_referencias()

        # Construccion de jerarquia visual y primer render de contenidos.
        self._crear_layout_principal()
        self._configurar_estilo_tabla_prestamos()
        self._refrescar_todo()

    def _sincronizar_referencias(self) -> None:
        """Comparte colecciones entre CRUD y prestamos para mantener un estado unico."""
        self.prestamos.usuarios = self.crud.usuarios
        self.prestamos.libros = self.crud.libros

    def _crear_layout_principal(self) -> None:
        """Construye cabecera, tabs y contenedor de mensajes de estado.

        Estructura jerarquica:
        - Fila 0: encabezado con titulo y subtitulo.
        - Fila 1: contenedor de pestañas con las vistas funcionales.
        - Fila 2: barra de estado para mensajes de confirmacion y errores.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            header,
            text="Gestion de Biblioteca",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=20, pady=(14, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            header,
            text="CRUD + Prestamos + Visualizacion de datos",
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")

        self.tab_libros = self.tabs.add("Libros")
        self.tab_usuarios = self.tabs.add("Usuarios")
        self.tab_prestamos = self.tabs.add("Préstamos")
        self.tab_estadisticas = self.tabs.add("Estadísticas")

        self._crear_tab_libros()
        self._crear_tab_usuarios()
        self._crear_tab_prestamos()
        self._crear_tab_estadisticas()

        self.estado_var = ctk.StringVar(value="Listo")
        estado_label = ctk.CTkLabel(self, textvariable=self.estado_var, anchor="w")
        estado_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

    def _crear_tab_libros(self) -> None:
        """Configura controles de CRUD para libros.

        Criterios de Fluidez y Validacion:
        - La disposicion de widgets con `grid()` en columnas y filas es
          intuitiva: el formulario a la izquierda (entrada) y el listado a la
          derecha (salida).
        - Cada boton (Crear, Actualizar, etc.) se vincula a una funcion `_ui`
          especifica (ej. `crear_libro_ui`) que valida las entradas para
          prevenir datos vacios o con formato incorrecto antes de pasarlos a la
          capa de servicios.
        """
        self.tab_libros.grid_columnconfigure(0, weight=0)
        self.tab_libros.grid_columnconfigure(1, weight=1)
        self.tab_libros.grid_rowconfigure(0, weight=1)

        formulario = ctk.CTkFrame(self.tab_libros)
        formulario.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="ns")

        ctk.CTkLabel(formulario, text="Formulario Libro", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(12, 8), sticky="w"
        )

        self.libro_id_entry = self._agregar_entry(formulario, "ID", 1)
        self.libro_titulo_entry = self._agregar_entry(formulario, "Titulo", 2)
        self.libro_autor_entry = self._agregar_entry(formulario, "Autor", 3)
        self.libro_anio_entry = self._agregar_entry(formulario, "Año", 4)

        ctk.CTkLabel(formulario, text="Estado").grid(row=5, column=0, padx=10, pady=6, sticky="w")
        self.libro_estado_menu = ctk.CTkOptionMenu(
            formulario,
            values=[Libro.ESTADO_DISPONIBLE, Libro.ESTADO_PRESTADO],
        )
        self.libro_estado_menu.set(Libro.ESTADO_DISPONIBLE)
        self.libro_estado_menu.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        botones = ctk.CTkFrame(formulario, fg_color="transparent")
        botones.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(botones, text="Crear", command=self.crear_libro_ui).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Actualizar", command=self.actualizar_libro_ui).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Eliminar", command=self.eliminar_libro_ui).grid(
            row=1, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Refrescar", command=self.refrescar_libros_ui).grid(
            row=1, column=1, padx=4, pady=4, sticky="ew"
        )

        lista_frame = ctk.CTkFrame(self.tab_libros)
        lista_frame.grid(row=0, column=1, padx=(10, 0), pady=6, sticky="nsew")
        lista_frame.grid_columnconfigure(0, weight=1)
        lista_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(lista_frame, text="Catalogo", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 4), sticky="w"
        )

        self.libros_tree = ttk.Treeview(
            lista_frame,
            columns=("id", "titulo", "autor", "anio", "estado"),
            show="headings",
            style="Libros.Treeview",
        )
        self.libros_tree.heading("id", text="ID")
        self.libros_tree.heading("titulo", text="Titulo")
        self.libros_tree.heading("autor", text="Autor")
        self.libros_tree.heading("anio", text="Año")
        self.libros_tree.heading("estado", text="Estado")

        self.libros_tree.column("id", width=90, minwidth=70, anchor="center", stretch=True)
        self.libros_tree.column("titulo", width=280, minwidth=180, anchor="w", stretch=True)
        self.libros_tree.column("autor", width=210, minwidth=150, anchor="w", stretch=True)
        self.libros_tree.column("anio", width=95, minwidth=80, anchor="center", stretch=True)
        self.libros_tree.column("estado", width=120, minwidth=100, anchor="center", stretch=True)

        scroll_vertical = ttk.Scrollbar(lista_frame, orient="vertical", command=self.libros_tree.yview)
        scroll_horizontal = ttk.Scrollbar(lista_frame, orient="horizontal", command=self.libros_tree.xview)
        self.libros_tree.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
        )

        self.libros_tree.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="nsew")
        scroll_vertical.grid(row=1, column=1, pady=(0, 0), sticky="ns")
        scroll_horizontal.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _crear_tab_usuarios(self) -> None:
        """Configura controles de CRUD para usuarios.

        Criterios de Fluidez y Validacion:
        - La disposicion de widgets con `grid()` en columnas y filas es
          intuitiva: el formulario a la izquierda (entrada) y el listado a la
          derecha (salida).
        - Cada boton (Crear, Actualizar, etc.) se vincula a una funcion `_ui`
          especifica (ej. `crear_usuario_ui`) que valida las entradas para
          prevenir datos vacios o con formato incorrecto antes de pasarlos a la
          capa de servicios.
        """
        self.tab_usuarios.grid_columnconfigure(0, weight=0)
        self.tab_usuarios.grid_columnconfigure(1, weight=1)
        self.tab_usuarios.grid_rowconfigure(0, weight=1)

        formulario = ctk.CTkFrame(self.tab_usuarios)
        formulario.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="ns")

        ctk.CTkLabel(formulario, text="Formulario Usuario", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(12, 8), sticky="w"
        )

        self.usuario_id_entry = self._agregar_entry(formulario, "ID", 1)
        self.usuario_nombre_entry = self._agregar_entry(formulario, "Nombre", 2)
        self.usuario_max_entry = self._agregar_entry(formulario, "Max prestamos", 3)

        botones = ctk.CTkFrame(formulario, fg_color="transparent")
        botones.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(botones, text="Crear", command=self.crear_usuario_ui).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Actualizar", command=self.actualizar_usuario_ui).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Eliminar", command=self.eliminar_usuario_ui).grid(
            row=1, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Refrescar", command=self.refrescar_usuarios_ui).grid(
            row=1, column=1, padx=4, pady=4, sticky="ew"
        )

        lista_frame = ctk.CTkFrame(self.tab_usuarios)
        lista_frame.grid(row=0, column=1, padx=(10, 0), pady=6, sticky="nsew")
        lista_frame.grid_columnconfigure(0, weight=1)
        lista_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(lista_frame, text="Usuarios", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 4), sticky="w"
        )

        self.usuarios_tree = ttk.Treeview(
            lista_frame,
            columns=("id", "nombre", "max_prestamos"),
            show="headings",
            style="Usuarios.Treeview",
        )
        self.usuarios_tree.heading("id", text="ID")
        self.usuarios_tree.heading("nombre", text="Nombre")
        self.usuarios_tree.heading("max_prestamos", text="Max prestamos")

        self.usuarios_tree.column("id", width=90, minwidth=70, anchor="center", stretch=True)
        self.usuarios_tree.column("nombre", width=300, minwidth=180, anchor="w", stretch=True)
        self.usuarios_tree.column(
            "max_prestamos", width=150, minwidth=120, anchor="center", stretch=True
        )

        scroll_vertical = ttk.Scrollbar(lista_frame, orient="vertical", command=self.usuarios_tree.yview)
        scroll_horizontal = ttk.Scrollbar(
            lista_frame,
            orient="horizontal",
            command=self.usuarios_tree.xview,
        )
        self.usuarios_tree.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
        )

        self.usuarios_tree.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="nsew")
        scroll_vertical.grid(row=1, column=1, pady=(0, 0), sticky="ns")
        scroll_horizontal.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _crear_tab_prestamos(self) -> None:
        """Configura acciones de prestar/devolver con validaciones de negocio.

        Criterios de Fluidez y Validacion:
        - La disposicion de widgets con `grid()` en columnas y filas es
          intuitiva: el formulario a la izquierda (entrada) y el listado a la
          derecha (salida).
        - Cada boton (Prestar, Devolver, etc.) se vincula a una funcion `_ui`
          especifica (ej. `prestar_libro_ui`) que valida las entradas para
          prevenir datos vacios o con formato incorrecto antes de pasarlos a la
          capa de servicios.
        """
        self.tab_prestamos.grid_columnconfigure(0, weight=0)
        self.tab_prestamos.grid_columnconfigure(1, weight=1)
        self.tab_prestamos.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self.tab_prestamos)
        panel.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="ns")

        ctk.CTkLabel(panel, text="Operaciones", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(12, 8), sticky="w"
        )

        self.prestamo_libro_entry = self._agregar_entry(panel, "ID Libro", 1)
        self.prestamo_usuario_entry = self._agregar_entry(panel, "ID Usuario", 2)
        self.fecha_prestamo_entry = self._agregar_entry(panel, "Fecha prestamo", 3)
        self.fecha_devolucion_entry = self._agregar_entry(panel, "Fecha devolucion", 4)

        hoy = date.today().isoformat()
        self.fecha_prestamo_entry.insert(0, hoy)
        self.fecha_devolucion_entry.insert(0, hoy)

        botones = ctk.CTkFrame(panel, fg_color="transparent")
        botones.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(botones, text="Prestar", command=self.prestar_libro_ui).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(botones, text="Devolver", command=self.devolver_libro_ui).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(
            botones,
            text="Estado actual",
            command=self.consultar_estado_libro_ui,
        ).grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(
            botones,
            text="Refrescar",
            command=self.refrescar_prestamos_ui,
        ).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        historial_frame = ctk.CTkFrame(self.tab_prestamos)
        historial_frame.grid(row=0, column=1, padx=(10, 0), pady=6, sticky="nsew")
        historial_frame.grid_columnconfigure(0, weight=1)
        historial_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            historial_frame,
            text="Historial de prestamos",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=(10, 4), sticky="w")

        self.historial_tree = ttk.Treeview(
            historial_frame,
            columns=(
                "id_libro",
                "id_usuario",
                "fecha_prestamo",
                "fecha_devolucion",
                "estado",
            ),
            show="headings",
            style="Prestamos.Treeview",
        )
        self.historial_tree.heading("id_libro", text="ID Libro")
        self.historial_tree.heading("id_usuario", text="ID Usuario")
        self.historial_tree.heading("fecha_prestamo", text="Fecha Prestamo")
        self.historial_tree.heading("fecha_devolucion", text="Fecha Devolucion")
        self.historial_tree.heading("estado", text="Estado")

        # stretch=True permite que el usuario redimensione columnas arrastrando bordes.
        self.historial_tree.column("id_libro", width=110, minwidth=90, anchor="center", stretch=True)
        self.historial_tree.column("id_usuario", width=120, minwidth=95, anchor="center", stretch=True)
        self.historial_tree.column(
            "fecha_prestamo", width=165, minwidth=130, anchor="center", stretch=True
        )
        self.historial_tree.column(
            "fecha_devolucion", width=175, minwidth=140, anchor="center", stretch=True
        )
        self.historial_tree.column("estado", width=120, minwidth=100, anchor="center", stretch=True)

        scroll_vertical = ttk.Scrollbar(
            historial_frame,
            orient="vertical",
            command=self.historial_tree.yview,
        )
        scroll_horizontal = ttk.Scrollbar(
            historial_frame,
            orient="horizontal",
            command=self.historial_tree.xview,
        )
        self.historial_tree.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
        )

        self.historial_tree.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="nsew")
        scroll_vertical.grid(row=1, column=1, pady=(0, 0), sticky="ns")
        scroll_horizontal.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    def _configurar_estilo_tabla_prestamos(self) -> None:
        """Sincroniza colores de todas las tablas Treeview con customtkinter."""
        modo = ctk.get_appearance_mode().lower()

        if modo == "dark":
            fondo_tabla = "#1f1f1f"
            texto_tabla = "#f3f4f6"
            fondo_cabecera = "#2b2b2b"
            texto_cabecera = "#f9fafb"
            borde = "#3f3f46"
            seleccionado = "#1d4ed8"
        else:
            fondo_tabla = "#ffffff"
            texto_tabla = "#111827"
            fondo_cabecera = "#e5e7eb"
            texto_cabecera = "#111827"
            borde = "#cbd5e1"
            seleccionado = "#bfdbfe"

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        nombres_estilo = ("Libros.Treeview", "Usuarios.Treeview", "Prestamos.Treeview")

        for nombre in nombres_estilo:
            estilo.configure(
                nombre,
                background=fondo_tabla,
                fieldbackground=fondo_tabla,
                foreground=texto_tabla,
                bordercolor=borde,
                rowheight=28,
                relief="flat",
            )
            estilo.configure(
                f"{nombre}.Heading",
                background=fondo_cabecera,
                foreground=texto_cabecera,
                bordercolor=borde,
                relief="flat",
                font=("Segoe UI", 10, "bold"),
            )
            estilo.map(
                nombre,
                background=[("selected", seleccionado)],
                foreground=[("selected", texto_tabla)],
            )
            estilo.map(
                f"{nombre}.Heading",
                background=[("active", fondo_cabecera)],
            )

    def _crear_tab_estadisticas(self) -> None:
        """Construye el contenedor para graficos de barras y pastel."""
        self.tab_estadisticas.grid_columnconfigure((0, 1), weight=1)
        self.tab_estadisticas.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(
            self.tab_estadisticas,
            text="Actualizar estadisticas",
            command=self.refrescar_estadisticas_ui,
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        frame_barras = ctk.CTkFrame(self.tab_estadisticas)
        frame_barras.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="nsew")
        frame_pastel = ctk.CTkFrame(self.tab_estadisticas)
        frame_pastel.grid(row=1, column=1, padx=(5, 10), pady=(0, 10), sticky="nsew")

        figura_barras = Figure(figsize=(5, 4), dpi=100)
        self.ax_barras = figura_barras.add_subplot(111)
        self.canvas_barras = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(figura_barras, master=frame_barras)
        self.canvas_barras.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        figura_pastel = Figure(figsize=(5, 4), dpi=100)
        self.ax_pastel = figura_pastel.add_subplot(111)
        self.canvas_pastel = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(figura_pastel, master=frame_pastel)
        self.canvas_pastel.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _agregar_entry(self, parent: ctk.CTkFrame, texto: str, fila: int) -> ctk.CTkEntry:
        """Crea un label + entry estandar para formularios."""
        ctk.CTkLabel(parent, text=texto).grid(row=fila, column=0, padx=10, pady=6, sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=fila, column=1, padx=10, pady=6, sticky="ew")
        return entry

    def _set_estado(self, mensaje: str) -> None:
        """Actualiza la barra inferior con feedback de operacion."""
        self.estado_var.set(mensaje)

    def _parsear_fecha(self, valor: str) -> date:
        """Convierte texto ISO (YYYY-MM-DD) a fecha para reglas de negocio."""
        return date.fromisoformat(valor.strip())

    @staticmethod
    def _normalizar_id(valor: str) -> str:
        return str(valor).strip()

    @staticmethod
    def _validar_id(valor: str) -> str:
        texto = BibliotecaApp._normalizar_id(valor)
        if not texto:
            raise ValueError("El ID es obligatorio.")
        if not re.fullmatch(r"^(?=.*[A-Za-z0-9])[A-Za-z0-9-]+$", texto):
            raise ValueError("ID invalido. Use letras, numeros y guion '-'. Ej: RO-253385")
        return texto

    def crear_libro_ui(self) -> None:
        """Maneja evento de alta de libro y sincroniza vistas."""
        try:
            id_libro = self._validar_id(self.libro_id_entry.get())
            libro = Libro(
                id_libro=id_libro,
                titulo=self.libro_titulo_entry.get().strip(),
                autor=self.libro_autor_entry.get().strip(),
                anio=int(self.libro_anio_entry.get().strip()),
            )
            self.crud.crear_libro(libro)
            estado = self.libro_estado_menu.get()
            if estado != Libro.ESTADO_DISPONIBLE:
                self.crud.actualizar_libro(libro.id, estado=estado)

            self._sincronizar_referencias()
            self._refrescar_todo()
            self._set_estado("Libro creado correctamente.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def actualizar_libro_ui(self) -> None:
        """Maneja evento de actualizacion de libro por ID."""
        try:
            id_libro = self._validar_id(self.libro_id_entry.get())
            titulo = self._valor_o_none(self.libro_titulo_entry.get())
            autor = self._valor_o_none(self.libro_autor_entry.get())
            anio = self._valor_o_none(self.libro_anio_entry.get())
            estado = self.libro_estado_menu.get()

            self.crud.actualizar_libro(
                id_libro=id_libro,
                titulo=titulo,
                autor=autor,
                anio=int(anio) if anio is not None else None,
                estado=estado,
            )
            self._refrescar_todo()
            self._set_estado("Libro actualizado.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def eliminar_libro_ui(self) -> None:
        """Maneja baja de libro por ID."""
        try:
            id_libro = self._validar_id(self.libro_id_entry.get())
            self.crud.eliminar_libro(id_libro)
            self._sincronizar_referencias()
            self._refrescar_todo()
            self._set_estado("Libro eliminado.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def refrescar_libros_ui(self) -> None:
        """Actualiza solo la vista de libros."""
        self._render_libros()
        self._set_estado("Catalogo refrescado.")

    def crear_usuario_ui(self) -> None:
        """Maneja alta de usuario y actualiza persistencia."""
        try:
            usuario = Usuario(
                id_persona=self._validar_id(self.usuario_id_entry.get()),
                nombre=self.usuario_nombre_entry.get().strip(),
                max_prestamos=int(self.usuario_max_entry.get().strip() or "3"),
            )
            self.crud.crear_usuario(usuario)
            self._sincronizar_referencias()
            self._refrescar_todo()
            self._set_estado("Usuario creado correctamente.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def actualizar_usuario_ui(self) -> None:
        """Maneja actualizacion de usuario por ID."""
        try:
            id_usuario = self._validar_id(self.usuario_id_entry.get())
            nombre = self._valor_o_none(self.usuario_nombre_entry.get())
            max_prestamos = self._valor_o_none(self.usuario_max_entry.get())

            self.crud.actualizar_usuario(
                id_usuario=id_usuario,
                nombre=nombre,
                max_prestamos=int(max_prestamos) if max_prestamos is not None else None,
            )
            self._refrescar_todo()
            self._set_estado("Usuario actualizado.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def eliminar_usuario_ui(self) -> None:
        """Maneja baja de usuario por ID."""
        try:
            id_usuario = self._validar_id(self.usuario_id_entry.get())
            self.crud.eliminar_usuario(id_usuario)
            self._sincronizar_referencias()
            self._refrescar_todo()
            self._set_estado("Usuario eliminado.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def refrescar_usuarios_ui(self) -> None:
        """Actualiza solo la vista de usuarios."""
        self._render_usuarios()
        self._set_estado("Lista de usuarios refrescada.")

    def prestar_libro_ui(self) -> None:
        """Ejecuta logica de prestamo con validaciones criticas."""
        try:
            self._sincronizar_referencias()
            id_libro = self._validar_id(self.prestamo_libro_entry.get())
            id_usuario = self._validar_id(self.prestamo_usuario_entry.get())
            fecha_prestamo = self._parsear_fecha(self.fecha_prestamo_entry.get())

            self.prestamos.prestar_libro(id_libro, id_usuario, fecha_prestamo)
            # Guarda estado de libros tras el prestamo.
            self.crud.guardar_datos()
            self._refrescar_todo()
            self._set_estado("Prestamo registrado.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def devolver_libro_ui(self) -> None:
        """Ejecuta devolucion y valida fecha de devolucion."""
        try:
            self._sincronizar_referencias()
            id_libro = self._validar_id(self.prestamo_libro_entry.get())
            fecha_devolucion = self._parsear_fecha(self.fecha_devolucion_entry.get())

            self.prestamos.devolver_libro(id_libro, fecha_devolucion)
            # Guarda estado de libros tras la devolucion.
            self.crud.guardar_datos()
            self._refrescar_todo()
            self._set_estado("Devolucion registrada.")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def consultar_estado_libro_ui(self) -> None:
        """Muestra el estado vigente de un libro especifico."""
        try:
            self._sincronizar_referencias()
            id_libro = self._validar_id(self.prestamo_libro_entry.get())
            estado = self.prestamos.estado_actual_libro(id_libro)
            self._set_estado(f"Estado del libro {id_libro}: {estado}")
            messagebox.showinfo("Estado actual", f"Libro {id_libro}: {estado}")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error", str(error))

    def refrescar_estadisticas_ui(self) -> None:
        """Actualiza ambos graficos usando el historial actual en memoria."""
        self._render_estadisticas()
        self._set_estado("Estadisticas actualizadas.")

    def refrescar_prestamos_ui(self) -> None:
        """Recarga la tabla de historial de prestamos desde la matriz de servicios."""
        self._render_historial()
        self._set_estado("Historial de prestamos refrescado.")

    def _render_libros(self) -> None:
        """Limpia y repuebla la tabla de libros con los datos actuales."""
        self._configurar_estilo_tabla_prestamos()

        for item_id in self.libros_tree.get_children():
            self.libros_tree.delete(item_id)

        libros = self.crud.listar_libros()

        for libro in libros:
            self.libros_tree.insert(
                "",
                "end",
                values=(libro.id, libro.titulo, libro.autor, libro.anio, libro.estado),
            )

    def _render_usuarios(self) -> None:
        """Limpia y repuebla la tabla de usuarios con los datos actuales."""
        self._configurar_estilo_tabla_prestamos()

        for item_id in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item_id)

        usuarios = self.crud.listar_usuarios()

        for usuario in usuarios:
            self.usuarios_tree.insert(
                "",
                "end",
                values=(usuario.id, usuario.nombre, usuario.max_prestamos),
            )

    def _render_historial(self) -> None:
        """Limpia y repuebla el Treeview de prestamos con datos tabulares."""
        self._configurar_estilo_tabla_prestamos()

        for item_id in self.historial_tree.get_children():
            self.historial_tree.delete(item_id)

        matriz = self.prestamos.convertir_prestamos_a_matriz()

        for id_libro, id_usuario, fecha_prestamo, fecha_devolucion in matriz:
            estado = "Devuelto" if fecha_devolucion else "Prestado"
            self.historial_tree.insert(
                "",
                "end",
                values=(
                    id_libro,
                    id_usuario,
                    fecha_prestamo,
                    fecha_devolucion if fecha_devolucion else "Pendiente",
                    estado,
                ),
            )

    def _render_estadisticas(self) -> None:
        """Dibuja grafico de barras y pastel a partir del historial de prestamos."""
        matriz = self.prestamos.convertir_prestamos_a_matriz()
        ranking_libros = self.prestamos.libros_mas_prestados(limite=5)
        ranking_usuarios = self.prestamos.usuarios_mas_activos(limite=5)

        self.ax_barras.clear()
        self.ax_pastel.clear()

        if matriz and ranking_libros:
            etiquetas_libros: list[str] = []
            valores_libros: list[int] = []
            for id_libro, total in ranking_libros:
                libro = self.crud.obtener_libro(id_libro)
                etiqueta = libro.titulo if libro is not None else f"Libro {id_libro}"
                etiquetas_libros.append(etiqueta)
                valores_libros.append(total)

            self.ax_barras.bar(etiquetas_libros, valores_libros, color="#2563eb")
            self.ax_barras.set_title("Libros mas prestados")
            self.ax_barras.set_ylabel("Cantidad de prestamos")
            self.ax_barras.tick_params(axis="x", labelrotation=22)
        else:
            self.ax_barras.set_title("Libros mas prestados")
            self.ax_barras.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            self.ax_barras.set_xticks([])
            self.ax_barras.set_yticks([])

        if matriz and ranking_usuarios:
            etiquetas_usuarios: list[str] = []
            valores_usuarios: list[int] = []
            for id_usuario, total in ranking_usuarios:
                usuario = self.crud.obtener_usuario(id_usuario)
                etiqueta = usuario.nombre if usuario is not None else f"Usuario {id_usuario}"
                etiquetas_usuarios.append(etiqueta)
                valores_usuarios.append(total)

            self.ax_pastel.pie(
                valores_usuarios,
                labels=etiquetas_usuarios,
                autopct="%1.1f%%",
                startangle=90,
            )
            self.ax_pastel.set_title("Usuarios mas activos")
        else:
            self.ax_pastel.set_title("Usuarios mas activos")
            self.ax_pastel.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            self.ax_pastel.set_xticks([])
            self.ax_pastel.set_yticks([])

        self.canvas_barras.draw_idle()
        self.canvas_pastel.draw_idle()

    def _refrescar_todo(self) -> None:
        """Sincroniza todas las vistas para mantener consistencia visual."""
        self._render_libros()
        self._render_usuarios()
        self._render_historial()
        self._render_estadisticas()

    @staticmethod
    def _valor_o_none(valor: str) -> str | None:
        """Convierte cadenas vacias en None para updates parciales."""
        texto = valor.strip()
        return texto if texto else None
