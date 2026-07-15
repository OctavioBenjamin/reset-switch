# rlab-switches

Script de reseteo de switches de red para el laboratorio remoto de la materia de Redes.

## Descripción

Herramienta que conecta por puerto serial a switches Cisco IOS y HP ProCurve para
restaurarlos a su configuración base antes de cada trabajo práctico. La Raspberry Pi
gestiona las conexiones seriales y aplica las configuraciones de forma automatizada.

## Funcionalidad

- Conexión serial a switches Cisco y HP
- Configuración base: hostname, VLAN de gestión, IP, gateway, credenciales
- Reset completo de todos los dispositivos o uno específico vía `-d`
- Plantillas editables por tipo de dispositivo

## Uso

```bash
pip install -r requirements.txt
python resetear.py              # resetea todos los dispositivos
python resetear.py -d switch-1  # resetea uno específico
```

## Configuración

Los dispositivos se definen en `config.yaml` con su puerto serial, baud rate,
driver y credenciales. Las plantillas de configuración están en `plantillas/`.

## Estructura

```
├── config.yaml              # Dispositivos conectados
├── resetear.py              # Script principal
├── requirements.txt         # Dependencias (pyserial, pyyaml)
├── controlador/             # Controladores por tipo de switch
│   ├── __init__.py          # Mapeo de drivers a controladores
│   ├── base.py              # Clase abstracta ControladorSwitch
│   ├── cisco.py             # ControladorCisco (IOS)
│   └── hp.py                # ControladorHP (ProCurve)
└── plantillas/              # Configuraciones base
    ├── cisco_ios.cfg
    └── hp_procurve.cfg
```

