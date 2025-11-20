import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date

from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.reports import reportes_tablas as rpt
from src.reports import reportes_graficos as rpt_g
from src.reports import reportes_export as rpt_x


class ReportesScreen(ttk.Frame):
    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("RepTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("RepSubtitle.TLabel", font=("Segoe UI", 10), foreground="#555555")

    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Reportes del negocio",
            style="RepTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Consultas sobre alquileres, incidentes y estado de la flota.",
            style="RepSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        filtros = ttk.LabelFrame(body, text="Filtros", padding=10)
        filtros.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        ttk.Label(filtros, text="Fecha desde:").grid(row=0, column=0, sticky="w")
        self.date_desde = DateEntry(
            filtros,
            width=12,
            date_pattern="yyyy-mm-dd",
            state="readonly",
        )
        self.date_desde.set_date(date.today())
        self.date_desde.grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Label(filtros, text="Fecha hasta:").grid(row=2, column=0, sticky="w")
        self.date_hasta = DateEntry(
            filtros,
            width=12,
            date_pattern="yyyy-mm-dd",
            state="readonly",
        )
        self.date_hasta.set_date(date.today())
        self.date_hasta.grid(row=3, column=0, sticky="w", pady=(0, 8))

        btns = ttk.Frame(filtros)
        btns.grid(row=4, column=0, pady=(10, 0), sticky="w")

        ttk.Button(
            btns,
            text="Resumen económico",
            command=self._mostrar_resumen_economico,
            width=22,
        ).grid(row=0, column=0, pady=2, sticky="w")

        ttk.Button(
            btns,
            text="Vehículos más alquilados",
            command=self._mostrar_top_vehiculos,
            width=22,
        ).grid(row=1, column=0, pady=2, sticky="w")

        ttk.Button(
            btns,
            text="Clientes con más alquileres",
            command=self._mostrar_top_clientes,
            width=22,
        ).grid(row=2, column=0, pady=2, sticky="w")

        ttk.Button(
            btns,
            text="Estado de flota (hoy)",
            command=self._mostrar_estado_flota,
            width=22,
        ).grid(row=3, column=0, pady=8, sticky="w")

        ttk.Label(
            filtros,
            text="Gráficos",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=5, column=0, sticky="w", pady=(12, 2))

        btns_g = ttk.Frame(filtros)
        btns_g.grid(row=6, column=0, pady=(2, 0), sticky="w")

        ttk.Button(
            btns_g,
            text="Gráfico resumen econ.",
            command=self._grafico_resumen_economico,
            width=22,
        ).grid(row=0, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_g,
            text="Gráfico top vehículos",
            command=self._grafico_top_vehiculos,
            width=22,
        ).grid(row=1, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_g,
            text="Gráfico top clientes",
            command=self._grafico_top_clientes,
            width=22,
        ).grid(row=2, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_g,
            text="Gráfico estado flota",
            command=self._grafico_estado_flota,
            width=22,
        ).grid(row=3, column=0, pady=2, sticky="w")

        ttk.Label(
            filtros,
            text="Exportar a PDF",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=7, column=0, sticky="w", pady=(12, 2))

        btns_x = ttk.Frame(filtros)
        btns_x.grid(row=8, column=0, pady=(2, 0), sticky="w")

        ttk.Button(
            btns_x,
            text="PDF resumen",
            command=self._exportar_resumen_pdf,
            width=22,
        ).grid(row=0, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_x,
            text="PDF top vehículos",
            command=self._exportar_top_vehiculos_pdf,
            width=22,
        ).grid(row=1, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_x,
            text="PDF top clientes",
            command=self._exportar_top_clientes_pdf,
            width=22,
        ).grid(row=2, column=0, pady=2, sticky="w")

        ttk.Button(
            btns_x,
            text="PDF estado flota",
            command=self._exportar_estado_flota_pdf,
            width=22,
        ).grid(row=3, column=0, pady=2, sticky="w")

        resultados = ttk.Frame(body)
        resultados.grid(row=0, column=1, sticky="nsew")
        resultados.rowconfigure(1, weight=1)
        resultados.columnconfigure(0, weight=1)

        self.lbl_resumen_1 = ttk.Label(resultados, text="", anchor="w")
        self.lbl_resumen_1.grid(row=0, column=0, sticky="w")
        self.lbl_resumen_2 = ttk.Label(resultados, text="", anchor="w")
        self.lbl_resumen_2.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.lbl_resumen_3 = ttk.Label(resultados, text="", anchor="w")
        self.lbl_resumen_3.grid(row=0, column=2, sticky="w", padx=(10, 0))

        tabla_frame = ttk.Frame(resultados)
        tabla_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tabla_frame,
            columns=("col1",),
            show="headings",
            height=15,
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

    def _limpiar_resumen_labels(self):
        self.lbl_resumen_1.config(text="")
        self.lbl_resumen_2.config(text="")
        self.lbl_resumen_3.config(text="")

    def _configurar_tabla(self, columnas):
        ids = [c["id"] for c in columnas]
        self.tree["columns"] = ids

        for col_id in ids:
            self.tree.heading(col_id, text="")
            self.tree.column(col_id, width=80, anchor="center")

        for c in columnas:
            self.tree.heading(c["id"], text=c.get("text", ""))
            self.tree.column(
                c["id"],
                width=c.get("width", 80),
                anchor=c.get("anchor", "center"),
            )

        for item in self.tree.get_children():
            self.tree.delete(item)

    def _obtener_rango_fechas(self):
        f_desde = self.date_desde.get_date().isoformat()
        f_hasta = self.date_hasta.get_date().isoformat()

        if f_desde > f_hasta:
            messagebox.showwarning(
                "Validación",
                "La fecha DESDE no puede ser mayor que la fecha HASTA.",
            )
            return None, None
        return f_desde, f_hasta

    def _mostrar_figura(self, fig, titulo: str):
        if fig is None:
            return

        win = tk.Toplevel(self)
        win.title(titulo)
        win.geometry("700x500")

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    def _mostrar_resumen_economico(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, data = rpt.obtener_resumen_economico(f_desde, f_hasta)
        if not ok:
            messagebox.showerror("Error", data)
            return

        self._configurar_tabla(
            [
                {"id": "concepto", "text": "Concepto", "width": 220, "anchor": "w"},
                {"id": "monto", "text": "Monto $", "width": 120, "anchor": "e"},
            ]
        )

        self._limpiar_resumen_labels()
        self.lbl_resumen_1.config(
            text=f"Período: {f_desde} a {f_hasta}"
        )
        self.lbl_resumen_2.config(
            text=f"Total alquileres: ${data['total_alquileres']:.2f}"
        )
        self.lbl_resumen_3.config(
            text=f"Total incidentes pagados: ${data['total_incidentes']:.2f}"
        )

        filas = [
            ("Alquileres", data["total_alquileres"]),
            ("Incidentes pagados", data["total_incidentes"]),
            ("TOTAL GENERAL", data["total_general"]),
        ]
        for concepto, monto in filas:
            self.tree.insert(
                "",
                "end",
                values=(
                    concepto,
                    f"{monto:.2f}",
                ),
            )

    def _mostrar_top_vehiculos(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, filas = rpt.obtener_top_vehiculos(f_desde, f_hasta, limite=20)
        if not ok:
            messagebox.showerror("Error", filas)
            return

        self._configurar_tabla(
            [
                {"id": "vehiculo", "text": "Vehículo", "width": 260, "anchor": "w"},
                {"id": "cantidad", "text": "Cant. alquileres", "width": 120, "anchor": "center"},
                {"id": "total", "text": "Total facturado $", "width": 140, "anchor": "e"},
            ]
        )

        self._limpiar_resumen_labels()
        self.lbl_resumen_1.config(
            text=f"Vehículos más alquilados ({f_desde} a {f_hasta})"
        )

        for row in filas:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["vehiculo"],
                    row["cantidad"],
                    f"{row['total']:.2f}",
                ),
            )

    def _mostrar_top_clientes(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, filas = rpt.obtener_top_clientes(f_desde, f_hasta, limite=20)
        if not ok:
            messagebox.showerror("Error", filas)
            return

        self._configurar_tabla(
            [
                {"id": "cliente", "text": "Cliente", "width": 220, "anchor": "w"},
                {"id": "dni", "text": "DNI", "width": 100, "anchor": "center"},
                {"id": "cantidad", "text": "Cant. alquileres", "width": 120, "anchor": "center"},
                {"id": "total", "text": "Total facturado $", "width": 140, "anchor": "e"},
            ]
        )

        self._limpiar_resumen_labels()
        self.lbl_resumen_1.config(
            text=f"Clientes con más alquileres ({f_desde} a {f_hasta})"
        )

        for row in filas:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["cliente"],
                    row["dni"],
                    row["cantidad"],
                    f"{row['total']:.2f}",
                ),
            )

    def _mostrar_estado_flota(self):
        hoy = date.today().isoformat()

        ok, data = rpt.obtener_estado_flota(hoy)
        if not ok:
            messagebox.showerror("Error", data)
            return

        self._configurar_tabla(
            [
                {"id": "vehiculo", "text": "Vehículo", "width": 260, "anchor": "w"},
                {"id": "estado", "text": "Estado", "width": 120, "anchor": "center"},
            ]
        )

        self._limpiar_resumen_labels()
        res = data["resumen"]
        self.lbl_resumen_1.config(
            text=f"Estado de la flota al {hoy}"
        )
        self.lbl_resumen_2.config(
            text=f"Disponibles: {res['disponibles']}  |  Alquilados: {res['alquilados']}"
        )
        self.lbl_resumen_3.config(
            text=f"En mantenimiento: {res['mantenimiento']}"
        )

        for row in data["detalle"]:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["vehiculo"],
                    row["estado"],
                ),
            )

    def _grafico_resumen_economico(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, fig_o_msg = rpt_g.grafico_resumen_economico(f_desde, f_hasta)
        if not ok:
            messagebox.showinfo("Información", fig_o_msg)
            return

        self._mostrar_figura(fig_o_msg, "Gráfico - Resumen económico")

    def _grafico_top_vehiculos(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, fig_o_msg = rpt_g.grafico_top_vehiculos(f_desde, f_hasta, limite=10)
        if not ok:
            messagebox.showinfo("Información", fig_o_msg)
            return

        self._mostrar_figura(fig_o_msg, "Gráfico - Vehículos más alquilados")

    def _grafico_top_clientes(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return

        ok, fig_o_msg = rpt_g.grafico_top_clientes(f_desde, f_hasta, limite=10)
        if not ok:
            messagebox.showinfo("Información", fig_o_msg)
            return

        self._mostrar_figura(fig_o_msg, "Gráfico - Clientes con más alquileres")

    def _grafico_estado_flota(self):
        hoy = date.today().isoformat()

        ok, fig_o_msg = rpt_g.grafico_estado_flota(hoy)
        if not ok:
            messagebox.showinfo("Información", fig_o_msg)
            return

        self._mostrar_figura(fig_o_msg, "Gráfico - Estado de la flota")

    def _elegir_ruta_pdf(self, nombre_sugerido):
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte en PDF",
            defaultextension=".pdf",
            initialfile=nombre_sugerido,
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        return ruta

    def _exportar_resumen_pdf(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return
        ruta = self._elegir_ruta_pdf("resumen_economico.pdf")
        if not ruta:
            return
        ok, msg = rpt_x.export_resumen_economico_pdf(ruta, f_desde, f_hasta)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)

    def _exportar_top_vehiculos_pdf(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return
        ruta = self._elegir_ruta_pdf("top_vehiculos.pdf")
        if not ruta:
            return
        ok, msg = rpt_x.export_top_vehiculos_pdf(ruta, f_desde, f_hasta, limite=20)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)

    def _exportar_top_clientes_pdf(self):
        f_desde, f_hasta = self._obtener_rango_fechas()
        if not f_desde:
            return
        ruta = self._elegir_ruta_pdf("top_clientes.pdf")
        if not ruta:
            return
        ok, msg = rpt_x.export_top_clientes_pdf(ruta, f_desde, f_hasta, limite=20)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)

    def _exportar_estado_flota_pdf(self):
        hoy = date.today().isoformat()
        ruta = self._elegir_ruta_pdf("estado_flota.pdf")
        if not ruta:
            return
        ok, msg = rpt_x.export_estado_flota_pdf(ruta, hoy)
        if ok:
            messagebox.showinfo("OK", msg)
        else:
            messagebox.showerror("Error", msg)
