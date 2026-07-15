#!/usr/bin/env python3
"""
Script para resetear switches de red a configuracion base.

Se conecta por serial a cada dispositivo, inicia sesion y aplica la configuracion base desde las plantillas.

Uso:
    python resetear.py              # resetea todos los dispositivos
    python resetear.py -d switch-1  # resetea solo switch-1
"""

import argparse
import os
import sys

import yaml

from controlador import MAPEO_DRIVERS

RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
RUTA_PLANTILLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantillas")

def cargar_configuracion(ruta: str) -> dict:
    print(f"[INFO] Cargando configuracion desde {ruta}")
    with open(ruta, "r") as archivo:
        config = yaml.safe_load(archivo)
    cantidad = len(config.get("devices", []))
    print(f"[INFO] Dispositivos encontrados: {cantidad}")
    return config

def cargar_plantilla(driver: str) -> str:
    # Recibe un dispositivo y carga su plantilla de configuraciones
    ruta = os.path.join(RUTA_PLANTILLAS, f"{driver}.cfg")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe plantilla para driver '{driver}': {ruta}")
    with open(ruta, "r") as archivo:
        return archivo.read()

def renderizar_plantilla(plantilla: str, dispositivo: dict) -> list[str]:
    # Recibe la plantilla y las configuraciones del dispositivo
    # Devuelve la plantilla de configuracion linea a linea
    credenciales = dispositivo["credentials"]
    variables = {
        "hostname": dispositivo["name"],
        "mgmt_vlan": dispositivo["mgmt_vlan"],
        "mgmt_ip": dispositivo["mgmt_ip"],
        "subnet_mask": dispositivo["subnet_mask"],
        "default_gateway": dispositivo["default_gateway"],
        "username": credenciales["username"],
        "password": credenciales["password"],
        "enable_password": credenciales["enable_password"],
    }
    contenido = plantilla.format(**variables)
    return [linea for linea in contenido.splitlines()]


def configurar_dispositivo(dispositivo: dict):
    nombre = dispositivo["name"]
    driver = dispositivo["driver"]

    print(f"[INFO] === Procesando {nombre} ===")

    if driver not in MAPEO_DRIVERS:
        print(f"[ERROR] [{nombre}] Driver no soportado: {driver}")
        return

    print(f"[INFO] [{nombre}] Conectando a {dispositivo['port']} ({driver})...")

    try:
        plantilla = cargar_plantilla(driver)
        lineas = renderizar_plantilla(plantilla, dispositivo)
        print(f"[INFO] [{nombre}] Plantilla {driver}.cfg cargada ({len(lineas)} lineas)")

        clase_controlador = MAPEO_DRIVERS[driver]
        controlador = clase_controlador(
            puerto=dispositivo["port"],
            baud=dispositivo["baud"],
            credenciales=dispositivo["credentials"],
        )

        controlador.ejecutar(lineas)
        print(f"[INFO] [{nombre}] Configuracion aplicada correctamente.")

    except Exception as error:
        print(f"[ERROR] [{nombre}] {error}")


def main():
    parser = argparse.ArgumentParser(description="Resetear switches a configuracion base.")
    parser.add_argument("-d", "--dispositivo", help="Nombre del dispositivo a configurar.")
    args = parser.parse_args() # Recibir parametro por consola

    print("[INFO] Iniciando script de reseteo de switches...")

    configuracion = cargar_configuracion(RUTA_CONFIG) # Recibe config.yaml
    dispositivos = configuracion.get("devices", []) # Busca devices dentro del diccionario 

    if not dispositivos:
        print(f"[ERROR] No hay dispositivos definidos en {RUTA_CONFIG}")
        sys.exit(1)

    if args.dispositivo: # Verifica si recibio el parametro -d
        dispositivos = [d for d in dispositivos if d["name"] == args.dispositivo]
        if not dispositivos:
            print(f"[ERROR] Dispositivo '{args.dispositivo}' no encontrado en config.yaml")
            sys.exit(1)

    configurados = 0
    for dispositivo in dispositivos:
        configurar_dispositivo(dispositivo)
        configurados += 1

    print(f"[INFO] Proceso finalizado. {configurados}/{len(dispositivos)} dispositivos configurados.")


if __name__ == "__main__":
    main()
