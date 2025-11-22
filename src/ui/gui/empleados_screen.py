import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class EmpleadosScreen(ctk.CTkFrame):
    """
    Pantalla de gestión de empleados (Versión Modernizada).
    """

    def __init__(self, parent, empleado_service, on_back=None):
        super().__init__(parent)
        self.empleado_service = empleado_service
        self.on_back = on_back

        self._empleado_actual_id = None

        self._configurar_estilos_treeview()
        self._construir_ui()
        self._cargar_empleados_en_tabla()

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
        
        ctk.CTkLabel(title_frame, text="Gestión de Empleados", 
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Administración de usuarios y accesos", 
                     text_color="gray").pack(anchor="w")

        if self.on_back:
            ctk.CTkButton(header, text="Volver", width=80, height=30, 
                          fg_color="#444", hover_color="#333", 
                          command=self.on_back).pack(side="right", anchor="center")

        # --- BODY ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # 1. FORMULARIO (Izquierda)
        # Usamos ScrollableFrame porque son muchos campos
        form_frame = ctk.CTkScrollableFrame(body, width=320, corner_radius=10, label_text="Datos del Empleado")
        form_frame.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        # Nota: ScrollableFrame no soporta grid_propagate(False) directo facil, 
        # pero con width fijo funciona bien visualmente.

        self.entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre")
        self.entry_nombre.pack(fill="x", padx=10, pady=5)

        self.entry_apellido = ctk.CTkEntry(form_frame, placeholder_text="Apellido")
        self.entry_apellido.pack(fill="x", padx=10, pady=5)

        self.entry_dni = ctk.CTkEntry(form_frame, placeholder_text="DNI")
        self.entry_dni.pack(fill="x", padx=10, pady=5)

        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="Email")
        self.entry_email.pack(fill="x", padx=10, pady=5)

        self.entry_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono")
        self.entry_telefono.pack(fill="x", padx=10, pady=5)

        # Separador visual
        ttk.Separator(form_frame, orient="horizontal").pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(form_frame, text="Credenciales de Acceso", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10)

        self.entry_usuario = ctk.CTkEntry(form_frame, placeholder_text="Usuario")
        self.entry_usuario.pack(fill="x", padx=10, pady=5)

        self.entry_password = ctk.CTkEntry(form_frame, placeholder_text="Contraseña", show="*")
        self.entry_password.pack(fill="x", padx=10, pady=5)

        self.combo_rol = ctk.CTkComboBox(form_frame, values=["EMPLEADO", "ADMIN"], state="readonly")
        self.combo_rol.set("EMPLEADO")
        self.combo_rol.pack(fill="x", padx=10, pady=5)

        self.var_activo = tk.BooleanVar(value=True)
        self.chk_activo = ctk.CTkCheckBox(form_frame, text="Empleado Activo", variable=self.var_activo)
        self.chk_activo.pack(fill="x", padx=10, pady=15)

        # Botones (dentro del scroll para asegurar que se vean)
        ctk.CTkButton(form_frame, text="Guardar", fg_color="#2cc985", hover_color="#25a970", 
                      font=ctk.CTkFont(weight="bold"),
                      command=self._guardar_empleado).pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(form_frame, text="Desactivar", fg_color="#c0392b", hover_color="#a93226", 
                      command=self._desactivar_empleado).pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(form_frame, text="Limpiar", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                      command=self._limpiar_formulario).pack(fill="x", padx=10, pady=5)

        # 2. TABLA (Derecha)
        tabla_container = ctk.CTkFrame(body, corner_radius=10)
        tabla_container.grid(row=0, column=1, sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        columnas = ("id", "nombre", "apellido", "usuario", "rol", "email", "activo")
        self.tree = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("email", text="Email")
        self.tree.heading("activo", text="Activo")

        # Anchos
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=100)
        self.tree.column("apellido", width=100)
        self.tree.column("usuario", width=90)
        self.tree.column("rol", width=80, anchor="center")
        self.tree.column("email", width=150)
        self.tree.column("activo", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar
        scroll_y = ctk.CTkScrollbar(tabla_container, command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 5))
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ----------------------------------------------------------
    # LÓGICA
    # ----------------------------------------------------------

    def _limpiar_formulario(self):
        self._empleado_actual_id = None
        
        self.entry_nombre.delete(0, "end")
        self.entry_apellido.delete(0, "end")
        self.entry_dni.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")
        
        self.combo_rol.set("EMPLEADO")
        self.var_activo.set(True)
        
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        
        self.entry_nombre.focus_set()

    def _cargar_empleados_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, res = self.empleado_service.listar_empleados()
        if not ok:
            messagebox.showerror("Error", res)
            return

        for emp in res:
            self.tree.insert("", "end", iid=str(emp.id_empleado), values=(
                emp.id_empleado, emp.nombre, emp.apellido, 
                emp.usuario, emp.rol, emp.email, 
                "Sí" if emp.activo else "No"
            ))

    def _on_tree_select(self, event):
        selec = self.tree.selection()
        if not selec: return

        item_id = selec[0]
        valores = self.tree.item(item_id, "values")
        self._empleado_actual_id = int(valores[0])

        # Cargar datos completos desde el servicio para tener la pass (o no)
        ok, emp = self.empleado_service.obtener_empleado_por_id(self._empleado_actual_id)
        if not ok: return

        self.entry_nombre.delete(0, "end"); self.entry_nombre.insert(0, emp.nombre)
        self.entry_apellido.delete(0, "end"); self.entry_apellido.insert(0, emp.apellido)
        self.entry_dni.delete(0, "end"); self.entry_dni.insert(0, emp.dni)
        self.entry_email.delete(0, "end"); self.entry_email.insert(0, emp.email)
        self.entry_telefono.delete(0, "end"); self.entry_telefono.insert(0, emp.telefono)
        self.entry_usuario.delete(0, "end"); self.entry_usuario.insert(0, emp.usuario)
        self.entry_password.delete(0, "end"); self.entry_password.insert(0, emp.password)
        
        self.combo_rol.set(emp.rol)
        self.var_activo.set(emp.activo)

    def _email_valido(self, email):
        return "@" in email and "." in email # Simplificado

    def _validar_form(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        email = self.entry_email.get().strip()
        tel = self.entry_telefono.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        rol = self.combo_rol.get().strip()

        if not nombre: messagebox.showwarning("Validación", "Nombre requerido."); return None
        if not apellido: messagebox.showwarning("Validación", "Apellido requerido."); return None
        if not dni or not dni.isdigit(): messagebox.showwarning("Validación", "DNI inválido."); return None
        if not self._email_valido(email): messagebox.showwarning("Validación", "Email inválido."); return None
        if not usuario: messagebox.showwarning("Validación", "Usuario requerido."); return None
        if len(password) < 4: messagebox.showwarning("Validación", "Contraseña mín 4 chars."); return None

        return {
            "nombre": nombre, "apellido": apellido, "dni": dni,
            "email": email, "telefono": tel, "usuario": usuario,
            "password": password, "rol": rol, "activo": self.var_activo.get()
        }

    def _guardar_empleado(self):
        datos = self._validar_form()
        if datos is None: return

        if self._empleado_actual_id is None:
            ok, res = self.empleado_service.crear_empleado(**datos)
        else:
            ok, res = self.empleado_service.actualizar_empleado(
                id_empleado=self._empleado_actual_id,
                **datos
            )

        if not ok:
            messagebox.showerror("Error", res)
            return

        self._cargar_empleados_en_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("OK", "Empleado guardado correctamente.")

    def _desactivar_empleado(self):
        if self._empleado_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un empleado.")
            return

        if not messagebox.askyesno("Confirmar", "¿Desactivar empleado?"): return

        ok, res = self.empleado_service.inactivar_empleado(self._empleado_actual_id)
        if not ok:
            messagebox.showerror("Error", res)
            return

        self._cargar_empleados_en_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("OK", "Empleado desactivado.")