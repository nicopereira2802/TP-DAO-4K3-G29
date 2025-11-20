import tkinter as tk
from tkinter import ttk, messagebox

from src.services.incidente_service import IncidenteService
from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.vehiculo_repository import VehiculoRepository


class IncidentesScreen(ttk.Frame):
    """
    Pantalla de gestión de incidentes.

    Usa IncidenteService para CRUD real.
    Se asume que IncidenteService expone:
      - listar_incidentes()
      - crear_incidente(id_alquiler, tipo, descripcion, monto)
      - marcar_incidente_como_pagado(id_incidente)
    """

    TIPOS_VALIDOS = ["MULTA", "DANO", "OTRO"]

    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._incidente_actual_id = None

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_alquileres_para_combo()
        self._cargar_incidentes_en_tabla()

    # ----------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("IncTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("IncSubtitle.TLabel", font=("Segoe UI", 10), foreground="#555555")

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
            text="Gestión de incidentes",
            style="IncTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Registrar multas, daños y otros incidentes asociados a alquileres.",
            style="IncSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        # BODY
        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        # FORM
        form = ttk.LabelFrame(body, text="Nuevo incidente", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        # Alquiler
        ttk.Label(form, text="Alquiler:").grid(row=0, column=0, sticky="w")
        self.combo_alquiler = ttk.Combobox(form, state="readonly", width=40)
        self.combo_alquiler.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Tipo
        ttk.Label(form, text="Tipo de incidente:").grid(row=2, column=0, sticky="w")
        self.combo_tipo = ttk.Combobox(
            form,
            values=self.TIPOS_VALIDOS,
            state="readonly",
            width=20,
        )
        self.combo_tipo.grid(row=3, column=0, sticky="w", pady=(0, 8))

        # Descripción
        ttk.Label(form, text="Descripción:").grid(row=4, column=0, sticky="w")
        self.text_descripcion = tk.Text(form, width=38, height=4)
        self.text_descripcion.grid(row=5, column=0, sticky="w", pady=(0, 8))

        # Monto
        ttk.Label(form, text="Monto ($):").grid(row=6, column=0, sticky="w")
        vcmd_monto = (self.register(self._validar_monto), "%P")
        self.entry_monto = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_monto,
        )
        self.entry_monto.grid(row=7, column=0, sticky="w", pady=(0, 8))

        # Botones
        btns = ttk.Frame(form)
        btns.grid(row=8, column=0, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Guardar incidente", command=self._guardar_incidente) \
            .grid(row=0, column=0, padx=(0, 5))

        ttk.Button(btns, text="Marcar como pagado", command=self._marcar_pagado) \
            .grid(row=0, column=1, padx=5)

        # TABLA
        tabla_frame = ttk.LabelFrame(body, text="Listado de incidentes", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("id", "alquiler", "tipo", "descripcion", "monto", "estado")
        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=15,
            selectmode="browse",
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("alquiler", text="Alquiler")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("monto", text="Monto $")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("alquiler", width=90, anchor="center")
        self.tree.column("tipo", width=80, anchor="center")
        self.tree.column("descripcion", width=220)
        self.tree.column("monto", width=80, anchor="e")
        self.tree.column("estado", width=80, anchor="center")

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
    def _validar_monto(self, valor: str) -> bool:
        if valor == "":
            return True
        try:
            v = float(valor)
        except ValueError:
            return False
        return v >= 0

    def _limpiar_formulario(self):
        self._incidente_actual_id = None
        self.combo_alquiler.set("")
        self.combo_tipo.set("")
        self.text_descripcion.delete("1.0", tk.END)
        self.entry_monto.delete(0, tk.END)
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    # ----------------------------------------------------------
    def _cargar_alquileres_para_combo(self):
        """
        Llena el combo de alquileres con algo legible:
        "id - DNI - Nombre Apellido - Patente (Marca Modelo)"
        """
        try:
            alquileres = AlquilerRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar alquileres.\n{e}")
            alquileres = []

        items = []
        for a in alquileres:
            # cliente
            cliente = ClienteRepository.obtener_por_id(a.id_cliente)
            if cliente is not None:
                nombre_cli = getattr(cliente, "nombre", "")
                apellido_cli = getattr(cliente, "apellido", "")
                dni_cli = getattr(cliente, "dni", "")
                txt_cli = f"{dni_cli} - {nombre_cli} {apellido_cli}".strip()
            else:
                txt_cli = f"Cliente {a.id_cliente}"

            # vehiculo
            vehiculo = VehiculoRepository.obtener_por_id(a.id_vehiculo)
            if vehiculo is not None:
                txt_veh = f"{vehiculo.patente} ({vehiculo.marca} {vehiculo.modelo})"
            else:
                txt_veh = f"Vehículo {a.id_vehiculo}"

            etiqueta = f"{a.id_alquiler} - {txt_cli} - {txt_veh}"
            items.append(etiqueta)

        self.combo_alquiler["values"] = items

    # ----------------------------------------------------------
    def _cargar_incidentes_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, incidentes = IncidenteService.listar_incidentes()
        if not ok:
            messagebox.showerror("Error", incidentes)
            return

        for inc in incidentes:
            self.tree.insert(
                "",
                "end",
                iid=str(inc.id_incidente),
                values=(
                    inc.id_incidente,
                    inc.id_alquiler,
                    inc.tipo,
                    inc.descripcion,
                    inc.monto,
                    inc.estado,
                ),
            )

    # ----------------------------------------------------------
    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item_id = sel[0]
        valores = self.tree.item(item_id, "values")

        self._incidente_actual_id = int(valores[0])

        # Rellenar form (simple)
        id_alq = valores[1]
        for opt in self.combo_alquiler["values"]:
            if str(opt).startswith(f"{id_alq} - "):
                self.combo_alquiler.set(opt)
                break

        self.combo_tipo.set(valores[2])

        self.text_descripcion.delete("1.0", tk.END)
        self.text_descripcion.insert("1.0", valores[3])

        self.entry_monto.delete(0, tk.END)
        self.entry_monto.insert(0, str(valores[4]))

    # ----------------------------------------------------------
    def _validar_form(self):
        alquiler_sel = self.combo_alquiler.get().strip()
        tipo = self.combo_tipo.get().strip()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        monto_txt = self.entry_monto.get().strip()

        if not alquiler_sel:
            messagebox.showwarning("Validación", "Seleccioná un alquiler.")
            return None

        if not tipo:
            messagebox.showwarning("Validación", "Seleccioná un tipo de incidente.")
            return None

        if not descripcion:
            messagebox.showwarning("Validación", "La descripción no puede estar vacía.")
            return None

        if not monto_txt:
            messagebox.showwarning("Validación", "Ingresá un monto para el incidente.")
            return None

        try:
            monto = float(monto_txt)
        except ValueError:
            messagebox.showwarning("Validación", "El monto debe ser numérico.")
            return None

        if monto < 0:
            messagebox.showwarning("Validación", "El monto no puede ser negativo.")
            return None

        try:
            id_alquiler = int(alquiler_sel.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Validación", "No se pudo interpretar el alquiler seleccionado.")
            return None

        return {
            "id_alquiler": id_alquiler,
            "tipo": tipo,
            "descripcion": descripcion,
            "monto": monto,
        }

    # ----------------------------------------------------------
    def _guardar_incidente(self):
        datos = self._validar_form()
        if datos is None:
            return

        ok, r = IncidenteService.crear_incidente(
            datos["id_alquiler"],
            datos["tipo"],
            datos["descripcion"],
            datos["monto"],
        )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Incidente registrado correctamente.")
        self._limpiar_formulario()
        self._cargar_incidentes_en_tabla()

    # ----------------------------------------------------------
    def _marcar_pagado(self):
        if self._incidente_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un incidente de la tabla.")
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Marcar este incidente como PAGADO?"
        ):
            return

        ok, r = IncidenteService.marcar_incidente_como_pagado(self._incidente_actual_id)
        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Incidente marcado como pagado.")
        self._limpiar_formulario()
        self._cargar_incidentes_en_tabla()
