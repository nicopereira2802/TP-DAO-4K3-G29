import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from datetime import date

from tkcalendar import DateEntry  # asegurate: pip install tkcalendar

from src.services.alquiler_service import AlquilerService
from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.cliente_repository import ClienteRepository


class AlquileresScreen(ttk.Frame):

    def __init__(self, parent, usuario_actual, on_back=None):
        super().__init__(parent)

        self.usuario_actual = usuario_actual
        self.on_back = on_back

        self._alquiler_actual_id = None

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_clientes()
        self._cargar_vehiculos_disponibles()
        self._cargar_alquileres()

    # ----------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("AlqTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("AlqSubtitle.TLabel", font=("Segoe UI", 10), foreground="#555")

    # ----------------------------------------------------------
    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # HEADER
        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Gestión de Alquileres", style="AlqTitle.TLabel") \
            .grid(row=0, column=0, sticky="w")

        ttk.Label(header, text="Registrar y cerrar alquileres", style="AlqSubtitle.TLabel") \
            .grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        # BODY
        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)

        # FORMULARIO
        form = ttk.LabelFrame(body, text="Registrar alquiler", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        # CLIENTE: combobox de clientes activos
        ttk.Label(form, text="Cliente (DNI - Nombre):") \
            .grid(row=0, column=0, sticky="w")
        self.combo_cliente = ttk.Combobox(form, state="readonly", width=35)
        self.combo_cliente.grid(row=1, column=0, sticky="w", pady=5)

        # Vehículo disponible
        ttk.Label(form, text="Vehículo (disponibles):") \
            .grid(row=2, column=0, sticky="w")

        self.combo_vehiculo = ttk.Combobox(form, state="readonly", width=35)
        self.combo_vehiculo.grid(row=3, column=0, sticky="w", pady=5)

        # Fechas con calendario (solo selección, sin escribir)
        ttk.Label(form, text="Fecha inicio:") \
            .grid(row=4, column=0, sticky="w")
        self.date_inicio = DateEntry(
            form,
            width=20,
            date_pattern="yyyy-mm-dd",
            state="readonly"
        )
        self.date_inicio.set_date(date.today())
        self.date_inicio.grid(row=5, column=0, sticky="w", pady=2)

        ttk.Label(form, text="Fecha fin:") \
            .grid(row=6, column=0, sticky="w")
        self.date_fin = DateEntry(
            form,
            width=20,
            date_pattern="yyyy-mm-dd",
            state="readonly"
        )
        self.date_fin.set_date(date.today())
        self.date_fin.grid(row=7, column=0, sticky="w", pady=2)

        # Botón crear alquiler
        ttk.Button(form, text="Registrar alquiler", command=self._registrar_alquiler) \
            .grid(row=8, column=0, sticky="w", pady=10)

        # TABLA DE ALQUILERES
        tabla_frame = ttk.LabelFrame(body, text="Alquileres", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("id", "cliente", "vehiculo", "inicio", "fin", "estado", "total")
        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=15,
            selectmode="browse"
        )

        headers = ["ID", "Cliente", "Vehículo", "Inicio", "Fin", "Estado", "Total $"]
        for col, texto in zip(columnas, headers):
            self.tree.heading(col, text=texto)

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("cliente", width=100)
        self.tree.column("vehiculo", width=100)
        self.tree.column("inicio", width=90)
        self.tree.column("fin", width=90)
        self.tree.column("estado", width=80)
        self.tree.column("total", width=80, anchor="e")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll_y.set)

        # Botón cerrar alquiler
        ttk.Button(tabla_frame, text="Cerrar alquiler", command=self._cerrar_alquiler) \
            .grid(row=1, column=0, sticky="w", pady=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ----------------------------------------------------------
    def _cargar_clientes(self):
        """
        Llena el combo con todos los clientes activos.
        Formato: "id - DNI - Nombre Apellido"
        """
        try:
            clientes = ClienteRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes.\n{e}")
            clientes = []

        items = []
        for c in clientes:
            if not getattr(c, "activo", True):
                continue

            cid = getattr(c, "id", None)
            dni = getattr(c, "dni", "")
            nombre = getattr(c, "nombre", "")
            apellido = getattr(c, "apellido", "")
            etiqueta = f"{cid} - {dni} - {nombre} {apellido}".strip()
            items.append(etiqueta)

        self.combo_cliente["values"] = items

    # ----------------------------------------------------------
    def _cargar_vehiculos_disponibles(self):
        vehiculos = VehiculoRepository.listar()

        disponibles = []
        for v in vehiculos:
            estado = getattr(v, "estado", "DISPONIBLE")
            if estado == "DISPONIBLE" and v.activo:
                disponibles.append(
                    f"{v.id_vehiculo} - {v.patente} ({v.marca} {v.modelo})"
                )

        self.combo_vehiculo["values"] = disponibles

    # ----------------------------------------------------------
    def _cargar_alquileres(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, alquileres = AlquilerService.listar_alquileres()
        if not ok:
            return

        for a in alquileres:
            self.tree.insert(
                "",
                "end",
                iid=str(a.id_alquiler),
                values=(
                    a.id_alquiler,
                    a.id_cliente,
                    a.id_vehiculo,
                    a.fecha_inicio,
                    a.fecha_fin,
                    a.estado,
                    a.total
                )
            )

    # ----------------------------------------------------------
    def _registrar_alquiler(self):
        cliente_sel = self.combo_cliente.get().strip()
        vehiculo_sel = self.combo_vehiculo.get().strip()

        f_inicio = self.date_inicio.get_date().isoformat()
        f_fin = self.date_fin.get_date().isoformat()

        if not cliente_sel:
            messagebox.showwarning("Validación", "Seleccioná un cliente.")
            return

        if not vehiculo_sel:
            messagebox.showwarning("Validación", "Seleccioná un vehículo.")
            return

        # obtener ID cliente
        try:
            id_cliente = int(cliente_sel.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Error al interpretar el cliente seleccionado.")
            return

        # obtener ID vehículo
        try:
            id_vehiculo = int(vehiculo_sel.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Error al interpretar el vehículo seleccionado.")
            return

        id_empleado = self.usuario_actual.get("id_empleado")

        ok, r = AlquilerService.crear_alquiler(
            id_cliente,
            id_vehiculo,
            id_empleado,
            f_inicio,
            f_fin
        )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Alquiler registrado correctamente.")

        self._cargar_vehiculos_disponibles()
        self._cargar_alquileres()

    # ----------------------------------------------------------
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        self._alquiler_actual_id = int(sel[0])

    # ----------------------------------------------------------
    def _cerrar_alquiler(self):
        if self._alquiler_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un alquiler.")
            return

        # Fecha de devolución = HOY automáticamente
        fecha_dev = date.today().isoformat()

        # Solo pedir monto extra opcional
        monto_extra = simpledialog.askstring("Extra", "Monto extra (opcional):")
        if not monto_extra:
            monto_extra = "0"

        ok, r = AlquilerService.cerrar_alquiler(
            self._alquiler_actual_id,
            fecha_dev,
            monto_extra
        )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Alquiler cerrado correctamente.")

        self._cargar_alquileres()
        self._cargar_vehiculos_disponibles()
