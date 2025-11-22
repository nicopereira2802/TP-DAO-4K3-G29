import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date

# pip install customtkinter tkcalendar matplotlib
import customtkinter as ctk
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.reports import reportes_tablas as rpt
from src.reports import reportes_graficos as rpt_g
from src.reports import reportes_export as rpt_x
from src.services.reporte_service import ReporteService
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.vehiculo_repository import VehiculoRepository


class ReportesScreen(ctk.CTkFrame):
    """
    Pantalla de Reportes (Versión Modernizada).
    """
    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_clientes_combo()

    def _configurar_estilos_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        
        bg_color = "#2b2b2b"
        text_color = "white"
        selected_bg = "#1f538d"
        header_bg = "#3a3a3a"
        
        style.configure("Treeview",
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        borderwidth=0,
                        rowheight=25)
        style.map('Treeview', background=[('selected', selected_bg)])
        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#565b5e')])

    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Reportes y Estadísticas", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Análisis de desempeño del negocio", 
                     text_color="gray").pack(anchor="w")

        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=80, height=30, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right", anchor="center")

        # --- BODY ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(1, weight=1) # Derecha se expande
        body.grid_rowconfigure(0, weight=1)

        # 1. PANEL IZQUIERDO: FILTROS (Scrollable)
        filtros_frame = ctk.CTkScrollableFrame(body, width=300, corner_radius=10, label_text="Filtros y Acciones")
        filtros_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        
        # --- Sección Fechas ---
        ctk.CTkLabel(filtros_frame, text="Rango de Fechas", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        
        dates_container = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        dates_container.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dates_container, text="Desde:").pack(side="left", padx=5)
        self.date_desde = DateEntry(dates_container, width=10, date_pattern="yyyy-mm-dd")
        self.date_desde.pack(side="left", padx=5)
        self.date_desde.set_date(date.today())

        dates_container2 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        dates_container2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dates_container2, text="Hasta: ").pack(side="left", padx=5)
        self.date_hasta = DateEntry(dates_container2, width=10, date_pattern="yyyy-mm-dd")
        self.date_hasta.pack(side="left", padx=5)
        self.date_hasta.set_date(date.today())

        # --- Sección Cliente ---
        ctk.CTkLabel(filtros_frame, text="Filtrar por Cliente", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(15,0))
        self.combo_cliente = ctk.CTkComboBox(filtros_frame, state="readonly")
        self.combo_cliente.set("Seleccionar Cliente")
        self.combo_cliente.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(filtros_frame, text="Ver Historial Cliente", fg_color="#555", hover_color="#333",
                      command=self._mostrar_alquileres_por_cliente).pack(fill="x", padx=5, pady=5)

        # --- Sección Tablas ---
        ctk.CTkLabel(filtros_frame, text="Reportes Tabulares", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(20,5))
        
        btn_style = {"fg_color": "transparent", "border_width": 1, "text_color": ("gray10", "gray90")}
        
        ctk.CTkButton(filtros_frame, text="Alquileres por Mes", command=self._mostrar_alquileres_por_mes, **btn_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="Alquileres por Trimestre", command=self._mostrar_alquileres_por_trimestre, **btn_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="Top Vehículos", command=self._mostrar_top_vehiculos, **btn_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="Top Clientes", command=self._mostrar_top_clientes, **btn_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="Resumen Económico", command=self._mostrar_resumen_economico, **btn_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="Estado Flota (Hoy)", command=self._mostrar_estado_flota, **btn_style).pack(fill="x", padx=5, pady=2)

        # --- Sección Gráficos ---
        ctk.CTkLabel(filtros_frame, text="Gráficos Visuales", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(20,5))
        # Botones de gráficos con color suave
        gf_style = {"fg_color": "#3A7AFE", "hover_color": "#2c5dcf"}
        
        ctk.CTkButton(filtros_frame, text="📊 Facturación Mensual", command=self._grafico_facturacion_mensual, **gf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="💰 Resumen Económico", command=self._grafico_resumen_economico, **gf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="🏆 Top Vehículos", command=self._grafico_top_vehiculos, **gf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="👥 Top Clientes", command=self._grafico_top_clientes, **gf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="🚗 Estado Flota", command=self._grafico_estado_flota, **gf_style).pack(fill="x", padx=5, pady=2)

        # --- Sección PDF ---
        ctk.CTkLabel(filtros_frame, text="Exportar PDF", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(20,5))
        pdf_style = {"fg_color": "#c0392b", "hover_color": "#a93226"}
        
        ctk.CTkButton(filtros_frame, text="📄 PDF Resumen", command=self._exportar_resumen_pdf, **pdf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="📄 PDF Top Vehículos", command=self._exportar_top_vehiculos_pdf, **pdf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="📄 PDF Top Clientes", command=self._exportar_top_clientes_pdf, **pdf_style).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(filtros_frame, text="📄 PDF Estado Flota", command=self._exportar_estado_flota_pdf, **pdf_style).pack(fill="x", padx=5, pady=2)


        # 2. PANEL DERECHO: RESULTADOS
        resultados_frame = ctk.CTkFrame(body, corner_radius=10)
        resultados_frame.grid(row=0, column=1, sticky="nsew")
        resultados_frame.grid_rowconfigure(1, weight=1)
        resultados_frame.grid_columnconfigure(0, weight=1)

        # Etiquetas de resumen superior
        resumen_top = ctk.CTkFrame(resultados_frame, fg_color="transparent")
        resumen_top.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        self.lbl_resumen_1 = ctk.CTkLabel(resumen_top, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_resumen_1.pack(side="left", padx=(0, 20))
        
        self.lbl_resumen_2 = ctk.CTkLabel(resumen_top, text="")
        self.lbl_resumen_2.pack(side="left", padx=(0, 20))
        
        self.lbl_resumen_3 = ctk.CTkLabel(resumen_top, text="")
        self.lbl_resumen_3.pack(side="left")

        # Tabla
        self.tree = ttk.Treeview(resultados_frame, columns=("col1"), show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        scroll_y = ctk.CTkScrollbar(resultados_frame, command=self.tree.yview)
        scroll_y.grid(row=1, column=1, sticky="ns", pady=(0, 10), padx=(0,5))
        self.tree.configure(yscrollcommand=scroll_y.set)

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------
    def _cargar_clientes_combo(self):
        try:
            clientes = ClienteRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando clientes: {e}")
            clientes = []

        items = []
        for c in clientes:
            if getattr(c, "activo", True):
                cid = getattr(c, "id", None)
                nombre = f"{getattr(c, 'dni', '')} - {getattr(c, 'nombre', '')} {getattr(c, 'apellido', '')}"
                items.append(f"{cid} - {nombre}")
        
        self.combo_cliente.configure(values=items)

    def _limpiar_resumen_labels(self):
        self.lbl_resumen_1.configure(text="")
        self.lbl_resumen_2.configure(text="")
        self.lbl_resumen_3.configure(text="")

    def _configurar_tabla(self, columnas):
        ids = [c["id"] for c in columnas]
        self.tree["columns"] = ids
        for col_id in ids:
            self.tree.heading(col_id, text="")
            self.tree.column(col_id, width=80, anchor="center")

        for c in columnas:
            self.tree.heading(c["id"], text=c.get("text", ""))
            self.tree.column(c["id"], width=c.get("width", 80), anchor=c.get("anchor", "center"))

        for item in self.tree.get_children():
            self.tree.delete(item)

    def _obtener_rango_fechas(self):
        f_desde = self.date_desde.get_date().isoformat()
        f_hasta = self.date_hasta.get_date().isoformat()
        if f_desde > f_hasta:
            messagebox.showwarning("Fechas", "La fecha DESDE no puede ser mayor que HASTA.")
            return None, None
        return f_desde, f_hasta

    def _mostrar_figura(self, fig, titulo: str):
        if fig is None: return
        
        # Ventana emergente moderna
        win = ctk.CTkToplevel(self)
        win.title(titulo)
        win.geometry("700x500")
        # Hacerla modal (opcional)
        # win.grab_set()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    # --------------------------------------------------------------
    # Reportes TABULARES (Lógica Original)
    # --------------------------------------------------------------
    def _mostrar_resumen_economico(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde: return

        ok, data = rpt.obtener_resumen_economico(f_desde, f_hasta)
        if not ok: messagebox.showerror("Error", data); return

        self._configurar_tabla([
            {"id": "concepto", "text": "Concepto", "width": 220, "anchor": "w"},
            {"id": "monto", "text": "Monto $", "width": 120, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        self.lbl_resumen_1.configure(text=f"Período: {f_desde} a {f_hasta}")
        
        filas = [
            ("Alquileres", data["total_alquileres"]),
            ("Incidentes", data["total_incidentes"]),
            ("TOTAL", data["total_general"]),
        ]
        for concepto, monto in filas:
            self.tree.insert("", "end", values=(concepto, f"{monto:.2f}"))

    def _mostrar_top_vehiculos(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde: return

        ok, filas = rpt.obtener_top_vehiculos(f_desde, f_hasta, limite=20)
        if not ok: messagebox.showerror("Error", filas); return

        self._configurar_tabla([
            {"id": "vehiculo", "text": "Vehículo", "width": 260, "anchor": "w"},
            {"id": "cantidad", "text": "Alquileres", "width": 100, "anchor": "center"},
            {"id": "total", "text": "Total $", "width": 120, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        self.lbl_resumen_1.configure(text=f"Top Vehículos ({f_desde} a {f_hasta})")

        for row in filas:
            self.tree.insert("", "end", values=(row["vehiculo"], row["cantidad"], f"{row['total']:.2f}"))

    def _mostrar_top_clientes(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde: return

        ok, filas = rpt.obtener_top_clientes(f_desde, f_hasta, limite=20)
        if not ok: messagebox.showerror("Error", filas); return

        self._configurar_tabla([
            {"id": "cliente", "text": "Cliente", "width": 200, "anchor": "w"},
            {"id": "dni", "text": "DNI", "width": 100, "anchor": "center"},
            {"id": "cantidad", "text": "Cant.", "width": 80, "anchor": "center"},
            {"id": "total", "text": "Total $", "width": 120, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        self.lbl_resumen_1.configure(text="Top Clientes")

        for row in filas:
            self.tree.insert("", "end", values=(row["cliente"], row["dni"], row["cantidad"], f"{row['total']:.2f}"))

    def _mostrar_estado_flota(self):
        hoy = date.today().isoformat()
        ok, data = rpt.obtener_estado_flota(hoy)
        if not ok: messagebox.showerror("Error", data); return

        self._configurar_tabla([
            {"id": "vehiculo", "text": "Vehículo", "width": 260, "anchor": "w"},
            {"id": "estado", "text": "Estado", "width": 120, "anchor": "center"},
        ])
        self._limpiar_resumen_labels()
        res = data["resumen"]
        self.lbl_resumen_1.configure(text=f"Disp: {res['disponibles']}")
        self.lbl_resumen_2.configure(text=f"Alq: {res['alquilados']}")
        self.lbl_resumen_3.configure(text=f"Mant: {res['mantenimiento']}")

        for row in data["detalle"]:
            self.tree.insert("", "end", values=(row["vehiculo"], row["estado"]))

    def _mostrar_alquileres_por_cliente(self):
        sel = self.combo_cliente.get()
        if "Seleccionar" in sel or not sel: messagebox.showwarning("Atención", "Seleccioná un cliente"); return
        try: id_cli = int(sel.split(" - ")[0])
        except: return

        ok, alquileres = ReporteService.alquileres_por_cliente(id_cli)
        if not ok: messagebox.showerror("Error", alquileres); return

        self._configurar_tabla([
            {"id": "id", "text": "ID", "width": 50},
            {"id": "ini", "text": "Inicio", "width": 90},
            {"id": "fin", "text": "Fin", "width": 90},
            {"id": "est", "text": "Estado", "width": 80},
            {"id": "tot", "text": "Total", "width": 100, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        self.lbl_resumen_1.configure(text=f"Historial de {sel.split(' - ')[1]}")

        for a in alquileres:
            self.tree.insert("", "end", values=(a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.estado, f"{a.total}"))

    def _mostrar_alquileres_por_mes(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, filas = rpt.obtener_alquileres_por_mes(f_d, f_h)
        if not ok: return
        
        self._configurar_tabla([
            {"id": "p", "text": "Periodo", "width": 100},
            {"id": "c", "text": "Cant", "width": 80},
            {"id": "t", "text": "Total", "width": 120, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        for r in filas:
            self.tree.insert("", "end", values=(r["periodo"], r["cantidad"], f"{r['total']:.2f}"))

    def _mostrar_alquileres_por_trimestre(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, filas = rpt.obtener_alquileres_por_trimestre(f_d, f_h)
        if not ok: return

        self._configurar_tabla([
            {"id": "a", "text": "Año", "width": 80},
            {"id": "tri", "text": "Trimestre", "width": 80},
            {"id": "c", "text": "Cant", "width": 80},
            {"id": "t", "text": "Total", "width": 120, "anchor": "e"},
        ])
        self._limpiar_resumen_labels()
        for r in filas:
            self.tree.insert("", "end", values=(r["anio"], r["trimestre"], r["cantidad"], f"{r['total']:.2f}"))

    # --------------------------------------------------------------
    # GRÁFICOS
    # --------------------------------------------------------------
    def _grafico_resumen_economico(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, fig = rpt_g.grafico_resumen_economico(f_d, f_h)
        if ok: self._mostrar_figura(fig, "Resumen Económico")

    def _grafico_top_vehiculos(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, fig = rpt_g.grafico_top_vehiculos(f_d, f_h)
        if ok: self._mostrar_figura(fig, "Top Vehículos")

    def _grafico_top_clientes(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, fig = rpt_g.grafico_top_clientes(f_d, f_h)
        if ok: self._mostrar_figura(fig, "Top Clientes")

    def _grafico_estado_flota(self):
        ok, fig = rpt_g.grafico_estado_flota()
        if ok: self._mostrar_figura(fig, "Estado de Flota")

    def _grafico_facturacion_mensual(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ok, fig = rpt_g.grafico_facturacion_mensual(f_d, f_h)
        if ok: self._mostrar_figura(fig, "Facturación Mensual")

    # --------------------------------------------------------------
    # PDF
    # --------------------------------------------------------------
    def _elegir_ruta(self, default):
        return filedialog.asksaveasfilename(title="Guardar PDF", defaultextension=".pdf", initialfile=default, filetypes=[("PDF", "*.pdf")])

    def _exportar_resumen_pdf(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ruta = self._elegir_ruta("resumen.pdf")
        if ruta: 
            ok, msg = rpt_x.export_resumen_economico_pdf(ruta, f_d, f_h)
            messagebox.showinfo("Info", msg)

    def _exportar_top_vehiculos_pdf(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ruta = self._elegir_ruta("top_vehiculos.pdf")
        if ruta:
            ok, msg = rpt_x.export_top_vehiculos_pdf(ruta, f_d, f_h)
            messagebox.showinfo("Info", msg)

    def _exportar_top_clientes_pdf(self):
        f_d, f_h = self._obtener_rango_fechas()
        if not f_d: return
        ruta = self._elegir_ruta("top_clientes.pdf")
        if ruta:
            ok, msg = rpt_x.export_top_clientes_pdf(ruta, f_d, f_h)
            messagebox.showinfo("Info", msg)

    def _exportar_estado_flota_pdf(self):
        ruta = self._elegir_ruta("estado_flota.pdf")
        if ruta:
            ok, msg = rpt_x.export_estado_flota_pdf(ruta)
            messagebox.showinfo("Info", msg)