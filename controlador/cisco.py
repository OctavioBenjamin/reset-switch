import time

import serial

from controlador.base import ControladorSwitch


class ControladorCisco(ControladorSwitch):
    # La interfaz define: Puerto, baud, usuario, password y password enable. 
    """Controlador para switches Cisco IOS."""

    ESPERA = 1.0

    def conectar(self):
        print(f"[INFO] Cisco: Abriendo puerto serial {self.puerto} a {self.baud} baudios...")
        self.conexion = serial.Serial(
            port=self.puerto,
            baudrate=self.baud,
            timeout=5,
        )
        time.sleep(2)
        self._limpiar_buffer()
        print("[INFO] Cisco: Puerto serial abierto.")

    def login(self):
        print("[INFO] Cisco: Enviando credenciales...")
        self._enviar("")
        time.sleep(self.ESPERA)
        self._limpiar_buffer()

        self._enviar(self.usuario)
        time.sleep(self.ESPERA)
        self._enviar(self.contrasena)
        time.sleep(self.ESPERA)
        print("[INFO] Cisco: Credenciales enviadas.")

        print("[INFO] Cisco: Entrando a modo enable...")
        self._entrar_enable()
        print("[INFO] Cisco: Modo enable activado.")

    def enviar_configuracion(self, lineas: list[str]):
        print("[INFO] Cisco: Entrando a modo configuracion...")
        self._enviar("configure terminal")
        time.sleep(self.ESPERA)

        comandos_enviados = 0
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith("!"):
                continue
            self._enviar(linea)
            comandos_enviados += 1
            time.sleep(0.5)

        self._enviar("end")
        time.sleep(self.ESPERA)
        print(f"[INFO] Cisco: Configuracion enviada ({comandos_enviados} comandos).")

    def guardar(self):
        print("[INFO] Cisco: Guardando configuracion en memoria...")
        self._enviar("write memory")
        time.sleep(2)
        print("[INFO] Cisco: Configuracion guardada.")

    def desconectar(self):
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            print("[INFO] Cisco: Puerto serial cerrado.")

    def _entrar_enable(self):
        self._enviar("enable")
        time.sleep(self.ESPERA)
        self._limpiar_buffer()
        self._enviar(self.contrasena_enable)
        time.sleep(self.ESPERA)

    def _enviar(self, comando: str):
        self.conexion.write(f"{comando}\n".encode("ascii"))
        self.conexion.flush()
        time.sleep(0.3)

    def _limpiar_buffer(self):
        if self.conexion:
            self.conexion.read(self.conexion.in_waiting or 1)
