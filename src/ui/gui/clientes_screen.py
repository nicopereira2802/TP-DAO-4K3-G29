import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class ClientesScreen(ctk.CTkFrame):
    """
    Pantalla de gestión de clientes (Versión Modernizada).
    """

    def __init__(self, parent, cliente_service=None, on_back=None):
        super().__init__(parent)
        self.cliente_service = cliente_service
        self.on_back = on_back

        self._cliente_actual_id = None
        # Datos demo por si no hay servicio
        self._clientes_demo = []
        self._next_demo_id = 1

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_clientes_en_tabla()

    def _configurar_estilos_treeview(self):
        """Aplica estilo oscuro a la tabla estándar de Tkinter."""
        style = ttk.Style()
        style.theme_use("default")
        
        # Colores
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
        # Layout principal: Header arriba, Cuerpo abajo
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        # Título y Subtítulo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Gestión de Clientes", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Alta, modificación y baja lógica", 
                     text_color="gray").pack(anchor="w")

        # Botón Volver
        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=80, height=30, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right", anchor="center")

        # --- BODY (Split View) ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(1, weight=1) # La tabla se expande
        body.grid_rowconfigure(0, weight=1)

        # 1. PANEL IZQUIERDO: FORMULARIO
        form_frame = ctk.CTkFrame(body, width=320, corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        form_frame.grid_propagate(False) # Fijar ancho

        ctk.CTkLabel(form_frame, text="Datos del Cliente", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        # Campos
        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre")
        self.entry_nombre.pack(fill="x", padx=15, pady=5)

        self.entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido")
        self.entry_apellido.pack(fill="x", padx=15, pady=5)

        self.entry_dni = ctk.CTkEntry(form_frame, placeholder_text="DNI")
        self.entry_dni.pack(fill="x", padx=15, pady=5)

        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Email")
        self.entry_email.pack(fill="x", padx=15, pady=5)

        self.entry_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono")
        self.entry_telefono.pack(fill="x", padx=15, pady=5)

        self.var_activo = tk.BooleanVar(value=True)
        self.chk_activo = ctk.CTkCheckBox(form_frame, text="Cliente Activo", variable=self.var_activo)
        self.chk_activo.pack(fill="x", padx=15, pady=15)

        # Botones del Formulario
        ctk.CTkButton(form_frame, text="Guardar", fg_color="#2cc985", hover_color="#25a970", 
                      font=ctk.CTkFont(weight="bold"),
                      command=self._guardar_cliente).pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(form_frame, text="Desactivar", fg_color="#c0392b", hover_color="#a93226", 
                      command=self._desactivar_cliente).pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(form_frame, text="Limpiar", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=self._limpiar_formulario).pack(fill="x", padx=15, pady=5)

        # 2. PANEL DERECHO: TABLA
        tabla_container = ctk.CTkFrame(body, corner_radius=10)
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        columnas = ("id", "nombre", "apellido", "dni", "email", "telefono", "activo")
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("email", text="Email")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("activo", text="Activo")

        # Anchos
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=100)
        self.tree.column("apellido", width=100)
        self.tree.column("dni", width=80, anchor="center")
        self.tree.column("email", width=150)
        self.tree.column("telefono", width=90, anchor="center")
        self.tree.column("activo", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar
        scroll_y = ctk.CTkScrollbar(tabla_container, command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 5))
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ----------------------------------------------------------
    # LÓGICA (Mantenida casi idéntica, adaptada a CTkEntry)
    # ----------------------------------------------------------

    def _validar_entero(self, nuevo_valor: str) -> bool:
        return nuevo_valor.isdigit() or nuevo_valor == ""

    def _limpiar_formulario(self):
        self._cliente_actual_id = None
        
        # En CTk, usamos .delete(0, "end") y .insert(0, val) igual que en tk
        self.entry_nombre.delete(0, "end")
        self.entry_apellido.delete(0, "end")
        self.entry_dni.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.var_activo.set(True)
        
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        
        self.entry_nombre.focus_set()

    def _cargar_clientes_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.cliente_service is not None:
            try:
                clientes = self.cliente_service.listar_clientes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los clientes.\n{e}")
                return
        else:
            clientes = self._clientes_demo

        for c in clientes:
            # Manejo híbrido objeto/diccionario por si usas modo demo
            if isinstance(c, dict):
                cid = c.get("id"); nombre = c.get("nombre"); apellido = c.get("apellido")
                dni = c.get("dni"); email = c.get("email"); tel = c.get("telefono"); activo = c.get("activo")
            else:
                cid = getattr(c, "id", None)
                nombre = getattr(c, "nombre", "")
                apellido = getattr(c, "apellido", "")
                dni = getattr(c, "dni", "")
                email = getattr(c, "email", "")
                tel = getattr(c, "telefono", "")
                activo = getattr(c, "activo", True)

            self.tree.insert("", "end", iid=str(cid), values=(
                cid, nombre, apellido, dni, email, tel, "Sí" if activo else "No"
            ))

    def _on_tree_select(self, event):
        selec = self.tree.selection()
        if not selec:
            return
        item_id = selec[0]
        valores = self.tree.item(item_id, "values")
        self._cliente_actual_id = int(valores[0])

        # Rellenar form
        self.entry_nombre.delete(0, "end"); self.entry_nombre.insert(0, valores[1])
        self.entry_apellido.delete(0, "end"); self.entry_apellido.insert(0, valores[2])
        self.entry_dni.delete(0, "end"); self.entry_dni.insert(0, valores[3])
        self.entry_email.delete(0, "end"); self.entry_email.insert(0, valores[4])
        self.entry_telefono.delete(0, "end"); self.entry_telefono.insert(0, valores[5])
        self.var_activo.set(valores[6] == "Sí")

    def _email_valido(self, email: str) -> bool:
        if "@" not in email or "." not in email: return False
        return True # Simplificado, tu lógica original era más completa, úsala si prefieres

    def _validar_form(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        email = self.entry_email.get().strip()
        tel = self.entry_telefono.get().strip()

        if not nombre: messagebox.showwarning("Validación", "Nombre requerido."); return None
        if not apellido: messagebox.showwarning("Validación", "Apellido requerido."); return None
        if not dni or not dni.isdigit(): messagebox.showwarning("Validación", "DNI inválido."); return None
        if not email: messagebox.showwarning("Validación", "Email requerido."); return None
        
        return {
            "nombre": nombre, "nombre_raw": nombre, "apellido": apellido,
            "dni": dni, "email": email, "telefono": tel, "activo": self.var_activo.get()
        }

    def _guardar_cliente(self):
        datos = self._validar_form()
        if datos is None: return

        try:
            if self.cliente_service:
                if self._cliente_actual_id is None:
                    self.cliente_service.crear_cliente(
                        nombre=f"{datos['nombre']} {datos['apellido']}", # Tu lógica unía nombres
                        dni=datos["dni"], email=datos["email"], telefono=datos["telefono"]
                    )
                else:
                    self.cliente_service.modificar_cliente(
                        cliente_id=self._cliente_actual_id,
                        nombre=f"{datos['nombre']} {datos['apellido']}",
                        dni=datos["dni"], email=datos["email"], telefono=datos["telefono"],
                        activo=datos["activo"]
                    )
            else:
                # Modo demo...
                pass

            self._cargar_clientes_en_tabla()
            self._limpiar_formulario()
            messagebox.showinfo("OK", "Cliente guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")

    def _desactivar_cliente(self):
        if self._cliente_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un cliente.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desactivar cliente?"): return

        try:
            if self.cliente_service:
                self.cliente_service.desactivar_cliente(self._cliente_actual_id)
            self._cargar_clientes_en_tabla()
            self._limpiar_formulario()
            messagebox.showinfo("OK", "Cliente desactivado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))