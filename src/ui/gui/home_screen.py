import tkinter as tk
from tkinter import ttk
from pathlib import Path

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class HomeScreen(ttk.Frame):
    def __init__(self, parent, on_login_click):
        super().__init__(parent)
        self.on_login_click = on_login_click

        self._raw_images = {}
        self.current_bg_img = None
        self.hero_text_ids = []
        self.current_section = "inicio"

        # atributos para scroll de tarjetas
        self.cards_offset = 0
        self.cards_max_offset = 0
        self.cards_content_height = 0
        self.cards_view_height = 0

        self._cargar_imagenes()
        self._construir_ui()

        self.after(60, self._recentrar_texto_inicio_veh)
        self.hero.bind("<Configure>", self._on_hero_resize)

    # ================= IMÁGENES =======================
    def _load_raw_image(self, filename):
        ruta = Path(__file__).resolve().parent.parent.parent / "assets" / filename
        if not ruta.exists():
            return None

        if Image is not None:
            try:
                return Image.open(str(ruta))
            except Exception:
                return None
        else:
            try:
                return tk.PhotoImage(file=str(ruta))
            except tk.TclError:
                return None

    def _cargar_imagenes(self):
        self._raw_images["inicio"] = self._load_raw_image("home_bg.png")
        self._raw_images["vehiculos"] = self._load_raw_image("vehiculos_bg.png")
        self._raw_images["contacto"] = self._load_raw_image("contacto_bg.png")

    def _get_scaled_image(self, section_key, width, height):
        raw = self._raw_images.get(section_key) or self._raw_images.get("inicio")
        if raw is None:
            return None

        if Image is not None and isinstance(raw, Image.Image):
            img = raw.resize((max(1, width), max(1, height)), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        else:
            return raw

    # ================= UI =============================
    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # NAVBAR
        topbar = ttk.Frame(self)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.columnconfigure(0, weight=1)

        ttk.Label(
            topbar,
            text="RentaYa - Alquiler de Vehículos",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=10)

        nav = ttk.Frame(topbar)
        nav.grid(row=0, column=1, sticky="e", padx=20)

        style = ttk.Style()
        style.configure(
            "Nav.TButton",
            padding=(10, 5),
            relief="flat",
            font=("Segoe UI", 10),
        )

        ttk.Button(nav, text="Inicio", style="Nav.TButton",
                   command=self._mostrar_inicio).pack(side="left", padx=5)
        ttk.Button(nav, text="Vehículos", style="Nav.TButton",
                   command=self._mostrar_vehiculos).pack(side="left", padx=5)
        ttk.Button(nav, text="Contacto", style="Nav.TButton",
                   command=self._mostrar_contacto).pack(side="left", padx=5)
        ttk.Button(
            nav, text="Iniciar sesión",
            style="Nav.TButton",
            command=self.on_login_click,
        ).pack(side="left", padx=5)

        # ZONA CENTRAL: Canvas + Scrollbar (el fondo SIEMPRE está en este canvas)
        center = ttk.Frame(self)
        center.grid(row=1, column=0, sticky="nsew")
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)

        self.hero = tk.Canvas(center, highlightthickness=0, bd=0)
        self.hero.grid(row=0, column=0, sticky="nsew")

        self.hero_scrollbar = ttk.Scrollbar(center, orient="vertical")
        self.hero_scrollbar.grid(row=0, column=1, sticky="ns")

        # Por defecto, sin scroll “real”
        self.hero_scrollbar.configure(command=lambda *args: None)

        self._draw_inicio()

        # FOOTER
        footer = ttk.Frame(self)
        footer.grid(row=2, column=0, sticky="ew")
        ttk.Label(
            footer,
            text="Sistema de Alquiler de Vehículos - TP DAO",
            foreground="gray",
        ).pack(pady=5)

    # ================= FONDO ==========================
    def _draw_background(self, section_key):
        self.hero.delete("all")
        self.hero_text_ids = []

        width = self.hero.winfo_width() or 1100
        height = self.hero.winfo_height() or 600

        bg = self._get_scaled_image(section_key, width, height)
        if bg:
            self.current_bg_img = bg
            # Imagen de fondo SIEMPRE en (0,0)
            self.hero.create_image(0, 0, anchor="nw", image=self.current_bg_img, tags=("bg",))

        # no usamos yview para scroll, pero dejo el scrollregion por las dudas
        self.hero.configure(scrollregion=(0, 0, width, height))
        return width, height

    # ================= SECCIONES ======================
    def _draw_inicio(self):
        self.current_section = "inicio"

        width, height = self._draw_background("inicio")

        t1 = self.hero.create_text(
            width // 2, height // 3,
            text="Descubrí tu próximo destino",
            fill="yellow",
            font=("Segoe UI", 30, "bold"),
            width=900,
            justify="center",
            tags=("inicio_text",),
        )
        t2 = self.hero.create_text(
            width // 2, height // 3 + 32,
            text="Alquiler de vehículos fácil, moderno y seguro.",
            fill="brown",
            font=("Segoe UI", 15),
            width=900,
            justify="center",
            tags=("inicio_text",),
        )
        t3 = self.hero.create_text(
            width // 2, height // 3 + 64,
            text="Gestioná clientes, reservas y flota en un solo sistema.",
            fill="brown",
            font=("Segoe UI", 15),
            width=900,
            justify="center",
            tags=("inicio_text",),
        )

        self.hero_text_ids = [t1, t2, t3]

        # no necesitamos scrollbar acá
        self.hero_scrollbar.grid_remove()
        self.hero.unbind_all("<MouseWheel>")

    def _draw_vehiculos(self):
        from src.repositories.vehiculo_repository import VehiculoRepository
        from src.repositories.mantenimiento_repository import MantenimientoRepository
        from src.repositories.alquiler_repository import AlquilerRepository
        from datetime import date, datetime

        self.current_section = "vehiculos"
        width, height = self._draw_background("vehiculos")

        # mostramos scrollbar
        self.hero_scrollbar.grid(row=0, column=1, sticky="ns")

        hoy = date.today()
        vehiculos = VehiculoRepository.listar()
        alquileres = AlquilerRepository.listar()
        mantenimientos = MantenimientoRepository.listar()

        def parse_f(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None

        ocupados = set()
        for a in alquileres:
            if a.estado == "ABIERTO":
                fi, ff = parse_f(a.fecha_inicio), parse_f(a.fecha_fin)
                if fi and ff and fi <= hoy <= ff:
                    ocupados.add(a.id_vehiculo)

        en_mantenimiento = set()
        for m in mantenimientos:
            fi, ff = parse_f(m.fecha_inicio), parse_f(m.fecha_fin)
            if fi and ff and fi <= hoy <= ff:
                en_mantenimiento.add(m.id_vehiculo)

        disponibles = [
            v for v in vehiculos
            if v.activo and v.id_vehiculo not in (ocupados | en_mantenimiento)
        ]

        title_id = self.hero.create_text(
            width // 2, 70,
            text="Vehículos disponibles",
            fill="white",
            font=("Segoe UI", 26, "bold"),
            width=900,
            justify="center",
            tags=("cards",),   # lo trato como parte del contenido scrollable
        )
        self.hero_text_ids = [title_id]

        if not disponibles:
            self.hero.create_text(
                width // 2, 160,
                text="No hay vehículos disponibles en este momento.",
                fill="black",
                font=("Segoe UI", 12),
                width=600,
                justify="center",
                tags=("cards",),
            )
            self._setup_cards_scrolling(top_y=120, total_rows=1, card_h=0, v_gap=0, height=height)
            return

        card_w = 330
        card_h = 130  # antes 110, lo subimos para que entren KM y combustible
        h_gap = 25
        v_gap = 25
        top_y = 120

        cols_max = 4
        cols_min = 2
        cols = max(cols_min, min(cols_max, max(1, width // (card_w + h_gap))))

        total_cards_width = cols * card_w + (cols - 1) * h_gap
        left_margin = max(20, (width - total_cards_width) // 2)

        for idx, v in enumerate(disponibles):
            row = idx // cols
            col = idx % cols

            x0 = left_margin + col * (card_w + h_gap)
            y0 = top_y + row * (card_h + v_gap)
            x1 = x0 + card_w
            y1 = y0 + card_h

            # Todo lo que tenga tag "cards" se va a mover con el scroll
            self.hero.create_rectangle(
                x0, y0, x1, y1,
                fill="white",
                outline="#333333",
                width=1,
                tags=("cards",),
            )

            self.hero.create_text(
                x0 + 10, y0 + 20,
                anchor="w",
                text=f"{v.marca} {v.modelo}",
                font=("Segoe UI", 14, "bold"),
                fill="#111111",
                tags=("cards",),
            )

            self.hero.create_text(
                x1 - 10, y0 + 20,
                anchor="e",
                text=f"${v.precio_por_dia:.2f} / día",
                font=("Segoe UI", 12, "bold"),
                fill="#1a7f37",
                tags=("cards",),
            )

            subtitulo_texto = f"Año {v.anio}"
            if v.tipo:
                subtitulo_texto += f"  •  {str(v.tipo).capitalize()}"

            self.hero.create_text(
                x0 + 10, y0 + 44,
                anchor="w",
                text=subtitulo_texto,
                font=("Segoe UI", 10),
                fill="#555555",
                tags=("cards",),
            )

            self.hero.create_text(
                x0 + 10, y0 + 70,
                anchor="w",
                text=f"Patente: {v.patente}   •   Estado: Disponible",
                font=("Segoe UI", 9),
                fill="#222222",
                tags=("cards",),
            )

            # ===== Nueva línea: KM y combustible actual =====
            km_val = getattr(v, "km_actual", 0) or 0
            comb_val = getattr(v, "combustible_actual", 0.0) or 0.0

            texto_km_comb = f"KM: {km_val:.0f}   •   Combustible: {comb_val:.1f} L"
            color_km_comb = "#222222"
            if comb_val < 5:
                texto_km_comb += "   •   Combustible bajo"
                color_km_comb = "#AA0000"

            self.hero.create_text(
                x0 + 10, y0 + 94,
                anchor="w",
                text=texto_km_comb,
                font=("Segoe UI", 9),
                fill=color_km_comb,
                tags=("cards",),
            )

        total_rows = (len(disponibles) + cols - 1) // cols
        self._setup_cards_scrolling(top_y, total_rows, card_h, v_gap, height)

    def _setup_cards_scrolling(self, top_y, total_rows, card_h, v_gap, height_canvas):
        # altura total del contenido scrollable (tarjetas + título)
        content_height = top_y + total_rows * (card_h + v_gap)
        self.cards_content_height = content_height

        view_h = self.hero.winfo_height() or height_canvas
        self.cards_view_height = view_h
        self.cards_offset = 0
        self.cards_max_offset = max(0, content_height - view_h + 20)

        # configurar scrollbar para usar nuestro manejador
        self.hero_scrollbar.configure(command=self._on_cards_scroll)
        self._update_cards_scrollbar()

        # vincular rueda del mouse
        self.hero.unbind_all("<MouseWheel>")

        def _on_mousewheel(event):
            if self.current_section != "vehiculos":
                return
            step = 40
            direction = -1 if event.delta > 0 else 1
            self._scroll_cards(direction * step)

        self.hero.bind_all("<MouseWheel>", _on_mousewheel)

    def _scroll_cards(self, delta):
        if self.cards_max_offset <= 0:
            return

        new_offset = self.cards_offset + delta
        if new_offset < 0:
            new_offset = 0
        if new_offset > self.cards_max_offset:
            new_offset = self.cards_max_offset

        real_delta = new_offset - self.cards_offset
        if real_delta == 0:
            return

        self.cards_offset = new_offset
        # movemos SOLO los items con tag "cards"
        self.hero.move("cards", 0, -real_delta)
        self._update_cards_scrollbar()

    def _on_cards_scroll(self, *args):
        if self.cards_max_offset <= 0:
            return

        if args[0] == "moveto":
            frac = float(args[1])
            new_offset = frac * self.cards_max_offset
            self._scroll_cards(new_offset - self.cards_offset)
        elif args[0] == "scroll":
            amount = int(args[1])
            unit = args[2]
            step = 40 if unit == "units" else self.cards_view_height
            self._scroll_cards(amount * step)

    def _update_cards_scrollbar(self):
        if self.cards_content_height <= 0 or self.cards_view_height <= 0:
            self.hero_scrollbar.set(0.0, 1.0)
            return

        first = self.cards_offset / self.cards_content_height
        last = (self.cards_offset + self.cards_view_height) / self.cards_content_height
        if last > 1.0:
            last = 1.0
        self.hero_scrollbar.set(first, last)

    def _draw_contacto(self):
        self.current_section = "contacto"
        width, height = self._draw_background("contacto")

        text_x_center = int(width * 0.65)
        top_y = int(height * 0.20)

        self.hero.create_text(
            text_x_center, top_y,
            text="Contacto",
            fill="#111111",
            font=("Segoe UI", 20, "bold"),
            width=int(width * 0.5),
            justify="center",
        )

        texto = (
            "Somos el Grupo 29 del Trabajo Práctico de Diseño y Arquitectura de Objetos (DAO), "
            "curso 4K3 de la UTN FRC.\n\n"
            "Este sistema de alquiler de vehículos fue desarrollado como proyecto académico.\n\n"
            "Integrantes del grupo 29:\n"
            " - [Integrante 1]\n"
            " - [Integrante 2]\n"
            " - [Integrante 3]\n"
            " - [Integrante 4]\n\n"
            "Consultas:\n"
            "dao.g29.4k3@frc.utn.edu.ar  |  alquileres.rentaya@frc.utn.edu.ar"
        )

        self.hero.create_text(
            text_x_center, top_y + 200,
            text=texto,
            fill="#222222",
            font=("Segoe UI", 11),
            width=int(width * 0.5),
            justify="left",
        )

        self.hero_scrollbar.grid_remove()
        self.hero.unbind_all("<MouseWheel>")

    # ================= UTILIDADES ======================
    def _recentrar_texto_inicio_veh(self):
        if self.current_section != "inicio":
            return
        if not self.hero_text_ids:
            return

        width = self.hero.winfo_width()
        height = self.hero.winfo_height()
        base_y = height // 3
        step = 32
        for i, tid in enumerate(self.hero_text_ids):
            self.hero.coords(tid, width // 2, base_y + i * step)

    def _on_hero_resize(self, event):
        if self.current_section == "inicio":
            self._draw_inicio()
        elif self.current_section == "vehiculos":
            self._draw_vehiculos()
        elif self.current_section == "contacto":
            self._draw_contacto()

    # ================= BOTONES NAV =====================
    def _mostrar_inicio(self):
        self._draw_inicio()

    def _mostrar_vehiculos(self):
        self._draw_vehiculos()

    def _mostrar_contacto(self):
        self._draw_contacto()
