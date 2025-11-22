import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from src.services.incidente_service import IncidenteService
from src.repositories.alquiler_repository import AlquilerRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.vehiculo_repository import VehiculoRepository


class IncidentesScreen(ctk.CTkFrame):
    """
    Pantalla de gestión de incidentes (Versión Moderna).
    """

    TIPOS_VALIDOS = ["MULTA", "DANO", "OTRO"]

    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back

        self._incidente_actual_id = None

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_alquileres_para_combo()
        self._cargar_incidentes_en_tabla()

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
        
        ctk.CTkLabel(title_frame, text="Gestión de Incidentes", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Registro de multas y daños", 
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

        ctk.CTkLabel(form_frame, text="Nuevo Incidente", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        # Alquiler
        ctk.CTkLabel(form_frame, text="Alquiler Asociado:", anchor="w").pack(fill="x", padx=15, pady=(5,0))
        self.combo_alquiler = ctk.CTkComboBox(form_frame, state="readonly", width=280)
        self.combo_alquiler.set("Seleccionar Alquiler")
        self.combo_alquiler.pack(fill="x", padx=15, pady=5)

        # Tipo
        ctk.CTkLabel(form_frame, text="Tipo:", anchor="w").pack(fill="x", padx=15, pady=(10,0))
        self.combo_tipo = ctk.CTkComboBox(form_frame, values=self.TIPOS_VALIDOS, state="readonly")
        self.combo_tipo.set("Seleccionar Tipo")
        self.combo_tipo.pack(fill="x", padx=15, pady=5)

        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción:", anchor="w").pack(fill="x", padx=15, pady=(10,0))
        self.text_descripcion = ctk.CTkTextbox(form_frame, height=100, corner_radius=5)
        self.text_descripcion.pack(fill="x", padx=15, pady=5)

        # Monto
        ctk.CTkLabel(form_frame, text="Monto ($):", anchor="w").pack(fill="x", padx=15, pady=(10,0))
        self.entry_monto = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.entry_monto.pack(fill="x", padx=15, pady=5)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(btn_frame, text="Guardar Incidente", fg_color="#2cc985", hover_color="#25a970", 
                      font=ctk.CTkFont(weight="bold"),
                      command=self._guardar_incidente).pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Marcar como PAGADO", fg_color="#3A7AFE", hover_color="#2c5dcf", 
                      command=self._marcar_pagado).pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Limpiar", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=self._limpiar_formulario).pack(fill="x", pady=5)

        # 2. PANEL DERECHO: TABLA
        tabla_container = ctk.CTkFrame(body, corner_radius=10)
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        columnas = ("id", "alquiler", "tipo", "descripcion", "monto", "estado")
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        headers = {"id": "ID", "alquiler": "Alquiler ID", "tipo": "Tipo", 
                   "descripcion": "Descripción", "monto": "Monto $", "estado": "Estado"}
        
        for col, txt in headers.items():
            self.tree.heading(col, text=txt)

        # Anchos
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("alquiler", width=80, anchor="center")
        self.tree.column("tipo", width=80, anchor="center")
        self.tree.column("descripcion", width=200)
        self.tree.column("monto", width=80, anchor="e")
        self.tree.column("estado", width=80, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        scroll_y = ctk.CTkScrollbar(tabla_container, command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 5))
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ----------------------------------------------------------
    # LÓGICA
    # ----------------------------------------------------------

    def _validar_monto(self, valor: str) -> bool:
        if valor == "": return True
        try:
            v = float(valor)
            return v >= 0
        except ValueError:
            return False

    def _limpiar_formulario(self):
        self._incidente_actual_id = None
        self.combo_alquiler.set("Seleccionar Alquiler")
        self.combo_tipo.set("Seleccionar Tipo")
        
        # CTkTextbox usa "0.0" o "1.0" hasta "end"
        self.text_descripcion.delete("1.0", "end")
        self.entry_monto.delete(0, "end")
        
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def _cargar_alquileres_para_combo(self):
        try:
            alquileres = AlquilerRepository.listar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar alquileres.\n{e}")
            alquileres = []

        items = []
        for a in alquileres:
            cliente = ClienteRepository.obtener_por_id(a.id_cliente)
            txt_cli = f"{getattr(cliente, 'dni', '')} {getattr(cliente, 'apellido', '')}" if cliente else "?"
            
            vehiculo = VehiculoRepository.obtener_por_id(a.id_vehiculo)
            txt_veh = f"{getattr(vehiculo, 'patente', '')}" if vehiculo else "?"

            # Formato para combo
            etiqueta = f"{a.id_alquiler} - {txt_cli} - {txt_veh}"
            items.append(etiqueta)

        self.combo_alquiler.configure(values=items)

    def _cargar_incidentes_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, incidentes = IncidenteService.listar_incidentes()
        if not ok: return

        for inc in incidentes:
            self.tree.insert("", "end", iid=str(inc.id_incidente), values=(
                inc.id_incidente, inc.id_alquiler, inc.tipo, 
                inc.descripcion, f"{inc.monto:.2f}", inc.estado
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return

        item_id = sel[0]
        valores = self.tree.item(item_id, "values")
        self._incidente_actual_id = int(valores[0])

        # Rellenar form
        id_alq = valores[1]
        # Buscar coincidencia en el combo (CTK combo values es una lista)
        for opt in self.combo_alquiler._values: 
            if str(opt).startswith(f"{id_alq} - "):
                self.combo_alquiler.set(opt)
                break

        self.combo_tipo.set(valores[2])
        
        self.text_descripcion.delete("1.0", "end")
        self.text_descripcion.insert("1.0", valores[3])
        
        self.entry_monto.delete(0, "end")
        self.entry_monto.insert(0, valores[4])

    def _validar_form(self):
        alquiler_sel = self.combo_alquiler.get().strip()
        tipo = self.combo_tipo.get().strip()
        descripcion = self.text_descripcion.get("1.0", "end").strip()
        monto_txt = self.entry_monto.get().strip()

        if "Seleccionar" in alquiler_sel or not alquiler_sel:
            messagebox.showwarning("Validación", "Seleccioná un alquiler.")
            return None
        if "Seleccionar" in tipo or not tipo:
            messagebox.showwarning("Validación", "Seleccioná un tipo.")
            return None
        if not descripcion:
            messagebox.showwarning("Validación", "Descripción requerida.")
            return None
        
        try:
            monto = float(monto_txt)
            if monto < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Validación", "Monto inválido.")
            return None

        try:
            id_alquiler = int(alquiler_sel.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Error interno ID alquiler.")
            return None

        return {
            "id_alquiler": id_alquiler, "tipo": tipo,
            "descripcion": descripcion, "monto": monto
        }

    def _guardar_incidente(self):
        datos = self._validar_form()
        if datos is None: return

        ok, r = IncidenteService.crear_incidente(
            datos["id_alquiler"], datos["tipo"], datos["descripcion"], datos["monto"]
        )

        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Incidente registrado.")
        self._limpiar_formulario()
        self._cargar_incidentes_en_tabla()

    def _marcar_pagado(self):
        if self._incidente_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un incidente.")
            return

        if not messagebox.askyesno("Confirmar", "¿Marcar como PAGADO?"): return

        ok, r = IncidenteService.marcar_incidente_como_pagado(self._incidente_actual_id)
        if not ok:
            messagebox.showerror("Error", r)
            return

        messagebox.showinfo("OK", "Incidente pagado.")
        self._limpiar_formulario()
        self._cargar_incidentes_en_tabla()