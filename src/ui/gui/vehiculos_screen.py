import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from src.services.vehiculo_service import VehiculoService

# Listas para los Combobox
MARCAS = [
    "Peugeot", "Renault", "Ford", "Volkswagen", "Chevrolet", 
    "Fiat", "Toyota", "Honda", "Nissan", "BMW", "Mercedes-Benz"
]

ANOS = [str(a) for a in range(2000, 2026)]
TIPOS = ["auto", "camioneta", "moto"]

class VehiculosScreen(ctk.CTkFrame):
    """
    Pantalla de gestión de vehículos (Versión Modernizada).
    """

    def __init__(self, parent, usuario_actual, on_back=None):
        super().__init__(parent)

        self.usuario_actual = usuario_actual
        self.on_back = on_back
        self._vehiculo_actual_id = None

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_tabla()

    def _configurar_estilos_treeview(self):
        """Aplica estilo oscuro a la tabla estándar de Tkinter."""
        style = ttk.Style()
        style.theme_use("default")
        
        # Colores para modo oscuro
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
        # Layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Gestión de Flota", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Alta, modificación y control de vehículos", 
                     text_color="gray").pack(anchor="w")

        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=80, height=30, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right", anchor="center")

        # --- BODY (Split View) ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Grid interno del cuerpo: Izq (Form) fijo, Der (Tabla) flexible
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # 1. PANEL IZQUIERDO: FORMULARIO (Scrollable por si hay muchos campos)
        form_frame = ctk.CTkFrame(body, width=320, corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_frame.grid_propagate(False) # Mantiene el ancho fijo

        # Contenido del formulario
        ctk.CTkLabel(form_frame, text="Datos del Vehículo", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))

        # Scrollable interno para los campos si la pantalla es chica
        scroll_form = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        scroll_form.pack(fill="both", expand=True, padx=5, pady=5)

        self.entry_patente = ctk.CTkEntry(scroll_form, placeholder_text="Patente (Ej: AA123BB)")
        self.entry_patente.pack(fill="x", padx=5, pady=5)

        self.combo_marca = ctk.CTkComboBox(scroll_form, values=MARCAS)
        self.combo_marca.set("Seleccionar Marca") # Placeholder
        self.combo_marca.pack(fill="x", padx=5, pady=5)

        self.entry_modelo = ctk.CTkEntry(scroll_form, placeholder_text="Modelo")
        self.entry_modelo.pack(fill="x", padx=5, pady=5)

        self.combo_anio = ctk.CTkComboBox(scroll_form, values=ANOS)
        self.combo_anio.set("Año")
        self.combo_anio.pack(fill="x", padx=5, pady=5)

        self.combo_tipo = ctk.CTkComboBox(scroll_form, values=TIPOS)
        self.combo_tipo.set("Tipo de Vehículo")
        self.combo_tipo.pack(fill="x", padx=5, pady=5)

        self.entry_precio = ctk.CTkEntry(scroll_form, placeholder_text="Precio por día ($)")
        self.entry_precio.pack(fill="x", padx=5, pady=5)

        self.entry_km = ctk.CTkEntry(scroll_form, placeholder_text="Kilometraje Actual")
        self.entry_km.pack(fill="x", padx=5, pady=5)

        self.entry_comb = ctk.CTkEntry(scroll_form, placeholder_text="Combustible (Litros)")
        self.entry_comb.pack(fill="x", padx=5, pady=5)

        self.var_activo = tk.BooleanVar(value=True)
        self.chk_activo = ctk.CTkCheckBox(scroll_form, text="Vehículo Activo", variable=self.var_activo)
        self.chk_activo.pack(fill="x", padx=5, pady=15)

        # Botones fijos al pie del formulario (fuera del scroll)
        btns_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btns_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(btns_frame, text="Guardar", fg_color="#2cc985", hover_color="#25a970", 
                      font=ctk.CTkFont(weight="bold"),
                      command=self._guardar).pack(fill="x", pady=5)
        
        ctk.CTkButton(btns_frame, text="Desactivar", fg_color="#c0392b", hover_color="#a93226", 
                      command=self._desactivar).pack(fill="x", pady=5)
        
        ctk.CTkButton(btns_frame, text="Limpiar", fg_color="transparent", border_width=1, 
                      text_color=("gray10", "gray90"),
                      command=self._limpiar_formulario).pack(fill="x", pady=5)

        # 2. PANEL DERECHO: TABLA
        tabla_container = ctk.CTkFrame(body, corner_radius=10)
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        # Columnas
        columnas = (
            "id", "patente", "marca", "modelo", "anio",
            "tipo", "precio", "km", "comb", "alerta", "activo"
        )
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        # Encabezados
        headers = {
            "id": "ID", "patente": "Patente", "marca": "Marca", "modelo": "Modelo",
            "anio": "Año", "tipo": "Tipo", "precio": "$/día", "km": "KM",
            "comb": "Lts", "alerta": "Estado", "activo": "Activo"
        }
        
        for col_id, text in headers.items():
            self.tree.heading(col_id, text=text)

        # Anchos
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("patente", width=90, anchor="center")
        self.tree.column("marca", width=100)
        self.tree.column("modelo", width=100)
        self.tree.column("anio", width=60, anchor="center")
        self.tree.column("tipo", width=80)
        self.tree.column("precio", width=90, anchor="e")
        self.tree.column("km", width=80, anchor="e")
        self.tree.column("comb", width=60, anchor="e")
        self.tree.column("alerta", width=80, anchor="center") # Para alertas de combustible
        self.tree.column("activo", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar
        scroll_y = ctk.CTkScrollbar(tabla_container, command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 5))
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ---------------------------------------------------------
    # LÓGICA INTERNA
    # ---------------------------------------------------------

    def _limpiar_formulario(self):
        self._vehiculo_actual_id = None
        
        self.entry_patente.delete(0, "end")
        self.entry_modelo.delete(0, "end")
        self.entry_precio.delete(0, "end")
        self.entry_km.delete(0, "end")
        self.entry_comb.delete(0, "end")
        
        # Resetear combos a placeholders
        self.combo_marca.set("Seleccionar Marca")
        self.combo_anio.set("Año")
        self.combo_tipo.set("Tipo de Vehículo")
        
        self.var_activo.set(True)
        
        # Quitar selección de tabla
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def _cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, vehiculos = VehiculoService.listar_vehiculos()
        if not ok: return

        for v in vehiculos:
            # Alerta visual simple
            alerta = "⚠ Bajo" if v.combustible_actual < 5 else "OK"
            if v.estado == "MANTENIMIENTO": alerta = "🔧 Taller"
            elif v.estado == "ALQUILADO": alerta = "🚗 En uso"

            self.tree.insert("", "end", iid=str(v.id_vehiculo), values=(
                v.id_vehiculo, v.patente, v.marca, v.modelo, v.anio,
                v.tipo, f"{v.precio_por_dia:.2f}", f"{v.km_actual:.0f}", 
                f"{v.combustible_actual:.1f}", alerta,
                "Sí" if v.activo else "No"
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return

        item = sel[0]
        valores = self.tree.item(item, "values")
        self._vehiculo_actual_id = int(valores[0])

        # Rellenar campos
        self.entry_patente.delete(0, "end"); self.entry_patente.insert(0, valores[1])
        self.combo_marca.set(valores[2])
        self.entry_modelo.delete(0, "end"); self.entry_modelo.insert(0, valores[3])
        self.combo_anio.set(valores[4])
        self.combo_tipo.set(valores[5])
        self.entry_precio.delete(0, "end"); self.entry_precio.insert(0, valores[6])
        self.entry_km.delete(0, "end"); self.entry_km.insert(0, valores[7])
        self.entry_comb.delete(0, "end"); self.entry_comb.insert(0, valores[8])
        
        self.var_activo.set(valores[10] == "Sí")

    def _guardar(self):
        # Obtener valores
        patente = self.entry_patente.get()
        marca = self.combo_marca.get()
        modelo = self.entry_modelo.get()
        anio = self.combo_anio.get()
        tipo = self.combo_tipo.get()
        precio = self.entry_precio.get()
        km = self.entry_km.get()
        comb = self.entry_comb.get()

        # Validaciones básicas de UI (Service hace las fuertes)
        if marca == "Seleccionar Marca" or tipo == "Tipo de Vehículo":
            messagebox.showwarning("Validación", "Seleccione marca y tipo.")
            return

        if self._vehiculo_actual_id is None:
            ok, r = VehiculoService.crear_vehiculo(
                self.usuario_actual, patente, marca, modelo, anio, tipo, precio, km, comb
            )
        else:
            ok, r = VehiculoService.actualizar_vehiculo(
                self._vehiculo_actual_id, patente, marca, modelo, anio, tipo, precio, km, comb
            )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Vehículo guardado correctamente.")
        self._limpiar_formulario()
        self._cargar_tabla()

    def _desactivar(self):
        if self._vehiculo_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un vehículo.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desactivar vehículo?"): return

        ok, r = VehiculoService.inactivar_vehiculo(self._vehiculo_actual_id)
        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Vehículo desactivado.")
        self._limpiar_formulario()
        self._cargar_tabla()