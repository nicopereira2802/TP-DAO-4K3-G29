import tkinter as tk
from tkinter import ttk, messagebox
from src.services.vehiculo_service import VehiculoService

# Combobox de marcas predefinidas
MARCAS = [
    "Peugeot",
    "Renault",
    "Ford",
    "Volkswagen",
    "Chevrolet",
    "Fiat",
    "Toyota",
    "Honda",
    "Nissan",
]


class VehiculosScreen(ttk.Frame):
    """
    Pantalla de gestión de vehículos.
    Estilo igual a Clientes.
    """

    def __init__(self, parent, usuario_actual, on_back=None):
        super().__init__(parent)

        self.usuario_actual = usuario_actual
        self.on_back = on_back

        self._vehiculo_actual_id = None

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_tabla()

    # ---------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("VehiculosTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure(
            "VehiculosSubtitle.TLabel",
            font=("Segoe UI", 10),
            foreground="#555555"
        )

    # ---------------------------------------------------------
    def _validar_precio(self, valor):
        """Solo permite números positivos."""
        if valor == "":
            return True
        return valor.isdigit()

    def _validar_float(self, valor):
        """Permitir solo números reales positivos."""
        if valor == "":
            return True
        try:
            float(valor)
            return True
        except:
            return False

    # ---------------------------------------------------------
    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # ---- HEADER ----
        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Gestión de vehículos",
                  style="VehiculosTitle.TLabel").grid(row=0, column=0, sticky="w")

        ttk.Label(header, text="Alta, modificación y baja lógica de vehículos.",
                  style="VehiculosSubtitle.TLabel").grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        # ---- BODY ----
        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        # FORM
        form = ttk.LabelFrame(body, text="Datos del vehículo", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        self._crear_formulario(form)

        # TABLA
        tabla_frame = ttk.LabelFrame(body, text="Listado de vehículos", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        self._crear_tabla(tabla_frame)

    # ---------------------------------------------------------
    def _crear_formulario(self, form):

        # PATENTE
        ttk.Label(form, text="Patente:").grid(row=0, column=0, sticky="w")
        self.entry_patente = ttk.Entry(form, width=20)
        self.entry_patente.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # MARCA
        ttk.Label(form, text="Marca:").grid(row=2, column=0, sticky="w")
        self.combo_marca = ttk.Combobox(
            form, values=MARCAS, state="readonly", width=18
        )
        self.combo_marca.grid(row=3, column=0, sticky="w", pady=(0, 8))

        # MODELO
        ttk.Label(form, text="Modelo:").grid(row=4, column=0, sticky="w")
        self.entry_modelo = ttk.Entry(form, width=20)
        self.entry_modelo.grid(row=5, column=0, sticky="w", pady=(0, 8))

        # AÑO
        ttk.Label(form, text="Año:").grid(row=6, column=0, sticky="w")
        self.combo_anio = ttk.Combobox(
            form,
            values=[str(a) for a in range(2000, 2026)],
            state="readonly",
            width=18
        )
        self.combo_anio.grid(row=7, column=0, sticky="w", pady=(0, 8))

        # TIPO
        ttk.Label(form, text="Tipo:").grid(row=8, column=0, sticky="w")
        self.combo_tipo = ttk.Combobox(
            form,
            values=["auto", "camioneta", "moto"],
            state="readonly",
            width=18
        )
        self.combo_tipo.grid(row=9, column=0, sticky="w", pady=(0, 8))

        # PRECIO POR DIA
        ttk.Label(form, text="Precio por día:").grid(row=10, column=0, sticky="w")
        vcmd_precio = (self.register(self._validar_precio), "%P")
        self.entry_precio = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_precio
        )
        self.entry_precio.grid(row=11, column=0, sticky="w", pady=(0, 8))

        # KM ACTUAL
        ttk.Label(form, text="KM actual:").grid(row=12, column=0, sticky="w")
        vcmd_km = (self.register(self._validar_float), "%P")
        self.entry_km = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_km
        )
        self.entry_km.grid(row=13, column=0, sticky="w", pady=(0, 8))

        # COMBUSTIBLE ACTUAL
        ttk.Label(form, text="Combustible actual (L):").grid(row=14, column=0, sticky="w")
        vcmd_comb = (self.register(self._validar_float), "%P")
        self.entry_comb = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_comb
        )
        self.entry_comb.grid(row=15, column=0, sticky="w", pady=(0, 8))

        # ACTIVO
        self.var_activo = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            form, text="Vehículo activo", variable=self.var_activo
        ).grid(row=16, column=0, sticky="w", pady=(5, 10))

        # BOTONES
        btns = ttk.Frame(form)
        btns.grid(row=17, column=0, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Guardar", command=self._guardar)\
            .grid(row=0, column=0, padx=(0, 5))

        ttk.Button(btns, text="Desactivar", command=self._desactivar)\
            .grid(row=0, column=1, padx=5)

    # ---------------------------------------------------------
    def _crear_tabla(self, tabla_frame):
        columnas = (
            "id", "patente", "marca", "modelo", "anio",
            "tipo", "precio", "km", "comb", "alerta", "activo"
        )

        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=15,
        )

        # HEADERS
        self.tree.heading("id", text="ID")
        self.tree.heading("patente", text="Patente")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("modelo", text="Modelo")
        self.tree.heading("anio", text="Año")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("precio", text="Precio $/día")
        self.tree.heading("km", text="KM")
        self.tree.heading("comb", text="Comb (L)")
        self.tree.heading("alerta", text="Alerta")
        self.tree.heading("activo", text="Activo")

        # COLUMNAS
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("patente", width=90)
        self.tree.column("marca", width=120)
        self.tree.column("modelo", width=120)
        self.tree.column("anio", width=60, anchor="center")
        self.tree.column("tipo", width=80)
        self.tree.column("precio", width=100, anchor="e")
        self.tree.column("km", width=80, anchor="e")
        self.tree.column("comb", width=80, anchor="e")
        self.tree.column("alerta", width=80, anchor="center")
        self.tree.column("activo", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            tabla_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ---------------------------------------------------------
    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        valores = self.tree.item(item, "values")

        self._vehiculo_actual_id = int(valores[0])

        self.entry_patente.delete(0, tk.END)
        self.entry_patente.insert(0, valores[1])

        self.combo_marca.set(valores[2])

        self.entry_modelo.delete(0, tk.END)
        self.entry_modelo.insert(0, valores[3])

        self.combo_anio.set(valores[4])
        self.combo_tipo.set(valores[5])

        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, valores[6])

        # KM y combustible
        self.entry_km.delete(0, tk.END)
        self.entry_km.insert(0, valores[7])

        self.entry_comb.delete(0, tk.END)
        self.entry_comb.insert(0, valores[8])

        self.var_activo.set(valores[10] == "Sí")

    # ---------------------------------------------------------
    def _limpiar_formulario(self):
        self._vehiculo_actual_id = None

        self.entry_patente.delete(0, tk.END)
        self.combo_marca.set("")
        self.entry_modelo.delete(0, tk.END)
        self.combo_anio.set("")
        self.combo_tipo.set("")
        self.entry_precio.delete(0, tk.END)

        self.entry_km.delete(0, tk.END)
        self.entry_comb.delete(0, tk.END)

        self.var_activo.set(True)

        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    # ---------------------------------------------------------
    def _guardar(self):
        patente = self.entry_patente.get()
        marca = self.combo_marca.get()
        modelo = self.entry_modelo.get()
        anio = self.combo_anio.get()
        tipo = self.combo_tipo.get()
        precio = self.entry_precio.get()
        km = self.entry_km.get()
        combustible = self.entry_comb.get()

        if self._vehiculo_actual_id is None:
            ok, r = VehiculoService.crear_vehiculo(
                self.usuario_actual,
                patente,
                marca,
                modelo,
                anio,
                tipo,
                precio,
                km,
                combustible
            )
        else:
            ok, r = VehiculoService.actualizar_vehiculo(
                self._vehiculo_actual_id,
                patente,
                marca,
                modelo,
                anio,
                tipo,
                precio,
                km,
                combustible
            )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Vehículo guardado correctamente.")
        self._limpiar_formulario()
        self._cargar_tabla()

    # ---------------------------------------------------------
    def _desactivar(self):
        if self._vehiculo_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un vehículo.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desactivar vehículo?"):
            return

        ok, r = VehiculoService.inactivar_vehiculo(self._vehiculo_actual_id)

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Vehículo desactivado.")
        self._limpiar_formulario()
        self._cargar_tabla()

    # ---------------------------------------------------------
    def _cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, vehiculos = VehiculoService.listar_vehiculos()
        if not ok:
            return

        for v in vehiculos:
            alerta = "⚠ Bajo" if v.combustible_actual < 5 else ""

            self.tree.insert(
                "",
                "end",
                iid=str(v.id_vehiculo),
                values=(
                    v.id_vehiculo,
                    v.patente,
                    v.marca,
                    v.modelo,
                    v.anio,
                    v.tipo,
                    v.precio_por_dia,
                    v.km_actual,
                    v.combustible_actual,
                    alerta,
                    "Sí" if v.activo else "No",
                )
            )
