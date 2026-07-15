from controlador.base import ControladorSwitch
from controlador.cisco import ControladorCisco
from controlador.hp import ControladorHP

MAPEO_DRIVERS = {
    "cisco_ios": ControladorCisco,
    "hp_procurve": ControladorHP,
}

__all__ = ["ControladorSwitch", "ControladorCisco", "ControladorHP", "MAPEO_DRIVERS"]
