import tkinter as tk
from tkinter import ttk, messagebox

from src.services.auth_service import AuthService


class LoginScreen(ttk.Frame):
    def __init__(self, parent, on_login_ok, on_cancel):
        super().__init__(parent)
        self.on_login_ok = on_login_ok
        self.on_cancel = on_cancel
        self._construir_ui()

    def _construir_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        marco = ttk.Frame(self)
        marco.grid(row=0, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)

        titulo = ttk.Label(
            marco,
            text="Iniciar sesión",
            font=("Segoe UI", 20, "bold")
        )
        titulo.grid(row=0, column=0, pady=(40, 20), padx=20, sticky="n")

        form = ttk.Frame(marco)
        form.grid(row=1, column=0, pady=20, padx=20)

        ttk.Label(form, text="Usuario:").grid(
            row=0, column=0, sticky="e", pady=5, padx=5
        )
        ttk.Label(form, text="Contraseña:").grid(
            row=1, column=0, sticky="e", pady=5, padx=5
        )

        self.entry_user = ttk.Entry(form, width=30)
        self.entry_pass = ttk.Entry(form, width=30, show="*")

        self.entry_user.grid(row=0, column=1, pady=5, padx=5)
        self.entry_pass.grid(row=1, column=1, pady=5, padx=5)

        botones = ttk.Frame(form)
        botones.grid(row=2, column=0, columnspan=2, pady=15)

        btn_login = ttk.Button(botones, text="Ingresar", command=self._login)
        btn_cancel = ttk.Button(botones, text="Cancelar", command=self.on_cancel)

        btn_login.pack(side="left", padx=5)
        btn_cancel.pack(side="left", padx=5)

        ayuda = ttk.Label(
            marco,
            text="Ingresá el usuario y la contraseña asignados a tu empleado.\n"
                 "Si no tenés usuario, pedíselo al administrador del sistema.",
            foreground="gray",
            justify="center"
        )
        ayuda.grid(row=2, column=0, pady=(10, 0))

        # Foco inicial y Enter para loguear
        self.entry_user.focus_set()
        self.entry_pass.bind("<Return>", lambda _: self._login())

    def _login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        ok, res = AuthService.login(username, password)
        if not ok:
            messagebox.showerror("Error de login", res)
            return

        # res es el dict que devuelve AuthService (id_empleado, nombre_completo, rol, username)
        self.on_login_ok(res)
