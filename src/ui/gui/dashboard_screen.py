import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, date

from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.mantenimiento_repository import MantenimientoRepository


class DashboardScreen(ctk.CTkFrame):
    """
    Dashboard moderno con indicadores y tarjetas de menú.
    """

    def __init__(
        self,
        parent,
        usuario,
        on_logout,
        on_open_clientes,
        on_open_alquileres,
        on_open_incidentes,
        on_open_mantenimientos,
        on_open_vehiculos=None,
        on_open_empleados=None,
        on_open_reportes=None,
    ):
        super().__init__(parent)
        self.usuario = usuario or {}

        self.on_logout = on_logout
        self.actions = {
            "Clientes": on_open_clientes,
            "Alquileres": on_open_alquileres,
            "Incidentes": on_open_incidentes,
            "Mantenimientos": on_open_mantenimientos,
            "Vehículos": on_open_vehiculos,
            "Empleados": on_open_empleados,
            "Reportes": on_open_reportes,
        }

        self._construir_ui()

    def _construir_ui(self):
        # Usamos grid principal
        self.grid_rowconfigure(1, weight=1) # El cuerpo se expande
        self.grid_columnconfigure(0, weight=1)

        # ---------- HEADER ----------
        header = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=("gray85", "gray20"))
        header.grid(row=0, column=0, sticky="ew")
        
        # Título
        ctk.CTkLabel(
            header,
            text="Panel de Gestión",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        ).pack(side="left", padx=25, pady=15)

        # Botón Cerrar Sesión
        ctk.CTkButton(
            header,
            text="Cerrar sesión",
            fg_color="#c0392b", # Rojo
            hover_color="#a93226",
            width=120,
            height=35,
            command=self.on_logout,
        ).pack(side="right", padx=25)

        # Info Usuario
        rol = self.usuario.get('rol', '')
        nombre = self.usuario.get('nombre_completo', 'Usuario')
        ctk.CTkLabel(
            header,
            text=f"{nombre} ({rol})",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        ).pack(side="right", padx=10)

        # ---------- BODY (Scrollable) ----------
        # Usamos ScrollableFrame por si la pantalla es chica
        body = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        # Título Sección Indicadores
        ctk.CTkLabel(body, text="Estado del Negocio (Hoy)", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").pack(fill="x", padx=30, pady=(20, 10))

        # Indicadores
        self._crear_indicadores(body)

        # Separador
        ttk.Separator(body, orient="horizontal").pack(fill="x", padx=30, pady=20)

        # Título Sección Accesos
        ctk.CTkLabel(body, text="Accesos Rápidos", font=ctk.CTkFont(size=18, weight="bold"), anchor="w").pack(fill="x", padx=30, pady=(0, 10))

        # Menu Cards
        self._crear_cards(body)

        # Footer
        ctk.CTkLabel(body, text="Sistema RentaYa v2.0 - TP DAO", text_color="gray").pack(pady=30)

    # ----------------------------------------------------------------------
    # INDICADORES
    # ----------------------------------------------------------------------
    def _crear_indicadores(self, parent):
        data = self._obtener_indicadores()
        
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20)
        
        # Configurar grid de 4 columnas iguales
        for i in range(4): container.grid_columnconfigure(i, weight=1)

        # Crear las 4 tarjetas
        self._crear_tarjeta_kpi(container, 0, "Disponibles", data["veh_disp"], "#2cc985") # Verde
        self._crear_tarjeta_kpi(container, 1, "Alquilados", data["alq_abiertos"], "#f39c12") # Naranja
        self._crear_tarjeta_kpi(container, 2, "Mantenimiento", data["veh_mant"], "#e74c3c") # Rojo
        self._crear_tarjeta_kpi(container, 3, "Total Flota", data["veh_total"], "#3498db") # Azul

    def _crear_tarjeta_kpi(self, parent, col, titulo, valor, color_texto):
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=0, column=col, padx=10, pady=5, sticky="ew")
        
        # Título pequeño arriba
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14)).pack(pady=(15, 0))
        
        # Valor grande en color
        ctk.CTkLabel(
            card, 
            text=str(valor), 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color_texto
        ).pack(pady=(0, 15))

    # ----------------------------------------------------------------------
    # LÓGICA DE DATOS (Sin cambios, solo adaptada al contexto)
    # ----------------------------------------------------------------------
    def _parsear_fecha(self, s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _obtener_indicadores(self):
        hoy = date.today()

        vehiculos = VehiculoRepository.listar()
        alquileres = AlquilerRepository.listar()
        mantenimientos = MantenimientoRepository.listar()

        # --- vehículos bloqueados por alquiler ABIERTO hoy ---
        vehiculos_ocupados = set()
        for a in alquileres:
            if a.estado != "ABIERTO":
                continue
            fi = self._parsear_fecha(a.fecha_inicio)
            ff = self._parsear_fecha(a.fecha_fin)
            if fi and ff and fi <= hoy <= ff:
                vehiculos_ocupados.add(a.id_vehiculo)

        # --- vehículos bloqueados por mantenimiento hoy ---
        vehiculos_en_mant = set()
        for m in mantenimientos:
            fi = self._parsear_fecha(m.fecha_inicio)
            ff = self._parsear_fecha(m.fecha_fin)
            if fi and ff and fi <= hoy <= ff:
                vehiculos_en_mant.add(m.id_vehiculo)

        bloqueados = vehiculos_ocupados | vehiculos_en_mant

        veh_disp = len([v for v in vehiculos if v.activo and v.id_vehiculo not in bloqueados])
        alq_abiertos = len([a for a in alquileres if a.estado == "ABIERTO"])
        veh_mant = len(vehiculos_en_mant)
        veh_total = len(vehiculos)

        return {
            "veh_disp": veh_disp,
            "alq_abiertos": alq_abiertos,
            "veh_mant": veh_mant,
            "veh_total": veh_total,
        }

    # ----------------------------------------------------------------------
    # MENÚ DE TARJETAS
    # ----------------------------------------------------------------------
    def _crear_cards(self, parent):
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20)

        rol = (self.usuario.get("rol") or "").upper()

        if rol == "ADMIN":
            orden = ["Clientes", "Alquileres", "Incidentes", "Mantenimientos", "Vehículos", "Empleados", "Reportes"]
        else:
            orden = ["Clientes", "Alquileres", "Incidentes", "Mantenimientos"]

        # Configurar columnas (4 columnas max)
        cols = 4
        for i in range(cols): grid_frame.grid_columnconfigure(i, weight=1)

        for idx, titulo in enumerate(orden):
            callback = self.actions.get(titulo)
            row = idx // cols
            col = idx % cols
            
            if callback:
                self._crear_boton_menu(grid_frame, row, col, titulo, callback)

    def _crear_boton_menu(self, parent, row, col, titulo, callback):
        # Usamos un botón grande que parezca una tarjeta
        btn = ctk.CTkButton(
            parent,
            text=f"{titulo}\n\n{self._desc_para(titulo)}", # Salto de línea para subtítulo
            command=callback,
            height=100,
            corner_radius=12,
            fg_color=("white", "#333333"), # Blanco en light, Gris oscuro en dark
            text_color=("black", "white"), # Texto opuesto al fondo
            hover_color=("gray90", "gray25"),
            font=ctk.CTkFont(size=16, weight="bold"),
            border_width=1,
            border_color=("gray80", "gray40")
        )
        # Ajuste para que el subtitulo se vea más chico (no soportado nativamente en un solo string, 
        # pero visualmente funciona bien como bloque)
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _desc_para(self, titulo):
        # Descripciones cortas para el subtítulo del botón
        return {
            "Clientes": "ABM Clientes",
            "Alquileres": "Operaciones",
            "Incidentes": "Multas/Daños",
            "Mantenimientos": "Taller",
            "Vehículos": "Flota",
            "Empleados": "Usuarios",
            "Reportes": "Estadísticas",
        }.get(titulo, "")