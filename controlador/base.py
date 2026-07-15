from abc import ABC, abstractmethod


class ControladorSwitch(ABC):
    """Clase abstracta base para controladores de switches de red."""

    def __init__(self, puerto: str, baud: int, credenciales: dict):
        self.puerto = puerto
        self.baud = baud
        self.usuario = credenciales.get("username", "")
        self.contrasena = credenciales.get("password", "")
        self.contrasena_enable = credenciales.get("enable_password", "")
        self.conexion = None

    @abstractmethod
    def conectar(self):
        """Abrir conexion serial con el dispositivo."""

    @abstractmethod
    def login(self):
        """Iniciar sesion y obtener privilegios de administrador."""

    @abstractmethod
    def enviar_configuracion(self, lineas: list[str]):
        """Enviar configuracion linea a linea al dispositivo."""

    @abstractmethod
    def guardar(self):
        """Guardar configuracion en memoria permanente."""

    @abstractmethod
    def desconectar(self):
        """Cerrar conexion serial."""

    def ejecutar(self, lineas_config: list[str]):
        """Ejecuta el flujo completo: conectar -> login -> configurar -> guardar -> desconectar."""
        print("[INFO] Iniciando flujo de configuracion...")
        self.conectar()
        print("[INFO] Autenticando...")
        self.login()
        print("[INFO] Enviando configuracion...")
        self.enviar_configuracion(lineas_config)
        print("[INFO] Guardando configuracion en memoria...")
        self.guardar()
        print("[INFO] Desconectando del dispositivo...")
        self.desconectar()
        print("[INFO] Flujo de configuracion completado.")
