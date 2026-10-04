"""Simulador IoT de SolarDB: genera lecturas JSON de dos dispositivos.

Modificaciones respecto al script base:
  - Genera lecturas de DOS dispositivos (device_id 1 y 2).
  - Agrega un campo nuevo: voltaje_dc (V), tension de entrada DC del inversor.
  - Usa semilla fija para que el archivo de muestra sea reproducible.
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone

random.seed(811)  # grupo 811: datos reproducibles

TZ = timezone(timedelta(hours=-5))                    # hora de Colombia
inicio = datetime(2026, 10, 5, 6, 0, tzinfo=TZ)
DISPOSITIVOS = [1, 2]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

with open(os.path.join(DATA_DIR, "lecturas.jsonl"), "w", encoding="utf-8") as f:
    for i in range(144):                              # 12 h, una lectura cada 5 min
        ts = (inicio + timedelta(minutes=5 * i)).isoformat()
        for device_id in DISPOSITIVOS:
            msg = {
                "device_id": device_id,
                "ts": ts,
                "p_ac": round(random.uniform(0, 5.0), 3),          # kW
                "irradiancia": round(random.uniform(0, 1000), 1),  # W/m2
                "temp_modulo": round(random.uniform(18, 60), 1),   # grados C
                "voltaje_dc": round(random.uniform(300, 800), 1),  # V (campo nuevo)
            }
            if random.random() < 0.03:
                msg["alarma"] = "GRID_FAULT"
            f.write(json.dumps(msg) + "\n")

print("Archivo generado: data/lecturas.jsonl (288 mensajes, 2 dispositivos)")
