import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from tkcalendar import DateEntry  # pip install tkcalendar

from src.services.mantenimiento_service import MantenimientoService
from src.repositories.vehiculo_repository import VehiculoRepository


class MantenimientosScreen(ttk.Frame):
    """
    Pantalla de gestión de mantenimientos de vehículos.

    Usa:
      - MantenimientoService.crear_mantenimiento(...)
      - MantenimientoService.listar_mantenimientos()
      - MantenimientoService.eliminar_mantenimiento(...)
    """

    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._mantenimiento_actual_id = None

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_vehiculos_para_combo()
        self._cargar_mantenimientos_en_tabla()

    # ----------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("MantTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("MantSubtitle.TLabel", font=("Segoe UI", 10), foreground="#555555")

    # ----------------------------------------------------------
    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # HEADER
        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Gestión de mantenimientos",
            style="MantTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Registrar y administrar mantenimientos de los vehículos.",
            style="MantSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        # BODY
        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        # FORM
        form = ttk.LabelFrame(body, text="Nuevo mantenimiento", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        # Vehículo
        ttk.Label(form, text="Vehículo:").grid(row=0, column=0, sticky="w")
        self.combo_vehiculo = ttk.Combobox(form, state="readonly", width=40)
        self.combo_vehiculo.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Fechas
        ttk.Label(form, text="Fecha inicio:").grid(row=2, column=0, sticky="w")
        self.date_inicio = DateEntry(
            form,
            width=20,
            date_pattern="yyyy-mm-dd",
            state="readonly",
        )
        self.date_inicio.set_date(date.today())
        self.date_inicio.grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Fecha fin:").grid(row=4, column=0, sticky="w")
        self.date_fin = DateEntry(
            form,
            width=20,
            date_pattern="yyyy-mm-dd",
            state="readonly",
        )
        self.date_fin.set_date(date.today())
        self.date_fin.grid(row=5, column=0, sticky="w", pady=(0, 8))

        # Descripción
        ttk.Label(form, text="Descripción:").grid(row=6, column=0, sticky="w")
        self.text_descripcion = tk.Text(form, width=40, height=4)
        self.text_descripcion.grid(row=7, column=0, sticky="w", pady=(0, 8))

        # Botones
        btns = ttk.Frame(form)
        btns.grid(row=8, column=0, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Guardar mantenimiento", command=self._guardar_mantenimiento) \
            .grid(row=0, column=0, padx=(0, 5))

        ttk.Button(btns, text="Eliminar mantenimiento", command=self._eliminar_mantenimiento) \
            .grid(row=0, column=1, padx=5)

        # TABLA
        tabla_frame = ttk.LabelFrame(body, text="Listado de mantenimientos", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("id", "vehiculo", "inicio", "fin", "descripcion")
        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=15,
            selectmode="browse",
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("vehiculo", text="Vehículo")
        self.tree.heading("inicio", text="Inicio")
        self.tree.heading("fin", text="Fin")
        self.tree.heading("descripcion", text="Descripción")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("vehiculo", width=130)
        self.tree.column("inicio", width=90, anchor="center")
        self.tree.column("fin", width=90, anchor="center")
        self.tree.column("descripcion", width=250)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _limpiar_formulario(self):
        self._mantenimiento_actual_id = None
        self.combo_vehiculo.set("")
        self.date_inicio.set_date(date.today())
        self.date_fin.set_date(date.today())
        self.text_descripcion.delete("1.0", tk.END)
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    # ----------------------------------------------------------
    def _cargar_vehiculos_para_combo(self):
        """
        Llena el combo de vehículos.
        Formato: "id - Patente (Marca Modelo)"
        """
        try:
            vehiculos = VehiculoRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar vehículos.\n{e}")
            vehiculos = []

        items = []
        for v in vehiculos:
            if not v.activo:
                continue
            etiqueta = f"{v.id_vehiculo} - {v.patente} ({v.marca} {v.modelo})"
            items.append(etiqueta)

        self.combo_vehiculo["values"] = items

    # ----------------------------------------------------------
    def _cargar_mantenimientos_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, mantenimientos = MantenimientoService.listar_mantenimientos()
        if not ok:
            messagebox.showerror("Error", mantenimientos)
            return

        # Para mostrar algo más legible del vehículo, volvemos a buscarlo
        for m in mantenimientos:
            vehiculo = VehiculoRepository.obtener_por_id(m.id_vehiculo)
            if vehiculo is not None:
                txt_veh = f"{vehiculo.patente} ({vehiculo.marca} {vehiculo.modelo})"
            else:
                txt_veh = f"Vehículo {m.id_vehiculo}"

            self.tree.insert(
                "",
                "end",
                iid=str(m.id_mantenimiento),
                values=(
                    m.id_mantenimiento,
                    txt_veh,
                    m.fecha_inicio,
                    m.fecha_fin,
                    m.descripcion,
                ),
            )

    # ----------------------------------------------------------
    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item_id = sel[0]
        valores = self.tree.item(item_id, "values")

        self._mantenimiento_actual_id = int(valores[0])

        # Buscar el vehículo en el combo que matchee la patente/etiqueta
        vehiculo_txt = valores[1]
        for opt in self.combo_vehiculo["values"]:
            if vehiculo_txt in opt:
                self.combo_vehiculo.set(opt)
                break

        # Fechas
        try:
            f_ini = valores[2]
            f_fin = valores[3]
            self.date_inicio.set_date(f_ini)
            self.date_fin.set_date(f_fin)
        except Exception:
            pass

        # Descripción
        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", valores[4])

    # ----------------------------------------------------------
    def _guardar_mantenimiento(self):
        veh_sel = self.combo_vehiculo.get().strip()
        if not veh_sel:
            messagebox.showwarning("Validación", "Seleccioná un vehículo.")
            return

        try:
            id_vehiculo = int(veh_sel.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Validación", "No se pudo interpretar el vehículo seleccionado.")
            return

        f_inicio = self.date_inicio.get_date().isoformat()
        f_fin = self.date_fin.get_date().isoformat()

        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        if not descripcion:
            messagebox.showwarning("Validación", "La descripción no puede estar vacía.")
            return

        ok, r = MantenimientoService.crear_mantenimiento(
            id_vehiculo,
            f_inicio,
            f_fin,
            descripcion
        )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Mantenimiento registrado correctamente.")
        self._limpiar_formulario()
        self._cargar_mantenimientos_en_tabla()

    # ----------------------------------------------------------
    def _eliminar_mantenimiento(self):
        if self._mantenimiento_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un mantenimiento.")
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar este mantenimiento?"
        ):
            return

        ok, r = MantenimientoService.eliminar_mantenimiento(self._mantenimiento_actual_id)
        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", r)
        self._limpiar_formulario()
        self._cargar_mantenimientos_en_tabla()
