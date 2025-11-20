# src/ui/gui/dashboard_screen.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date

from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.mantenimiento_repository import MantenimientoRepository


class DashboardScreen(ttk.Frame):
    """
    Dashboard con indicadores y tarjetas.
    - ADMIN: todas las secciones
    - EMPLEADO: sólo clientes, alquileres, incidentes y mantenimientos
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

        self._configurar_estilos()
        self._construir_ui()

    # ----------------------------------------------------------------------
    # ESTILOS
    # ----------------------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        self.color_bg = "#EEF1F5"
        self.card_bg = "#FFFFFF"

        self.card_width = 210
        self.card_height = 150

        style.configure("Bg.TFrame", background=self.color_bg)

        style.configure(
            "Card.TFrame",
            background=self.card_bg,
            relief="solid",
            borderwidth=1,
        )

        style.configure(
            "CardTitle.TLabel",
            background=self.card_bg,
            foreground="#000000",
            font=("Segoe UI", 12, "bold"),
        )

        style.configure(
            "CardDesc.TLabel",
            background=self.card_bg,
            foreground="#333333",
            font=("Segoe UI", 10),
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )

        style.configure(
            "DashboardTitle.TLabel",
            font=("Segoe UI", 22, "bold"),
            background=self.color_bg,
        )

        style.configure(
            "DashboardSubtitle.TLabel",
            font=("Segoe UI", 11),
            background=self.color_bg,
            foreground="#444",
        )

    # ----------------------------------------------------------------------
    # UI
    # ----------------------------------------------------------------------
    def _construir_ui(self):
        self.columnconfigure(0, weight=1)

        # ---------- HEADER ----------
        header = ttk.Frame(self, style="Bg.TFrame", padding=20)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="RentaYa - Panel de gestión",
            style="DashboardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            header,
            text="Cerrar sesión",
            style="Primary.TButton",
            command=self.on_logout,
        ).grid(row=0, column=2, sticky="e")

        ttk.Label(
            header,
            text=f"{self.usuario.get('nombre_completo', 'Usuario')} ({self.usuario.get('rol', '')})",
            background=self.color_bg,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=1, sticky="e", padx=10)

        # ---------- INDICADORES ----------
        self._crear_indicadores()

        # ---------- TARJETAS ----------
        self._crear_cards()

        # ---------- FOOTER ----------
        footer = ttk.Frame(self, style="Bg.TFrame", padding=10)
        footer.grid(row=3, column=0)
        ttk.Label(
            footer,
            text="Sistema de Alquiler de Vehículos - TP DAO",
            background=self.color_bg,
        ).pack()

    # ----------------------------------------------------------------------
    # INDICADORES
    # ----------------------------------------------------------------------
    def _crear_indicadores(self):
        frame = ttk.Frame(self, style="Bg.TFrame", padding=20)
        frame.grid(row=1, column=0, sticky="ew")

        for i in range(4):
            frame.columnconfigure(i, weight=1)

        data = self._obtener_indicadores()

        items = [
            ("Vehículos disponibles", data["veh_disp"], "#4CAF50"),
            ("Alquileres abiertos", data["alq_abiertos"], "#FF9800"),
            ("Vehículos en mantenimiento", data["veh_mant"], "#E67E22"),
            ("Total vehículos", data["veh_total"], "#3A7AFE"),
        ]

        for col, (title, value, color) in enumerate(items):
            self._crear_indicador(frame, col, title, value, color)

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

        veh_disp = len(
            [
                v
                for v in vehiculos
                if v.activo and v.id_vehiculo not in bloqueados
            ]
        )

        alq_abiertos = len([a for a in alquileres if a.estado == "ABIERTO"])
        veh_mant = len(vehiculos_en_mant)
        veh_total = len(vehiculos)

        return {
            "veh_disp": veh_disp,
            "alq_abiertos": alq_abiertos,
            "veh_mant": veh_mant,
            "veh_total": veh_total,
        }

    def _crear_indicador(self, parent, col, titulo, valor, color):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.grid(row=0, column=col, padx=10, sticky="ew")

        ttk.Label(frame, text=titulo, style="CardDesc.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text=str(valor),
            font=("Segoe UI", 20, "bold"),
            background=self.card_bg,
            foreground=color,
        ).pack(anchor="w", pady=(5, 0))

    # ----------------------------------------------------------------------
    # TARJETAS (BOTONES GRANDES)
    # ----------------------------------------------------------------------
    def _crear_cards(self):
        frame = ttk.Frame(self, style="Bg.TFrame", padding=10)
        frame.grid(row=2, column=0)

        rol = (self.usuario.get("rol") or "").upper()

        if rol == "ADMIN":
            orden = [
                "Clientes",
                "Alquileres",
                "Incidentes",
                "Mantenimientos",
                "Vehículos",
                "Empleados",
                "Reportes",
            ]
        else:
            orden = [
                "Clientes",
                "Alquileres",
                "Incidentes",
                "Mantenimientos",
            ]

        cards = [(titulo, self.actions[titulo]) for titulo in orden]

        if len(cards) == 7:
            # layout 3 + 4 (admin)
            f1 = ttk.Frame(frame, style="Bg.TFrame")
            f1.grid(row=0, column=0, pady=10)
            for i in range(3):
                f1.columnconfigure(i, weight=1)

            for col, (titulo, callback) in enumerate(cards[:3]):
                self._crear_card(f1, 0, col, titulo, callback)

            f2 = ttk.Frame(frame, style="Bg.TFrame")
            f2.grid(row=1, column=0, pady=10)
            for i in range(4):
                f2.columnconfigure(i, weight=1)

            for col, (titulo, callback) in enumerate(cards[3:]):
                self._crear_card(f2, 0, col, titulo, callback)
        else:
            # layout genérico para EMPLEADO (hasta 4 tarjetas)
            cols = 2 if len(cards) <= 4 else 3
            for i in range(cols):
                frame.columnconfigure(i, weight=1)

            for idx, (titulo, callback) in enumerate(cards):
                row = idx // cols
                col = idx % cols
                self._crear_card(frame, row, col, titulo, callback)

    def _crear_card(self, parent, row, col, titulo, callback):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.grid(row=row, column=col, padx=20, pady=10, sticky="n")

        frame.grid_propagate(False)
        frame.configure(width=self.card_width, height=self.card_height)

        ttk.Label(frame, text=titulo, style="CardTitle.TLabel").pack()
        ttk.Label(
            frame,
            text=self._desc_para(titulo),
            style="CardDesc.TLabel",
        ).pack(pady=(5, 10))

        ttk.Button(
            frame,
            text="Abrir",
            style="Primary.TButton",
            command=callback,
        ).pack()

    def _desc_para(self, titulo):
        return {
            "Clientes": "Gestionar clientes",
            "Alquileres": "Crear y cerrar alquileres",
            "Incidentes": "Registrar multas o daños",
            "Mantenimientos": "Servicios del vehículo",
            "Vehículos": "Flota de vehículos",
            "Empleados": "Gestión de empleados",
            "Reportes": "Reportes del negocio",
        }.get(titulo, "")
