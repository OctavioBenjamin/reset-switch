from controlador.base import ControladorSwitch
from controlador.cisco import ControladorCisco
from controlador.hp_1910 import ControladorHP1910

MAPEO_DRIVERS = {
    "cisco_ios": ControladorCisco,
    "hp_1910": ControladorHP1910,
}

__all__ = ["ControladorSwitch", "ControladorCisco", "ControladorHP1910", "MAPEO_DRIVERS"]
