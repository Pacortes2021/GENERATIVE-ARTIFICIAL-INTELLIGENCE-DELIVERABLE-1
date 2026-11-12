"""Especificaciones curadas por bloques para el dataset de fine-tuning del Redactor."""

from __future__ import annotations

from dataset_blocks.bloques_1_2 import (
    BLOQUE_1_CITAS_CRUCE,
    BLOQUE_2_CONDICIONES_EXCEPCIONES,
)
from dataset_blocks.bloques_3_4 import (
    BLOQUE_3_POLARES_Y_LECTURA,
    BLOQUE_4_CALCULOS_Y_ORDEN,
)
from dataset_blocks.bloques_5_6 import (
    BLOQUE_5_RESILIENCIA_FEEDBACK,
    BLOQUE_6_ABSTENCION_HONESTA,
)

__all__ = [
    "BLOQUE_1_CITAS_CRUCE",
    "BLOQUE_2_CONDICIONES_EXCEPCIONES",
    "BLOQUE_3_POLARES_Y_LECTURA",
    "BLOQUE_4_CALCULOS_Y_ORDEN",
    "BLOQUE_5_RESILIENCIA_FEEDBACK",
    "BLOQUE_6_ABSTENCION_HONESTA",
]
