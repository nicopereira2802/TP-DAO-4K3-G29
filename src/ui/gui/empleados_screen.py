import tkinter as tk
from tkinter import ttk, messagebox


class EmpleadosScreen(ttk.Frame):
    """
    Pantalla de gestión de empleados.

    Usa EmpleadoService para alta, modificación y baja lógica.
    """

    def __init__(self, parent, empleado_service, on_back=None):
        super().__init__(parent)
        self.empleado_service = empleado_service
        self.on_back = on_back

        self._empleado_actual_id = None

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_empleados_en_tabla()

    # ------------------ Estilos ------------------ #
    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("EmpTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("EmpSubtitle.TLabel", font=("Segoe UI", 10), foreground="#555555")

    # ------------------ UI principal ------------------ #
    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Gestión de empleados",
            style="EmpTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Alta, modificación y baja lógica de empleados con usuario y rol.",
            style="EmpSubtitle.TLabel"
        ).grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ----------- Formulario ----------- #
        form = ttk.LabelFrame(body, text="Datos del empleado", padding=10)
        form.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.entry_nombre = ttk.Entry(form, width=25)
        self.entry_nombre.grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Apellido:").grid(row=2, column=0, sticky="w")
        self.entry_apellido = ttk.Entry(form, width=25)
        self.entry_apellido.grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="DNI:").grid(row=4, column=0, sticky="w")
        vcmd_dni = (self.register(self._validar_entero), "%P")
        self.entry_dni = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_dni
        )
        self.entry_dni.grid(row=5, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Email:").grid(row=6, column=0, sticky="w")
        self.entry_email = ttk.Entry(form, width=30)
        self.entry_email.grid(row=7, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Teléfono:").grid(row=8, column=0, sticky="w")
        vcmd_tel = (self.register(self._validar_entero), "%P")
        self.entry_telefono = ttk.Entry(
            form,
            width=20,
            validate="key",
            validatecommand=vcmd_tel
        )
        self.entry_telefono.grid(row=9, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Usuario:").grid(row=10, column=0, sticky="w")
        self.entry_usuario = ttk.Entry(form, width=25)
        self.entry_usuario.grid(row=11, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Contraseña:").grid(row=12, column=0, sticky="w")
        self.entry_password = ttk.Entry(form, width=25, show="*")
        self.entry_password.grid(row=13, column=0, sticky="w", pady=(0, 8))

        ttk.Label(form, text="Rol:").grid(row=14, column=0, sticky="w")
        self.combo_rol = ttk.Combobox(
            form,
            values=["ADMIN", "EMPLEADO"],
            state="readonly",
            width=22,
        )
        self.combo_rol.current(1)  # por defecto EMPLEADO
        self.combo_rol.grid(row=15, column=0, sticky="w", pady=(0, 8))

        self.var_activo = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            form,
            text="Empleado activo",
            variable=self.var_activo
        ).grid(row=16, column=0, sticky="w", pady=(5, 10))

        btns = ttk.Frame(form)
        btns.grid(row=17, column=0, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Guardar", command=self._guardar_empleado) \
            .grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btns, text="Desactivar", command=self._desactivar_empleado) \
            .grid(row=0, column=1, padx=5)

        # ----------- Tabla ----------- #
        tabla_frame = ttk.LabelFrame(body, text="Listado de empleados", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("id", "nombre", "apellido", "usuario", "rol", "email", "activo")
        self.tree = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=15,
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("email", text="Email")
        self.tree.heading("activo", text="Activo")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=110)
        self.tree.column("apellido", width=110)
        self.tree.column("usuario", width=100)
        self.tree.column("rol", width=80, anchor="center")
        self.tree.column("email", width=180)
        self.tree.column("activo", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ------------------ Helpers / Validaciones ------------------ #
    def _validar_entero(self, nuevo_valor: str) -> bool:
        if nuevo_valor == "":
            return True
        return nuevo_valor.isdigit()

    def _email_valido(self, email: str) -> bool:
        email = (email or "").strip()
        if "@" not in email or "." not in email:
            return False
        parte_local, dominio = email.split("@", 1)
        if not parte_local or not dominio:
            return False
        if "." not in dominio:
            return False
        if dominio.startswith("."):
            return False
        partes = dominio.split(".")
        if any(not p for p in partes):
            return False
        return True

    def _limpiar_formulario(self):
        self._empleado_actual_id = None
        for entry in (
            self.entry_nombre,
            self.entry_apellido,
            self.entry_dni,
            self.entry_email,
            self.entry_telefono,
            self.entry_usuario,
            self.entry_password,
        ):
            entry.delete(0, tk.END)
        self.combo_rol.set("EMPLEADO")
        self.var_activo.set(True)
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self.entry_nombre.focus_set()

    # ------------------ Carga de tabla ------------------ #
    def _cargar_empleados_en_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ok, res = self.empleado_service.listar_empleados()
        if not ok:
            messagebox.showerror("Error", res)
            return

        empleados = res
        for emp in empleados:
            self.tree.insert(
                "",
                "end",
                iid=str(emp.id_empleado),
                values=(
                    emp.id_empleado,
                    emp.nombre,
                    emp.apellido,
                    emp.usuario,
                    emp.rol,
                    emp.email,
                    "Sí" if emp.activo else "No",
                ),
            )

    # ------------------ Selección en tabla ------------------ #
    def _on_tree_select(self, event):
        selec = self.tree.selection()
        if not selec:
            return

        item_id = selec[0]
        valores = self.tree.item(item_id, "values")
        self._empleado_actual_id = int(valores[0])

        ok, emp_o_msg = self.empleado_service.obtener_empleado_por_id(self._empleado_actual_id)
        if not ok:
            messagebox.showerror("Error", emp_o_msg)
            return

        emp = emp_o_msg

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, emp.nombre)

        self.entry_apellido.delete(0, tk.END)
        self.entry_apellido.insert(0, emp.apellido)

        self.entry_dni.delete(0, tk.END)
        self.entry_dni.insert(0, emp.dni)

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, emp.email)

        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, emp.telefono)

        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, emp.usuario)

        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, emp.password)

        self.combo_rol.set(emp.rol)
        self.var_activo.set(emp.activo)

    # ------------------ Validación de formulario ------------------ #
    def _validar_form(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        email = self.entry_email.get().strip()
        telefono = self.entry_telefono.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        rol = self.combo_rol.get().strip()
        activo = self.var_activo.get()

        if not nombre:
            messagebox.showwarning("Validación", "El nombre no puede estar vacío.")
            return None
        if not apellido:
            messagebox.showwarning("Validación", "El apellido no puede estar vacío.")
            return None
        if not dni:
            messagebox.showwarning("Validación", "El DNI no puede estar vacío.")
            return None
        if not dni.isdigit() or len(dni) < 7 or len(dni) > 10:
            messagebox.showwarning("Validación", "El DNI debe tener entre 7 y 10 dígitos numéricos.")
            return None
        if not email:
            messagebox.showwarning("Validación", "El email no puede estar vacío.")
            return None
        if not self._email_valido(email):
            messagebox.showwarning("Validación", "El email no tiene un formato válido.")
            return None
        if not usuario:
            messagebox.showwarning("Validación", "El usuario no puede estar vacío.")
            return None
        if " " in usuario:
            messagebox.showwarning("Validación", "El usuario no puede contener espacios.")
            return None
        if not password or len(password) < 4:
            messagebox.showwarning(
                "Validación",
                "La contraseña debe tener al menos 4 caracteres."
            )
            return None
        if rol not in ("ADMIN", "EMPLEADO"):
            messagebox.showwarning("Validación", "Seleccioná un rol válido.")
            return None

        return {
            "nombre": nombre,
            "apellido": apellido,
            "dni": dni,
            "email": email,
            "telefono": telefono,
            "usuario": usuario,
            "password": password,
            "rol": rol,
            "activo": activo,
        }

    # ------------------ Guardar (alta / modificación) ------------------ #
    def _guardar_empleado(self):
        datos = self._validar_form()
        if datos is None:
            return

        if self._empleado_actual_id is None:
            ok, res = self.empleado_service.crear_empleado(
                datos["nombre"],
                datos["apellido"],
                datos["dni"],
                datos["email"],
                datos["telefono"],
                datos["usuario"],
                datos["password"],
                datos["rol"],
            )
        else:
            ok, res = self.empleado_service.actualizar_empleado(
                self._empleado_actual_id,
                datos["nombre"],
                datos["apellido"],
                datos["dni"],
                datos["email"],
                datos["telefono"],
                datos["usuario"],
                datos["password"],
                datos["rol"],
                datos["activo"],
            )

        if not ok:
            messagebox.showerror("Error", res)
            return

        self._cargar_empleados_en_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("OK", "Empleado guardado correctamente.")

    # ------------------ Desactivar ------------------ #
    def _desactivar_empleado(self):
        if self._empleado_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un empleado para desactivar.")
            return

        if not messagebox.askyesno("Confirmar", "¿Seguro que querés desactivar este empleado?"):
            return

        ok, res = self.empleado_service.inactivar_empleado(self._empleado_actual_id)
        if not ok:
            messagebox.showerror("Error", res)
            return

        self._cargar_empleados_en_tabla()
        self._limpiar_formulario()
        messagebox.showinfo("OK", "Empleado desactivado.")
