import customtkinter as ctk
from tkinter import ttk

# Importamos las pantallas (asegúrate de que los nombres de archivo coincidan)
from src.ui.gui.home_screen import HomeScreen
from src.ui.gui.login_screen import LoginScreen
from src.ui.gui.dashboard_screen import DashboardScreen

from src.ui.gui.clientes_screen import ClientesScreen
from src.ui.gui.empleados_screen import EmpleadosScreen
from src.ui.gui.vehiculos_screen import VehiculosScreen
from src.ui.gui.alquileres_screen import AlquileresScreen
from src.ui.gui.incidentes_screen import IncidentesScreen
from src.ui.gui.mantenimientos_screen import MantenimientosScreen
from src.ui.gui.reportes_screen import ReportesScreen

# Importamos los servicios
from src.services.cliente_service import ClienteService
from src.services.empleado_service import EmpleadoService

# --- CONFIGURACIÓN GLOBAL DEL TEMA ---
# Esto aplica el modo oscuro/claro según tu sistema y el color azul por defecto
ctk.set_appearance_mode("System")  # Opciones: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Opciones: "blue" (default), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title("Sistema de Alquiler de Vehículos")
        self.geometry("1100x700")
        self.minsize(1100, 650)
        self.resizable(True, True)

        # Estado de la sesión
        self._usuario_logueado = None

        # Instancia global de servicios que se comparten
        self._cliente_service = ClienteService()
        self._empleado_service = EmpleadoService()

        # Contenedor principal (ahora es un CTkFrame)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self._frame_actual = None
        
        # Iniciar en la pantalla Home
        self.mostrar_home()

    def _cambiar_frame(self, nuevo_frame):
        """Destruye el frame actual y muestra el nuevo."""
        if self._frame_actual is not None:
            self._frame_actual.destroy()
        self._frame_actual = nuevo_frame
        self._frame_actual.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # MÉTODOS DE NAVEGACIÓN (Lógica intacta)
    # ------------------------------------------------------------------

    def mostrar_home(self):
        home = HomeScreen(
            self.container,
            on_login_click=self.mostrar_login
        )
        self._cambiar_frame(home)

    def mostrar_login(self):
        login = LoginScreen(
            self.container,
            on_login_ok=self._on_login_ok,
            on_cancel=self.mostrar_home
        )
        self._cambiar_frame(login)

    def _on_login_ok(self, usuario_dict):
        self._usuario_logueado = usuario_dict
        self.mostrar_dashboard()

    def mostrar_dashboard(self):
        dashboard = DashboardScreen(
            parent=self.container,
            usuario=self._usuario_logueado,
            on_logout=self._on_logout,
            on_open_clientes=self.mostrar_clientes,
            on_open_alquileres=self.mostrar_alquileres,
            on_open_incidentes=self.mostrar_incidentes,
            on_open_mantenimientos=self.mostrar_mantenimientos,
            on_open_vehiculos=self.mostrar_vehiculos,
            on_open_empleados=self.mostrar_empleados,
            on_open_reportes=self.mostrar_reportes,
        )
        self._cambiar_frame(dashboard)

    def _on_logout(self):
        self._usuario_logueado = None
        self.mostrar_home()

    # --- Pantallas Específicas ---

    def mostrar_clientes(self):
        pantalla = ClientesScreen(
            parent=self.container,
            cliente_service=self._cliente_service,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_empleados(self):
        pantalla = EmpleadosScreen(
            parent=self.container,
            empleado_service=self._empleado_service,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_vehiculos(self):
        pantalla = VehiculosScreen(
            parent=self.container,
            usuario_actual=self._usuario_logueado,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_alquileres(self):
        pantalla = AlquileresScreen(
            parent=self.container,
            usuario_actual=self._usuario_logueado,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_incidentes(self):
        pantalla = IncidentesScreen(
            parent=self.container,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_mantenimientos(self):
        pantalla = MantenimientosScreen(
            parent=self.container,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

    def mostrar_reportes(self):
        pantalla = ReportesScreen(
            parent=self.container,
            on_back=self.mostrar_dashboard
        )
        self._cambiar_frame(pantalla)

if __name__ == "__main__":
    app = App()
    app.mainloop()