# src/ui/gui/clientes_screen.py

import tkinter as tk
from tkinter import ttk, messagebox


class ClientesScreen(ttk.Frame):
    """
    Pantalla de gestión de clientes.

    Usa ClienteService para CRUD real.
    Si cliente_service es None, funciona en modo demo en memoria.
    """

    def __init__(self, parent, cliente_service=None, on_back=None):
        super().__init__(parent)
        self.cliente_service = cliente_service
        self.on_back = on_back

        self._cliente_actual_id = None

        # modo demo (por si algún día lo querés usar sin BD)
        self._clientes_demo = []
        self._next_demo_id = 1

        self._configurar_estilos()
        self._construir_ui()
        self._cargar_clientes_en_tabla()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("ClientesTitle.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure(
            "ClientesSubtitle.TLabel",
            font=("Segoe UI", 10),
            foreground="#555555"
        )

    def _construir_ui(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(self, padding=(20, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Gestión de clientes",
            style="ClientesTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Alta, modificación y baja lógica de clientes.",
            style="ClientesSubtitle.TLabel"
        ).grid(row=1, column=0, sticky="w")

        if self.on_back:
            ttk.Button(header, text="Volver al panel", command=self.on_back) \
                .grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="e")

        body = ttk.Frame(self, padding=20)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(body, text="Datos del cliente", padding=10)
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

        self.var_activo = tk.BooleanVar(value=True)
        chk_activo = ttk.Checkbutton(
            form,
            text="Cliente activo",
            variable=self.var_activo
        )
        chk_activo.grid(row=10, column=0, sticky="w", pady=(5, 10))

        btns = ttk.Frame(form)
        btns.grid(row=11, column=0, pady=(10, 0), sticky="w")

        ttk.Button(btns, text="Guardar", command=self._guardar_cliente) \
            .grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btns, text="Desactivar", command=self._desactivar_cliente) \
            .grid(row=0, column=1, padx=5)

        tabla_frame = ttk.LabelFrame(body, text="Listado de clientes", padding=10)
        tabla_frame.grid(row=0, column=1, sticky="nsew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("id", "nombre", "apellido", "dni", "email", "telefono", "activo")
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
        self.tree.heading("dni", text="DNI")
        self.tree.heading("email", text="Email")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("activo", text="Activo")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=120)
        self.tree.column("apellido", width=120)
        self.tree.column("dni", width=80, anchor="center")
        self.tree.column("email", width=180)
        self.tree.column("telefono", width=100, anchor="center")
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

    # -------- helpers/validaciones --------

    def _validar_entero(self, nuevo_valor: str) -> bool:
        if nuevo_valor == "":
            return True
        return nuevo_valor.isdigit()

    def _limpiar_formulario(self):
        self._cliente_actual_id = None
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.entry_dni.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.var_activo.set(True)
        self.entry_nombre.focus_set()
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def _cargar_clientes_en_tabla(self):
        # limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # obtener datos
        if self.cliente_service is not None:
            try:
                clientes = self.cliente_service.listar_clientes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los clientes.\n{e}")
                return
        else:
            clientes = self._clientes_demo

        # cargar filas
        for c in clientes:
            if isinstance(c, dict):
                cid = c.get("id")
                nombre = c.get("nombre", "")
                apellido = c.get("apellido", "")
                dni = c.get("dni", "")
                email = c.get("email", "")
                tel = c.get("telefono", "")
                activo = c.get("activo", True)
            else:
                cid = getattr(c, "id", None)
                nombre = getattr(c, "nombre", "")
                apellido = getattr(c, "apellido", "")
                dni = getattr(c, "dni", "")
                email = getattr(c, "email", "")
                tel = getattr(c, "telefono", "")
                activo = getattr(c, "activo", True)

            self.tree.insert(
                "",
                "end",
                iid=str(cid),
                values=(
                    cid,
                    nombre,
                    apellido,
                    dni,
                    email,
                    tel,
                    "Sí" if activo else "No",
                ),
            )

    def _on_tree_select(self, event):
        selec = self.tree.selection()
        if not selec:
            return
        item_id = selec[0]
        valores = self.tree.item(item_id, "values")
        self._cliente_actual_id = int(valores[0])

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, valores[1])

        self.entry_apellido.delete(0, tk.END)
        self.entry_apellido.insert(0, valores[2])

        self.entry_dni.delete(0, tk.END)
        self.entry_dni.insert(0, valores[3])

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, valores[4])

        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, valores[5])

        self.var_activo.set(valores[6] == "Sí")

    def _validar_form(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        email = self.entry_email.get().strip()
        tel = self.entry_telefono.get().strip()

        if not nombre:
            messagebox.showwarning("Validación", "El nombre no puede estar vacío.")
            return None
        if not apellido:
            messagebox.showwarning("Validación", "El apellido no puede estar vacío.")
            return None
        if not dni or len(dni) < 7 or len(dni) > 8:
            messagebox.showwarning("Validación", "El DNI debe tener 7 u 8 dígitos.")
            return None
        if not self._email_valido(email):
            messagebox.showwarning(
                "Validación",
                "El email no tiene un formato válido.\nEj: ejemplo@gmail.com",
            )
            return None
        if tel and len(tel) < 6:
            messagebox.showwarning(
                "Validación",
                "El teléfono parece demasiado corto."
            )
            return None

        nombre_completo = f"{nombre} {apellido}".strip()

        return {
            "nombre": nombre_completo,
            "nombre_raw": nombre,
            "apellido": apellido,
            "dni": dni,
            "email": email,
            "telefono": tel,
            "activo": self.var_activo.get(),
        }

    def _email_valido(self, email: str) -> bool:
        if "@" not in email or "." not in email:
            return False
        partes = email.split("@")
        if len(partes) != 2 or not partes[0]:
            return False
        dominio = partes[1]
        dominios_validos = (
            "gmail.com",
            "hotmail.com",
            "outlook.com",
            "yahoo.com",
            "frc.utn.edu.ar",
        )
        if dominio.lower() not in dominios_validos:
            return False
        return True

    def _guardar_cliente(self):
        datos = self._validar_form()
        if datos is None:
            return

        try:
            if self.cliente_service is not None:
                if self._cliente_actual_id is None:
                    # alta
                    self.cliente_service.crear_cliente(
                        nombre=datos["nombre"],
                        dni=datos["dni"],
                        email=datos["email"],
                        telefono=datos["telefono"],
                    )
                else:
                    # modificación
                    self.cliente_service.modificar_cliente(
                        cliente_id=self._cliente_actual_id,
                        nombre=datos["nombre"],
                        dni=datos["dni"],
                        email=datos["email"],
                        telefono=datos["telefono"],
                        activo=datos["activo"],
                    )
            else:
                # modo demo
                if self._cliente_actual_id is None:
                    nuevo = {
                        "id": self._next_demo_id,
                        "nombre": datos["nombre_raw"],
                        "apellido": datos["apellido"],
                        "dni": datos["dni"],
                        "email": datos["email"],
                        "telefono": datos["telefono"],
                        "activo": datos["activo"],
                    }
                    self._next_demo_id += 1
                    self._clientes_demo.append(nuevo)
                else:
                    for c in self._clientes_demo:
                        if c["id"] == self._cliente_actual_id:
                            c.update(
                                {
                                    "nombre": datos["nombre_raw"],
                                    "apellido": datos["apellido"],
                                    "dni": datos["dni"],
                                    "email": datos["email"],
                                    "telefono": datos["telefono"],
                                    "activo": datos["activo"],
                                }
                            )
                            break

            self._cargar_clientes_en_tabla()
            self._limpiar_formulario()
            messagebox.showinfo("OK", "Cliente guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el cliente.\n{e}")

    def _desactivar_cliente(self):
        if self._cliente_actual_id is None:
            messagebox.showwarning("Atención", "Seleccioná un cliente para desactivar.")
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Seguro que querés desactivar este cliente?"
        ):
            return

        try:
            if self.cliente_service is not None:
                self.cliente_service.desactivar_cliente(self._cliente_actual_id)
            else:
                for c in self._clientes_demo:
                    if c["id"] == self._cliente_actual_id:
                        c["activo"] = False
                        break

            self._cargar_clientes_en_tabla()
            self._limpiar_formulario()
            messagebox.showinfo("OK", "Cliente desactivado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo desactivar el cliente.\n{e}")
