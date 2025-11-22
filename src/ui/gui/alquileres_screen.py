import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date

# pip install customtkinter tkcalendar
import customtkinter as ctk
from tkcalendar import DateEntry

from src.services.alquiler_service import AlquilerService
from src.repositories.vehiculo_repository import VehiculoRepository
from src.repositories.cliente_repository import ClienteRepository

class AlquileresScreen(ctk.CTkFrame):

    def __init__(self, parent, usuario_actual, on_back=None):
        super().__init__(parent)

        self.usuario_actual = usuario_actual
        self.on_back = on_back
        self._alquiler_actual_id = None

        # Configurar colores del Treeview para que no desentone
        self._configurar_estilos_treeview()
        
        self._construir_ui()
        self._cargar_clientes()
        self._cargar_vehiculos_disponibles()
        self._cargar_alquileres()

    def _configurar_estilos_treeview(self):
        """
        Ajusta los colores de la tabla estándar (ttk.Treeview) para que
        se vea bien en modo oscuro/moderno.
        """
        style = ttk.Style()
        style.theme_use("default") # Necesario para poder cambiar colores de fondo

        # Colores (Gris oscuro para fondo, blanco para texto, azul para selección)
        bg_color = "#2b2b2b"
        text_color = "white"
        selected_bg = "#1f538d"
        header_bg = "#3a3a3a"
        
        # Configuración del cuerpo de la tabla
        style.configure("Treeview",
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        borderwidth=0,
                        rowheight=25)
        
        style.map('Treeview', background=[('selected', selected_bg)])

        # Configuración de los encabezados
        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground="white",
                        relief="flat")
        
        style.map("Treeview.Heading",
                  background=[('active', '#565b5e')])

    def _construir_ui(self):
        # Configuración del grid principal
        self.grid_columnconfigure(0, weight=1) # Izquierda (Formulario) no se estira tanto
        self.grid_columnconfigure(1, weight=3) # Derecha (Tabla) se estira más
        self.grid_rowconfigure(1, weight=1)

        # --- HEADER ---
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(header, text="Gestión de Alquileres", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=100, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right")

        ctk.CTkLabel(header, text="Registrar y cerrar alquileres", 
                     text_color="gray").pack(side="left", padx=20, pady=(5,0))

        # --- BODY (Contenedor principal) ---
        # 1. FORMULARIO (Izquierda)
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Nuevo Alquiler", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        # Cliente
        ctk.CTkLabel(form_frame, text="Cliente:", anchor="w").pack(fill="x", padx=15, pady=(5, 0))
        self.combo_cliente = ctk.CTkComboBox(form_frame, width=250, state="readonly")
        self.combo_cliente.pack(padx=15, pady=5)

        # Vehículo
        ctk.CTkLabel(form_frame, text="Vehículo:", anchor="w").pack(fill="x", padx=15, pady=(10, 0))
        self.combo_vehiculo = ctk.CTkComboBox(form_frame, width=250, state="readonly")
        self.combo_vehiculo.pack(padx=15, pady=5)

        # Fechas (Usamos Frame interno para agrupar DateEntries)
        fechas_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fechas_frame.pack(padx=15, pady=10, fill="x")

        # Inicio
        ctk.CTkLabel(fechas_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky="w", padx=5)
        self.date_inicio = DateEntry(fechas_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
        self.date_inicio.grid(row=1, column=0, padx=5, pady=5)

        # Fin
        ctk.CTkLabel(fechas_frame, text="Fecha Fin:").grid(row=0, column=1, sticky="w", padx=5)
        self.date_fin = DateEntry(fechas_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
        self.date_fin.grid(row=1, column=1, padx=5, pady=5)
        self.date_inicio.set_date(date.today())
        self.date_fin.set_date(date.today())

        # Botón Registrar (Verde o Azul fuerte)
        ctk.CTkButton(form_frame, text="Registrar Alquiler", height=40,
                      fg_color="#2cc985", hover_color="#25a970", text_color="white",
                      font=ctk.CTkFont(weight="bold"),
                      command=self._registrar_alquiler).pack(padx=15, pady=20, fill="x")

        # 2. TABLA (Derecha)
        tabla_container = ctk.CTkFrame(self, corner_radius=10)
        tabla_container.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=10)
        tabla_container.grid_rowconfigure(0, weight=1)
        tabla_container.grid_columnconfigure(0, weight=1)

        # Estructura del Treeview (se mantiene ttk pero con estilo modificado)
        columnas = ("id", "cliente", "vehiculo", "inicio", "fin", "estado", "total")
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        headers = ["ID", "Cliente", "Vehículo", "Inicio", "Fin", "Estado", "Total $"]
        for col, texto in zip(columnas, headers):
            self.tree.heading(col, text=texto)

        # Anchos de columna
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("cliente", width=120)
        self.tree.column("vehiculo", width=120)
        self.tree.column("inicio", width=80, anchor="center")
        self.tree.column("fin", width=80, anchor="center")
        self.tree.column("estado", width=80, anchor="center")
        self.tree.column("total", width=80, anchor="e")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar vertical moderna
        scroll_y = ctk.CTkScrollbar(tabla_container, orientation="vertical", command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0,5))
        self.tree.configure(yscrollcommand=scroll_y.set)
        
        # Botón Cerrar Alquiler (Abajo de la tabla)
        ctk.CTkButton(tabla_container, text="Cerrar Alquiler Seleccionado", 
                      fg_color="#c0392b", hover_color="#a93226",
                      command=self._cerrar_alquiler).grid(row=1, column=0, columnspan=2, pady=15)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _cargar_clientes(self):
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

        # En CTkComboBox se usa configure(values=...)
        self.combo_cliente.configure(values=items)
        if items: self.combo_cliente.set("") # Limpiar selección inicial

    def _cargar_vehiculos_disponibles(self):
        vehiculos = VehiculoRepository.listar()
        disponibles = []
        for v in vehiculos:
            estado = getattr(v, "estado", "DISPONIBLE")
            if estado == "DISPONIBLE" and v.activo:
                disponibles.append(f"{v.id_vehiculo} - {v.patente} ({v.marca} {v.modelo})")

        self.combo_vehiculo.configure(values=disponibles)
        self.combo_vehiculo.set("")

    def _cargar_alquileres(self):
        # Limpiar tabla vieja
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, alquileres = AlquilerService.listar_alquileres()
        if not ok:
            return

        for a in alquileres:
            self.tree.insert("", "end", iid=str(a.id_alquiler),
                values=(a.id_alquiler, a.id_cliente, a.id_vehiculo,
                        a.fecha_inicio, a.fecha_fin, a.estado, a.total))

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

        try:
            id_cliente = int(cliente_sel.split(" - ")[0])
            id_vehiculo = int(vehiculo_sel.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Error al interpretar selección.")
            return

        id_empleado = self.usuario_actual.get("id_empleado")
        ok, r = AlquilerService.crear_alquiler(id_cliente, id_vehiculo, id_empleado, f_inicio, f_fin)

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Alquiler registrado correctamente.")
        self._cargar_vehiculos_disponibles()
        self._cargar_alquileres()

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        self._alquiler_actual_id = int(sel[0])

    def _cerrar_alquiler(self):
        if self._alquiler_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un alquiler.")
            return

        fecha_dev = date.today().isoformat()
        
        # CustomTkinter tiene CTkInputDialog, pero simpledialog de tk es más robusto para validaciones rápidas
        km_final_str = simpledialog.askstring("Cierre", "Kilometraje final:")
        if not km_final_str: return

        combustible_final_str = simpledialog.askstring("Cierre", "Combustible final (litros):")
        if not combustible_final_str: return

        monto_extra = simpledialog.askstring("Cierre", "Monto extra (opcional):") or "0"

        ok, r = AlquilerService.cerrar_alquiler(self._alquiler_actual_id, fecha_dev, km_final_str, combustible_final_str, monto_extra)

        if not ok:
            messagebox.showerror("Error", r)
            return

        try:
            if float(combustible_final_str) < 5:
                messagebox.showwarning("Aviso", "Vehículo con combustible bajo.")
        except: pass

        messagebox.showinfo("OK", "Alquiler cerrado correctamente.")
        self._cargar_alquileres()
        self._cargar_vehiculos_disponibles()