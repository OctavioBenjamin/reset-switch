import time

import serial

from controlador.base import ControladorSwitch


class ControladorHP(ControladorSwitch):
    """Controlador para switches HP"""

    PROMPT_CONTRASENA = "Password:"
    PROMPT_MODO_CONFIG = "(config"
    PROMPT_FINAL = "#"
    ESPERA = 1.0

    def conectar(self):
        print(f"[INFO] HP: Abriendo puerto serial {self.puerto} a {self.baud} baudios...")
        self.conexion = serial.Serial(
            port=self.puerto,
            baudrate=self.baud,
            timeout=5,
        )
        time.sleep(2)
        self._limpiar_buffer()
        print("[INFO] HP: Puerto serial abierto.")

    def login(self):
        print("[INFO] HP: Enviando contrasena...")
        self._enviar("")
        time.sleep(self.ESPERA)
        self._limpiar_buffer()

        self._enviar(self.contrasena)
        time.sleep(self.ESPERA)
        print("[INFO] HP: Contrasena enviada.")

    def enviar_configuracion(self, lineas: list[str]):
        print("[INFO] HP: Entrando a modo configuracion...")
        self._enviar("config")
        time.sleep(self.ESPERA)

        comandos_enviados = 0
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("!"):
                continue
            self._enviar(linea)
            comandos_enviados += 1
            time.sleep(0.5)

        self._enviar("exit")
        time.sleep(self.ESPERA)
        print(f"[INFO] HP: Configuracion enviada ({comandos_enviados} comandos).")

    def guardar(self):
        print("[INFO] HP: Guardando configuracion en memoria...")
        self._enviar("write memory")
        time.sleep(2)
        print("[INFO] HP: Configuracion guardada.")

    def desconectar(self):
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            print("[INFO] HP: Puerto serial cerrado.")

    def _enviar(self, comando: str):
        self.conexion.write(f"{comando}\n".encode("ascii"))
        self.conexion.flush()
        time.sleep(0.3)

    def _limpiar_buffer(self):
        if self.conexion:
            self.conexion.read(self.conexion.in_waiting or 1)
