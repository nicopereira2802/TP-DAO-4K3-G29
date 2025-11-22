
# 🚗 Sistema de Gestión de Alquiler de Vehículos (RentaYa)

Trabajo Práctico Integrador - Diseño y Arquitectura de Objetos (DAO)
**UTN FRC - Grupo 29**

Este sistema es una aplicación de escritorio para la administración integral de una empresa de alquiler de autos. Permite gestionar clientes, vehículos, empleados, alquileres, mantenimientos e incidentes, además de generar reportes gráficos y en PDF.

---

## 📋 Requisitos Previos

* Tener instalado **Python 3.10** o superior.
* Sistema Operativo: Windows, macOS o Linux.

---

## ⚙️ Instalación de Dependencias

El proyecto utiliza librerías externas para la interfaz moderna, el manejo de fechas y la generación de reportes.

Abre una terminal (consola) en la carpeta del proyecto y ejecuta el siguiente comando:

```bash
pip install customtkinter tkcalendar matplotlib reportlab Pillow
Librerías utilizadas:

customtkinter: Interfaz gráfica moderna (Modo oscuro/claro).

tkcalendar: Selector visual de fechas.

matplotlib: Generación de gráficos estadísticos.

reportlab: Exportación de reportes a PDF.

Pillow: Manejo de imágenes.

🚀 Cómo Ejecutar el Sistema
Asegúrate de estar ubicado en la carpeta raíz del proyecto (donde está main_gui.py).

Ejecuta el siguiente comando en la terminal:

Bash

python main_gui.py
(Nota: Si tienes múltiples versiones de Python, intenta con python3 main_gui.py o py main_gui.py).

🔑 Credenciales de Acceso
Si la base de datos ya cuenta con usuarios cargados, puedes utilizar las siguientes credenciales de administrador para probar el sistema:

Usuario: admin

Contraseña: admin (o la que hayas configurado en tu script SQL inicial)

🏗️ Arquitectura y Patrones de Diseño
El sistema fue construido siguiendo una Arquitectura en Capas para garantizar la escalabilidad y el desacoplamiento:

UI (Presentación): Vistas implementadas con CustomTkinter.

Services (Lógica de Negocio): Validaciones y reglas del negocio.

Repositories (Persistencia): Acceso a datos con SQLite.

Domain (Entidades): Modelos de datos.

Patrones de Diseño Aplicados:
Singleton: Implementado en la clase DatabaseConnection para centralizar y optimizar la conexión a la base de datos SQLite, garantizando una única instancia activa.

Factory Method: Implementado en VehiculoFactory para desacoplar la lógica de creación de vehículos, permitiendo la instanciación flexible de distintos tipos de unidades (Auto, Camioneta, Moto).

📂 Estructura del Proyecto
/src: Código fuente principal.

/domain: Clases entidad (Cliente, Vehículo, etc.).

/repositories: Acceso a BD (SQL).

/services: Lógica de negocio.

/ui: Interfaces gráficas.

/reports: Lógica de reportes y gráficos.

/assets: Imágenes y recursos visuales.

main_gui.py: Punto de entrada de la aplicación.

Desarrollado por:

Castro Maximiliano

Pereira Puca Nicolas Francisco

Koncurat Joaquín Ernesto

