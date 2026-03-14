# Sistema de Gestión de Biblioteca (Python)

Documentación técnica y guía de usuario para el sistema de gestión de bibliotecas. Este proyecto implementa un CRUD completo para libros y usuarios, gestión de préstamos y visualización de estadísticas, todo empaquetado en una interfaz gráfica de escritorio.

**Fecha de análisis:** 14 de marzo de 2026

---

## 1. Arquitectura del Proyecto

El proyecto sigue una arquitectura por capas **Presentación (UI) → Servicios → Modelo**, con persistencia de datos en archivos JSON.

### 1.1. Jerarquía de Carpetas

```text
.
├── libros.json
├── prestamos.json
├── README.md
├── requirements.txt
├── usuarios.json
└── src/
    ├── main.py
    ├── main_gui.py
    ├── models/
    │   ├── __init__.py
    │   ├── libro.py
    │   ├── persona.py
    │   └── usuario.py
    ├── services/
    │   ├── __init__.py
    │   ├── crud_biblioteca.py
    │   ├── gestion_prestamos.py
    │   └── gestor_biblioteca.py
    └── ui/
        ├── __init__.py
        ├── app.py
        └── main_gui.py
```

### 1.2. Descripción de Módulos y Archivos

- **`src/main.py`**: Punto de entrada principal que inicia la interfaz gráfica (`BibliotecaApp`).
- **`src/main_gui.py`**: Punto de entrada alternativo que lanza una variante de la GUI (`MainGUI`) con foco en visualización.
- **`src/models/`**: Contiene las entidades del dominio (clases `Persona`, `Usuario`, `Libro`) donde se aplican los principios de POO.
- **`src/services/`**: Alberga la lógica de negocio.
  - `crud_biblioteca.py`: Servicio para operaciones CRUD y persistencia en JSON.
  - `gestion_prestamos.py`: Lógica para préstamos, devoluciones, validaciones y generación de datos para estadísticas.
- **`src/ui/`**: Componentes de la interfaz gráfica.
  - `app.py`: Define la clase base de la aplicación (`BibliotecaApp`) con `customtkinter`, incluyendo la maquetación de pestañas, formularios y la integración de gráficos Matplotlib.
  - `main_gui.py`: Subclase que especializa la visualización de estadísticas.
- **Archivos JSON**: `usuarios.json`, `libros.json`, y `prestamos.json` actúan como base de datos simple para persistir el estado de la aplicación.

---

## 2. Guía de Instalación y Despliegue

### 2.1. Requisitos

- **Python**: Versión **3.10** o superior.
- **Dependencias**: Las librerías necesarias se encuentran en `requirements.txt`.
  - `customtkinter>=5.2.0`
  - `matplotlib>=3.8.0`

### 2.2. Pasos de Instalación

1.  **Clonar o descargar el repositorio.**
2.  **Crear y activar un entorno virtual** (recomendado):
    ```powershell
    # Navegar a la raíz del proyecto
    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
3.  **Instalar las dependencias**:
    ```powershell
    pip install -r requirements.txt
    ```

### 2.3. Ejecución de la Aplicación

Una vez completada la instalación, puedes ejecutar la aplicación desde la raíz del proyecto:

- **Para la interfaz principal (CRUD + Préstamos + Estadísticas):**
  ```powershell
  python src/main.py
  ```
- **Para la variante de la GUI con foco en visualización:**
  ```powershell
  python src/main_gui.py
  ```

---

## 3. Implementación de Programación Orientada a Objetos (POO)

El proyecto está diseñado aplicando los tres pilares fundamentales de la POO.

### 3.1. Herencia

- La clase `Usuario` en `src/models/usuario.py` **hereda** de la clase base `Persona` (`src/models/persona.py`), reutilizando los atributos `id` y `nombre` y la lógica de validación asociada.
- En la capa de UI, `MainGUI` hereda de `BibliotecaApp` para especializar y sobreescribir la funcionalidad de la pestaña de estadísticas.

### 3.2. Encapsulamiento

- Todos los modelos (`Persona`, `Usuario`, `Libro`) utilizan **atributos privados** (ej. `__id`, `__nombre`) para proteger el estado interno.
- El acceso a estos atributos se controla mediante **propiedades (`@property`) y setters**, que centralizan las reglas de validación (ej. un ID debe ser positivo, un nombre no puede estar vacío).
- Las reglas de negocio, como no poder prestar un libro ya prestado, están encapsuladas dentro de los métodos de las clases (`Libro.prestar()`).

### 3.3. Polimorfismo

- Las clases `Persona`, `Usuario` y `Libro` implementan un método `obtener_detalle()`.
- Un cliente puede invocar este método sobre una lista de objetos heterogéneos (que contenga tanto `Usuario` como `Libro`) y cada objeto responderá ejecutando su propia versión del método, devolviendo una representación de sí mismo adaptada a su clase.

---

## 4. Características Funcionales

- **Gestión de Libros y Usuarios**: Formularios para crear, leer, actualizar y eliminar (CRUD) libros y usuarios, con persistencia automática en archivos JSON.
- **Sistema de Préstamos**: Lógica para prestar y devolver libros, validando la disponibilidad del libro, el límite de préstamos del usuario y la consistencia de las fechas.
- **Historial de Préstamos**: Todos los movimientos de préstamo y devolución se registran en `prestamos.json`.
- **Visualización de Estadísticas**: La pestaña "Estadísticas" muestra gráficos generados con Matplotlib:
  - **Gráfico de Barras**: Top 5 de los libros más prestados.
  - **Gráfico de Pastel**: Distribución de préstamos entre los 5 usuarios más activos.
- **Interfaz Gráfica Intuitiva**: Construida con `customtkinter`, organizada en pestañas para una navegación clara y fluida.
