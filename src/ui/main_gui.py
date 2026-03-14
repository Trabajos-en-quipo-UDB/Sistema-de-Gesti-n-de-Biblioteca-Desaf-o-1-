# Responsable: Oscar Monterrosa - Desarrollador Frontend y Visualización

"""Modulo de interfaz principal orientado a visualizacion.

Jerarquia de pestañas (Tabs):
- Libros
- Usuarios
- Préstamos
- Estadísticas

La aplicacion centraliza en una sola ventana el CRUD completo y la visualizacion
de datos. Esta organizacion reduce cambios de contexto y hace mas directo el flujo
de trabajo para el usuario final.

Se usa `customtkinter.CTkTabview` para lograr navegacion fluida entre secciones,
manteniendo un layout consistente mientras solo cambia el contenido de cada pestaña.
"""

from __future__ import annotations

from collections import Counter

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ui.app import BibliotecaApp


class MainGUI(BibliotecaApp):
    """UI principal con foco en visualizacion estadistica basada en matriz."""

    def _crear_tab_estadisticas(self) -> None:
        """Crea el panel de estadisticas con graficos embebidos en customtkinter."""
        self.tab_estadisticas.grid_columnconfigure((0, 1), weight=1)
        self.tab_estadisticas.grid_rowconfigure(1, weight=1)

        boton_refrescar = ctk.CTkButton(
            self.tab_estadisticas,
            text="Actualizar estadisticas",
            command=self.refrescar_estadisticas_ui,
        )
        boton_refrescar.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        frame_barras = ctk.CTkFrame(self.tab_estadisticas)
        frame_barras.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="nsew")

        frame_pastel = ctk.CTkFrame(self.tab_estadisticas)
        frame_pastel.grid(row=1, column=1, padx=(5, 10), pady=(0, 10), sticky="nsew")

        figura_barras = Figure(figsize=(5.2, 4.2), dpi=100)
        self.ax_barras = figura_barras.add_subplot(111)
        self.canvas_barras = FigureCanvasTkAgg(figura_barras, master=frame_barras)
        self.canvas_barras.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        figura_pastel = Figure(figsize=(5.2, 4.2), dpi=100)
        self.ax_pastel = figura_pastel.add_subplot(111)
        self.canvas_pastel = FigureCanvasTkAgg(figura_pastel, master=frame_pastel)
        self.canvas_pastel.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _render_estadisticas(self) -> None:
        """Genera dinamicamente los graficos estadisticos usando Matplotlib.

        Origen de Datos:
        - Se recupera la matriz de historial desde `GestionPrestamos`
          (logica de negocio).
        - Los datos se procesan con `collections.Counter` para agrupar libros
          mas prestados y usuarios mas activos.

        Visualizacion:
        - Se renderizan dos graficos (barras y pastel) sobre los lienzos
          de `FigureCanvasTkAgg` integrados en la interfaz `customtkinter`.
        - El redibujado es eficiente usando `draw_idle`.
        """
        matriz = self.prestamos.convertir_prestamos_a_matriz()

        self.ax_barras.clear()
        self.ax_pastel.clear()

        if not matriz:
            self.ax_barras.set_title("Libros mas prestados")
            self.ax_barras.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            self.ax_barras.set_xticks([])
            self.ax_barras.set_yticks([])

            self.ax_pastel.set_title("Usuarios activos")
            self.ax_pastel.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            self.ax_pastel.set_xticks([])
            self.ax_pastel.set_yticks([])

            self.canvas_barras.draw_idle()
            self.canvas_pastel.draw_idle()
            return

        # Matriz -> conteos de libros prestados y actividad de usuarios.
        conteo_libros = Counter(str(fila[0]) for fila in matriz)
        conteo_usuarios = Counter(str(fila[1]) for fila in matriz)

        top_libros = conteo_libros.most_common(5)
        top_usuarios = conteo_usuarios.most_common(5)

        etiquetas_libros: list[str] = []
        valores_libros: list[int] = []
        for id_libro, total in top_libros:
            libro = self.crud.obtener_libro(id_libro)
            etiquetas_libros.append(libro.titulo if libro is not None else f"Libro {id_libro}")
            valores_libros.append(total)

        self.ax_barras.bar(etiquetas_libros, valores_libros, color="#1d4ed8")
        self.ax_barras.set_title("Libros mas prestados")
        self.ax_barras.set_ylabel("Cantidad de prestamos")
        self.ax_barras.tick_params(axis="x", labelrotation=20)

        etiquetas_usuarios: list[str] = []
        valores_usuarios: list[int] = []
        for id_usuario, total in top_usuarios:
            usuario = self.crud.obtener_usuario(id_usuario)
            etiquetas_usuarios.append(
                usuario.nombre if usuario is not None else f"Usuario {id_usuario}"
            )
            valores_usuarios.append(total)

        self.ax_pastel.pie(
            valores_usuarios,
            labels=etiquetas_usuarios,
            autopct="%1.1f%%",
            startangle=90,
        )
        self.ax_pastel.set_title("Usuarios activos")

        # draw_idle mantiene la UI mas fluida que forzar redraw completo.
        self.canvas_barras.draw_idle()
        self.canvas_pastel.draw_idle()
