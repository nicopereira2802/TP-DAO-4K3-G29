import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from src.services.auth_service import AuthService

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_login_ok, on_cancel):
        super().__init__(parent)
        self.on_login_ok = on_login_ok
        self.on_cancel = on_cancel
        self._construir_ui()

    def _construir_ui(self):
        # Configurar este frame para que ocupe todo el espacio
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.pack(fill="both", expand=True)

        # --- TARJETA CENTRAL DE LOGIN ---
        # Creamos un frame más pequeño y centrado con bordes redondeados
        card = ctk.CTkFrame(self, width=400, height=500, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Título y Subtítulo
        ctk.CTkLabel(
            card, 
            text="Iniciar Sesión", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            card, 
            text="Ingresá tus credenciales para acceder", 
            font=ctk.CTkFont(size=12), 
            text_color="gray"
        ).pack(pady=(0, 30))

        # Campos de entrada
        self.entry_user = ctk.CTkEntry(
            card, 
            width=280, 
            height=45, 
            placeholder_text="Usuario",
            corner_radius=10
        )
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(
            card, 
            width=280, 
            height=45, 
            placeholder_text="Contraseña", 
            show="*",
            corner_radius=10
        )
        self.entry_pass.pack(pady=10)

        # Botones
        ctk.CTkButton(
            card, 
            text="Ingresar", 
            width=280, 
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#3A7AFE", 
            hover_color="#2c5dcf",
            corner_radius=10,
            command=self._login
        ).pack(pady=(30, 10))

        # Botón sutil para cancelar/volver
        ctk.CTkButton(
            card, 
            text="Volver al inicio", 
            width=200, 
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            command=self.on_cancel
        ).pack(pady=10)

        # Footer pequeño dentro de la tarjeta
        ctk.CTkLabel(
            card, 
            text="Sistema RentaYa v2.0", 
            font=ctk.CTkFont(size=10), 
            text_color="gray50"
        ).pack(side="bottom", pady=20)

        # Vincular tecla Enter para login rápido
        self.entry_user.bind("<Return>", lambda event: self._login())
        self.entry_pass.bind("<Return>", lambda event: self._login())

        # Dar foco al usuario al iniciar
        self.after(100, lambda: self.entry_user.focus_set())

    def _login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        # Llamada al servicio (Lógica original intacta)
        ok, res = AuthService.login(username, password)
        
        if not ok:
            # Usamos messagebox estándar porque es modal y simple
            messagebox.showerror("Acceso denegado", res)
            # Limpiar contraseña en caso de error
            self.entry_pass.delete(0, "end")
            return

        # Si es OK, llamamos al callback que nos pasó app.py
        self.on_login_ok(res)