import pexpect
import pexpect.fdpexpect
import serial

from controlador.base import ControladorSwitch

class ControladorHP1910(ControladorSwitch):
    """Controlador para switches HP 1910 (Comware-based)."""

    PROMPT_USER = r"<[\w\-]+>"
    PROMPT_SYSTEM = r"\[[\w\-]+\]"
    PROMPT_PASSWORD = "Password:"
    PROMPT_SAVE = r"\[Y/N\]"
    TIMEOUT = 30
    TIMEOUT_CMD = 10

    def __init__(self, puerto: str, baud: int, credenciales: dict):
        super().__init__(puerto, baud, credenciales)
        self.automatizador = None

    def conectar(self):
        print(f"[INFO] HP1910: Abriendo puerto serial {self.puerto} a {self.baud} baudios...")

        # Pyserial abre la conexion
        self.conexion = serial.Serial(
            port=self.puerto,
            baudrate=self.baud,
            timeout=0.1,
        )

        # Pexpect toma la conexion que abrio pyserial 
        # fd -> descriptor de archivo -> /proc/PID_SCRIPT/fd
        self.automatizador = pexpect.fdpexpect.fdspawn(
            self.conexion,
            timeout=self.TIMEOUT,
            encoding="ascii",
            codec_errors="replace",
        )
        print("[INFO] HP1910: Puerto serial abierto.")

    def login(self):
        assert self.automatizador is not None
        print("[INFO] HP1910: Iniciando sesion...")
        self.automatizador.sendline("")

        # expect queda esperando hasta encontrar un patron (uno de los PROMPTs)
        index = self.automatizador.expect([self.PROMPT_PASSWORD, self.PROMPT_USER], timeout=self.TIMEOUT)

        if index == 0:
            print("[INFO] HP1910: Enviando contrasena...")
            self.automatizador.sendline(self.contrasena)

            # Se queda esperando hasta encontrar el patron que indica que ingreso a entorno de usuario
            self.automatizador.expect(self.PROMPT_USER, timeout=self.TIMEOUT)
            print("[INFO] HP1910: Contrasena aceptada.")

        print("[INFO] HP1910: Sesion iniciada.")

    def desbloquear_comandos(self):
        # Desbloquea el catalogo completo de comandos en los switches HP 1910
        assert self.automatizador is not None

        print("[INFO] HP1910: Desbloqueando catalogo completo de comandos...")
        self.automatizador.sendline("_cmdline-mode on")
        
        # El swtich pregunta si quieremos mostrar todos los comandos -> [Y/N]
        index = self.automatizador.expect([self.PROMPT_SAVE, self.PROMPT_PASSWORD], timeout=self.TIMEOUT_CMD)
        if index == 0:
            self.automatizador.sendline("Y")
            self.automatizador.expect(self.PROMPT_PASSWORD, timeout=self.TIMEOUT_CMD)

        self.automatizador.sendline("512900")
        self.automatizador.expect(self.PROMPT_USER, timeout=self.TIMEOUT_CMD)
        print("[INFO] HP1910: Catalogo de comandos desbloqueado.")

    def enviar_configuracion(self, lineas: list[str]):
        # Recibe una lista de configuraciones en texto plano
        # Envia linea a linea

        assert self.automatizador is not None

        print("[INFO] HP1910: Entrando a modo sistema...")
        self.automatizador.sendline("system-view")
        self.automatizador.expect(self.PROMPT_SYSTEM, timeout=self.TIMEOUT_CMD)

        comandos_enviados = 0
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("!"):
                continue
            self.automatizador.sendline(linea)
            self.automatizador.expect(self.PROMPT_SYSTEM, timeout=self.TIMEOUT_CMD)
            comandos_enviados += 1

        print(f"[INFO] HP1910: Saliendo de modo sistema ({comandos_enviados} comandos).")
        self.automatizador.sendline("return")
        self.automatizador.expect(self.PROMPT_USER, timeout=self.TIMEOUT_CMD)
        print("[INFO] HP1910: Configuracion enviada.")

    def guardar(self):
        # Envia comando para guardar 
        # Manda aceptacion con Y
        assert self.automatizador is not None

        print("[INFO] HP1910: Guardando configuracion...")
        self.automatizador.sendline("save")
        index = self.automatizador.expect([self.PROMPT_SAVE, self.PROMPT_USER], timeout=self.TIMEOUT_CMD)
        if index == 0:
            self.automatizador.sendline("Y")
            self.automatizador.expect(self.PROMPT_USER, timeout=self.TIMEOUT)
        print("[INFO] HP1910: Configuracion guardada.")

    def desconectar(self):
        # Cierra la conexion con pyserial
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            print("[INFO] HP1910: Puerto serial cerrado.")
