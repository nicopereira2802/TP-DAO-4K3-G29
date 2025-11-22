import tkinter as tk
import customtkinter as ctk
from pathlib import Path

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class HomeScreen(ctk.CTkFrame):
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

        # Ajustes post-inicialización
        self.after(60, self._recentrar_texto_inicio_veh)
        self.hero.bind("<Configure>", self._on_hero_resize)

    # ================= IMÁGENES =======================
    def _load_raw_image(self, filename):
        # Ajusta la ruta según tu estructura de carpetas
        ruta = Path(__file__).resolve().parent.parent.parent.parent / "assets" / filename
        if not ruta.exists():
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
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- NAVBAR (Top) ---
        topbar = ctk.CTkFrame(self, height=60, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(0, weight=1)
        
        # Logo / Título
        ctk.CTkLabel(
            topbar,
            text="RentaYa",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
        ).pack(side="left", padx=20, pady=10)

        # Botones de Navegación
        nav_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)

        btn_kwargs = {
            "font": ctk.CTkFont(family="Segoe UI", size=14),
            "fg_color": "transparent",
            "text_color": ("gray10", "gray90"),
            "hover_color": ("gray70", "gray30"),
            "width": 80
        }

        ctk.CTkButton(nav_frame, text="Inicio", command=self._mostrar_inicio, **btn_kwargs).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="Vehículos", command=self._mostrar_vehiculos, **btn_kwargs).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="Contacto", command=self._mostrar_contacto, **btn_kwargs).pack(side="left", padx=5)
        
        ctk.CTkButton(
            nav_frame, 
            text="Iniciar sesión",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            width=120,
            fg_color="#3A7AFE", 
            hover_color="#2c5dcf",
            command=self.on_login_click,
        ).pack(side="left", padx=15)

        # --- ZONA CENTRAL (Canvas + Scrollbar) ---
        center = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        center.grid(row=1, column=0, sticky="nsew")
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=1)

        # Canvas nativo de TK
        self.hero = tk.Canvas(center, highlightthickness=0, bd=0, bg="#212121")
        self.hero.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self.hero_scrollbar = ctk.CTkScrollbar(center, orientation="vertical")
        self.hero_scrollbar.grid(row=0, column=1, sticky="ns")
        self.hero_scrollbar.configure(command=lambda *args: None)

        self._draw_inicio()

        # --- FOOTER ---
        footer = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=("gray85", "gray20"))
        footer.grid(row=2, column=0, sticky="ew")
        
        ctk.CTkLabel(
            footer,
            text="Sistema de Alquiler de Vehículos - TP DAO",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
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
            self.hero.create_image(0, 0, anchor="nw", image=self.current_bg_img, tags=("bg",))
        else:
            self.hero.create_rectangle(0, 0, width, height, fill="#2b2b2b", outline="")

        self.hero.configure(scrollregion=(0, 0, width, height))
        return width, height

    # ================= SECCIONES ======================
    def _draw_inicio(self):
        self.current_section = "inicio"
        width, height = self._draw_background("inicio")

        shadow_offset = 2
        
        self.hero.create_text(
            width // 2 + shadow_offset, height // 3 + shadow_offset,
            text="Descubrí tu próximo destino",
            fill="black", font=("Segoe UI", 36, "bold"), width=900, justify="center", tags=("inicio_text",)
        )
        t1 = self.hero.create_text(
            width // 2, height // 3,
            text="Descubrí tu próximo destino",
            fill="#FFC107", font=("Segoe UI", 36, "bold"), width=900, justify="center", tags=("inicio_text",)
        )

        t2 = self.hero.create_text(
            width // 2, height // 3 + 50,
            text="Alquiler de vehículos fácil, moderno y seguro.",
            fill="white", font=("Segoe UI", 18), width=900, justify="center", tags=("inicio_text",)
        )
        
        t3 = self.hero.create_text(
            width // 2, height // 3 + 85,
            text="Gestioná clientes, reservas y flota en un solo sistema.",
            fill="#dddddd", font=("Segoe UI", 14), width=900, justify="center", tags=("inicio_text",)
        )

        self.hero_text_ids = [t1, t2, t3]
        self.hero_scrollbar.grid_remove()
        self.hero.unbind_all("<MouseWheel>")

    def _draw_vehiculos(self):
        from src.repositories.vehiculo_repository import VehiculoRepository
        from src.repositories.mantenimiento_repository import MantenimientoRepository
        from src.repositories.alquiler_repository import AlquilerRepository
        from datetime import date, datetime

        self.current_section = "vehiculos"
        width, height = self._draw_background("vehiculos")
        self.hero_scrollbar.grid(row=0, column=1, sticky="ns")

        # Capa oscura para resaltar tarjetas
        self.hero.create_rectangle(0, 0, width, height, fill="black", stipple="gray12", tags=("bg_dim",))

        hoy = date.today()
        vehiculos = VehiculoRepository.listar()
        alquileres = AlquilerRepository.listar()
        mantenimientos = MantenimientoRepository.listar()

        def parse_f(s):
            try: return datetime.strptime(s, "%Y-%m-%d").date()
            except: return None

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

        disponibles = [v for v in vehiculos if v.activo and v.id_vehiculo not in (ocupados | en_mantenimiento)]

        self.hero.create_text(
            width // 2 + 2, 72,
            text="Vehículos disponibles", fill="black", font=("Segoe UI", 28, "bold"),
            width=900, justify="center", tags=("cards",)
        )
        title_id = self.hero.create_text(
            width // 2, 70,
            text="Vehículos disponibles", fill="white", font=("Segoe UI", 28, "bold"),
            width=900, justify="center", tags=("cards",)
        )
        self.hero_text_ids = [title_id]

        if not disponibles:
            self.hero.create_text(width // 2, 160, text="No hay vehículos disponibles en este momento.",
                fill="white", font=("Segoe UI", 14), width=600, justify="center", tags=("cards",))
            self._setup_cards_scrolling(top_y=120, total_rows=1, card_h=0, v_gap=0, height=height)
            return

        card_w = 330
        card_h = 140
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

            self.hero.create_rectangle(x0, y0, x1, y1, fill="#333333", outline="#555555", width=1, tags=("cards",))

            self.hero.create_text(x0 + 15, y0 + 25, anchor="w", text=f"{v.marca} {v.modelo}",
                font=("Segoe UI", 14, "bold"), fill="#ffffff", tags=("cards",))

            self.hero.create_text(x1 - 15, y0 + 25, anchor="e", text=f"${v.precio_por_dia:.2f} / día",
                font=("Segoe UI", 12, "bold"), fill="#4CAF50", tags=("cards",))

            subtitulo_texto = f"Año {v.anio}"
            if v.tipo: subtitulo_texto += f"  •  {str(v.tipo).capitalize()}"

            self.hero.create_text(x0 + 15, y0 + 55, anchor="w", text=subtitulo_texto,
                font=("Segoe UI", 11), fill="#aaaaaa", tags=("cards",))

            self.hero.create_text(x0 + 15, y0 + 80, anchor="w", text=f"Patente: {v.patente}",
                font=("Segoe UI", 10), fill="#aaaaaa", tags=("cards",))

            km_val = getattr(v, "km_actual", 0) or 0
            comb_val = getattr(v, "combustible_actual", 0.0) or 0.0
            texto_km_comb = f"KM: {km_val:.0f}   •   Comb: {comb_val:.1f} L"
            color_km_comb = "#aaaaaa"
            if comb_val < 5:
                texto_km_comb += "  ⚠ Bajo"
                color_km_comb = "#FF5555"

            self.hero.create_text(x0 + 15, y0 + 105, anchor="w", text=texto_km_comb,
                font=("Segoe UI", 10), fill=color_km_comb, tags=("cards",))

        total_rows = (len(disponibles) + cols - 1) // cols
        self._setup_cards_scrolling(top_y, total_rows, card_h, v_gap, height)

    def _setup_cards_scrolling(self, top_y, total_rows, card_h, v_gap, height_canvas):
        content_height = top_y + total_rows * (card_h + v_gap) + 50
        self.cards_content_height = content_height
        view_h = self.hero.winfo_height() or height_canvas
        self.cards_view_height = view_h
        self.cards_offset = 0
        self.cards_max_offset = max(0, content_height - view_h)

        self.hero_scrollbar.configure(command=self._on_cards_scroll)
        self._update_cards_scrollbar()
        self.hero.unbind_all("<MouseWheel>")
        self.hero.bind_all("<MouseWheel>", lambda e: self._scroll_cards(-1 * 40 if e.delta > 0 else 40) if self.current_section == "vehiculos" else None)

    def _scroll_cards(self, delta):
        if self.cards_max_offset <= 0: return
        new_offset = max(0, min(self.cards_offset + delta, self.cards_max_offset))
        real_delta = new_offset - self.cards_offset
        if real_delta == 0: return
        self.cards_offset = new_offset
        self.hero.move("cards", 0, -real_delta)
        self._update_cards_scrollbar()

    def _on_cards_scroll(self, *args):
        if self.cards_max_offset <= 0: return
        if args[0] == "moveto":
            self._scroll_cards((float(args[1]) * self.cards_max_offset) - self.cards_offset)
        elif args[0] == "scroll":
            step = 40 if args[2] == "units" else self.cards_view_height
            self._scroll_cards(int(args[1]) * step)

    def _update_cards_scrollbar(self):
        if self.cards_content_height <= 0 or self.cards_view_height <= 0:
            self.hero_scrollbar.set(0.0, 1.0); return
        first = self.cards_offset / self.cards_content_height
        last = (self.cards_offset + self.cards_view_height) / self.cards_content_height
        self.hero_scrollbar.set(first, min(last, 1.0))

    def _draw_contacto(self):
        self.current_section = "contacto"
        width, height = self._draw_background("contacto")

        self.hero_scrollbar.grid_remove()
        self.hero.unbind_all("<MouseWheel>")

        # --- POSICIONAMIENTO ---
        center_x = width // 2
        text_x = center_x + 180  
        center_y = height // 2
        
        # Subimos más el título para dejar espacio a las letras grandes
        title_y = center_y - 140 
        
        # Punto base para el cuerpo
        body_y = center_y + 20   

        # Agrandamos un poco el ancho permitido para que no corte las oraciones
        text_width = 600

        # --- 1. TÍTULO (Más Grande) ---
        self.hero.create_text(
            text_x, title_y,
            text="Contacto", 
            fill="#1F6AA5",  
            font=("Roboto", 44, "bold"), # Agrandado a 44
            width=text_width, 
            justify="center",
            tags=("contacto_text",)
        )

        # --- 2. CUERPO DEL TEXTO ---
        intro = (
            "Somos el Grupo 29 del Trabajo Práctico Integrador\n"
            "Diseño y Arquitectura de Objetos (DAO) - UTN FRC."
        )
        
        detalles = (
            "\n\n"
            "🛠️ TECNOLOGÍA\n"
            "Python 3 • CustomTkinter • SQLite3 • Patrones MVC\n\n"
            "👥 INTEGRANTES\n"
            "Castro Maximiliano\n"
            "Pereira Puca Nicolas Francisco\n"
            "Koncurat Joaquín Ernesto\n\n"
            "✉️ CONSULTAS\n"
            "dao.g29.4k3@frc.utn.edu.ar"
        )

        # Parte 1: Introducción (Letra 16)
        # Lo subimos un poco (body_y - 70) para separarlo del bloque de abajo
        self.hero.create_text(
            text_x, body_y - 70,
            text=intro, 
            fill="#222222", 
            font=("Arial", 16, "bold"), # Agrandado a 16
            width=text_width, 
            justify="center",
            tags=("contacto_text",)
        )

        # Parte 2: Detalles (Letra 13)
        # Lo bajamos un poco (body_y + 50)
        self.hero.create_text(
            text_x, body_y + 50,
            text=detalles, 
            fill="#444444", 
            font=("Arial", 13), # Agrandado a 13
            width=text_width, 
            justify="center",
            tags=("contacto_text",)
        )

    # ================= UTILIDADES ======================
    def _recentrar_texto_inicio_veh(self):
        if self.current_section != "inicio": return
        if not self.hero_text_ids: return
        width = self.hero.winfo_width()
        height = self.hero.winfo_height()
        base_y = height // 3
        step = 45
        for i, tid in enumerate(self.hero_text_ids):
            self.hero.coords(tid, width // 2, base_y + i * step)

    def _on_hero_resize(self, event):
        if self.current_section == "inicio": self._draw_inicio()
        elif self.current_section == "vehiculos": self._draw_vehiculos()
        elif self.current_section == "contacto": self._draw_contacto()

    def _mostrar_inicio(self): self._draw_inicio()
    def _mostrar_vehiculos(self): self._draw_vehiculos()
    def _mostrar_contacto(self): self._draw_contacto()