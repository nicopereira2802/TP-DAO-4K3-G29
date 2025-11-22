import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

# pip install customtkinter tkcalendar
import customtkinter as ctk
from tkcalendar import DateEntry

from src.services.mantenimiento_service import MantenimientoService
from src.repositories.vehiculo_repository import VehiculoRepository


class MantenimientosScreen(ctk.CTkFrame):
    """
    Pantalla de gestión de mantenimientos (Versión Moderna).
    """

    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._mantenimiento_actual_id = None

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_vehiculos_para_combo()
        self._cargar_mantenimientos_en_tabla()

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
        
        ctk.CTkLabel(title_frame, text="Mantenimiento de Flota", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Registro de reparaciones y servicios", 
                     text_color="gray").pack(anchor="w")

        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=80, height=30, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right", anchor="center")

        # --- BODY (Split View) ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # 1. PANEL IZQUIERDO: FORMULARIO
        form_frame = ctk.CTkFrame(body, width=320, corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_frame.grid_propagate(False)

        ctk.CTkLabel(form_frame, text="Nuevo Mantenimiento", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        # Vehículo
        ctk.CTkLabel(form_frame, text="Vehículo:", anchor="w").pack(fill="x", padx=15, pady=(5,0))
        self.combo_vehiculo = ctk.CTkComboBox(form_frame, state="readonly", width=280)
        self.combo_vehiculo.set("Seleccionar Vehículo")
        self.combo_vehiculo.pack(fill="x", padx=15, pady=5)

        # Fechas (En una fila horizontal)
        dates_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        dates_frame.pack(fill="x", padx=15, pady=10)
        
        # Inicio
        ctk.CTkLabel(dates_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky="w")
        self.date_inicio = DateEntry(dates_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_inicio.grid(row=1, column=0, sticky="w", pady=2)
        
        # Fin
        ctk.CTkLabel(dates_frame, text="Fecha Fin:").grid(row=0, column=1, sticky="w", padx=(10,0))
        self.date_fin = DateEntry(dates_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_fin.grid(row=1, column=1, sticky="w", pady=2, padx=(10,0))
        
        self.date_inicio.set_date(date.today())
        self.date_fin.set_date(date.today())

        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción del servicio:", anchor="w").pack(fill="x", padx=15, pady=(10,0))
        self.text_descripcion = ctk.CTkTextbox(form_frame, height=120, corner_radius=5)
        self.text_descripcion.pack(fill="x", padx=15, pady=5)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(btn_frame, text="Guardar", fg_color="#2cc985", hover_color="#25a970", 
                      font=ctk.CTkFont(weight="bold"),
                      command=self._guardar_mantenimiento).pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#c0392b", hover_color="#a93226", 
                      command=self._eliminar_mantenimiento).pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Limpiar", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=self._limpiar_formulario).pack(fill="x", pady=5)

        # 2. PANEL DERECHO: TABLA
        tabla_container = ctk.CTkFrame(body, corner_radius=10)
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        columnas = ("id", "vehiculo", "inicio", "fin", "descripcion")
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        headers = {"id": "ID", "vehiculo": "Vehículo", "inicio": "Inicio", "fin": "Fin", "descripcion": "Descripción"}
        for col, txt in headers.items():
            self.tree.heading(col, text=txt)

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("vehiculo", width=150)
        self.tree.column("inicio", width=90, anchor="center")
        self.tree.column("fin", width=90, anchor="center")
        self.tree.column("descripcion", width=200)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        scroll_y = ctk.CTkScrollbar(tabla_container, command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 5))
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _limpiar_formulario(self):
        self._mantenimiento_actual_id = None
        self.combo_vehiculo.set("Seleccionar Vehículo")
        self.date_inicio.set_date(date.today())
        self.date_fin.set_date(date.today())
        self.text_descripcion.delete("1.0", "end")
        
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def _cargar_vehiculos_para_combo(self):
        try:
            vehiculos = VehiculoRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar vehículos.\n{e}")
            vehiculos = []

        items = []
        for v in vehiculos:
            if not v.activo: continue
            # Formato: ID - Patente (Marca Modelo)
            etiqueta = f"{v.id_vehiculo} - {v.patente} ({v.marca} {v.modelo})"
            items.append(etiqueta)

        self.combo_vehiculo.configure(values=items)

    def _cargar_mantenimientos_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, mantenimientos = MantenimientoService.listar_mantenimientos()
        if not ok:
            messagebox.showerror("Error", mantenimientos)
            return

        for m in mantenimientos:
            vehiculo = VehiculoRepository.obtener_por_id(m.id_vehiculo)
            txt_veh = f"{vehiculo.patente} ({vehiculo.marca})" if vehiculo else f"ID {m.id_vehiculo}"

            self.tree.insert("", "end", iid=str(m.id_mantenimiento), values=(
                m.id_mantenimiento, txt_veh, m.fecha_inicio, m.fecha_fin, m.descripcion
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return

        item_id = sel[0]
        valores = self.tree.item(item_id, "values")
        self._mantenimiento_actual_id = int(valores[0])

        # Buscar el vehículo en el combo
        vehiculo_txt = valores[1]
        for opt in self.combo_vehiculo._values:
            if vehiculo_txt in opt: # Coincidencia parcial (Patente)
                self.combo_vehiculo.set(opt)
                break

        # Fechas
        try:
            self.date_inicio.set_date(valores[2])
            self.date_fin.set_date(valores[3])
        except: pass

        # Descripción
        self.text_descripcion.delete("1.0", "end")
        self.text_descripcion.insert("1.0", valores[4])

    def _guardar_mantenimiento(self):
        veh_sel = self.combo_vehiculo.get().strip()
        if "Seleccionar" in veh_sel or not veh_sel:
            messagebox.showwarning("Validación", "Seleccioná un vehículo.")
            return

        try:
            id_vehiculo = int(veh_sel.split(" - ")[0])
        except:
            messagebox.showwarning("Validación", "Error en selección de vehículo.")
            return

        f_inicio = self.date_inicio.get_date().isoformat()
        f_fin = self.date_fin.get_date().isoformat()
        descripcion = self.text_descripcion.get("1.0", "end").strip()

        if not descripcion:
            messagebox.showwarning("Validación", "Descripción requerida.")
            return

        ok, r = MantenimientoService.crear_mantenimiento(id_vehiculo, f_inicio, f_fin, descripcion)

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Mantenimiento registrado.")
        self._limpiar_formulario()
        self._cargar_mantenimientos_en_tabla()

    def _eliminar_mantenimiento(self):
        if self._mantenimiento_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un mantenimiento.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este mantenimiento?"): return

        ok, r = MantenimientoService.eliminar_mantenimiento(self._mantenimiento_actual_id)
        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", r)
        self._limpiar_formulario()
        self._cargar_mantenimientos_en_tabla()