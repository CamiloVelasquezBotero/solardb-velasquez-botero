"""Punto de entrada unico del pipeline ETL de SolarDB (practica guiada).

Uso:
    python etl/run_etl.py                 # flujo completo (simula si falta el archivo)
    python etl/run_etl.py --regenerar     # vuelve a generar data/lecturas.jsonl
    python etl/run_etl.py --paso staging  # solo carga el archivo a stg_lectura_raw

Flujo: simulador -> validacion JSON -> staging (JSONB) -> INSERT...SELECT idempotente
       -> registro en etl_log.
Las credenciales se leen de variables de entorno o del archivo .env (excluido de Git).
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

BASE = Path(__file__).resolve().parent.parent
ARCHIVO = BASE / "data" / "lecturas.jsonl"


def cargar_env():
    """Lee .env (si existe) sin sobrescribir variables ya definidas."""
    ruta = BASE / ".env"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip())


def conectar():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "solardb"),
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def leer_y_validar():
    """Devuelve (lineas_validas, leidas, rechazadas). Rechaza JSON invalido o sin device_id/ts."""
    validas, leidas, rechazadas = [], 0, 0
    with open(ARCHIVO, encoding="utf-8") as f:
        for linea in f:
            if not linea.strip():
                continue
            leidas += 1
            try:
                msg = json.loads(linea)
                if "device_id" not in msg or "ts" not in msg:
                    raise ValueError("faltan device_id o ts")
                validas.append((linea.strip(),))
            except ValueError:
                rechazadas += 1
    return validas, leidas, rechazadas


def cargar_staging(cur, validas):
    cur.execute("TRUNCATE stg_lectura_raw")  # staging transitorio: se recarga en cada corrida
    execute_values(cur, "INSERT INTO stg_lectura_raw (payload) VALUES %s",
                   validas, template="(%s::jsonb)")


def main():
    ap = argparse.ArgumentParser(description="ETL SolarDB")
    ap.add_argument("--regenerar", action="store_true", help="regenerar data/lecturas.jsonl")
    ap.add_argument("--paso", choices=["todo", "staging"], default="todo")
    args = ap.parse_args()

    cargar_env()
    if args.regenerar or not ARCHIVO.exists():
        subprocess.run([sys.executable, str(BASE / "etl" / "simulador.py")], check=True)

    conn = conectar()
    cur = conn.cursor()
    cur.execute((BASE / "sql" / "01_tablas.sql").read_text(encoding="utf-8"))
    conn.commit()

    validas, leidas, rechazadas = leer_y_validar()

    if args.paso == "staging":
        cargar_staging(cur, validas)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM stg_lectura_raw")
        print(f"stg_lectura_raw: {cur.fetchone()[0]} filas")
        return 0

    cur.execute("INSERT INTO etl_log (archivo) VALUES (%s) RETURNING id", (ARCHIVO.name,))
    log_id = cur.fetchone()[0]
    conn.commit()

    cargadas, estado, error = 0, "OK", None
    try:
        cargar_staging(cur, validas)
        cur.execute((BASE / "sql" / "02_carga.sql").read_text(encoding="utf-8"))
        cargadas = cur.rowcount
        conn.commit()
    except Exception as exc:  # cualquier falla: revertir y dejar constancia
        conn.rollback()
        estado, error = "ERROR", str(exc)

    duplicadas = len(validas) - cargadas if estado == "OK" else None
    cur.execute(
        """UPDATE etl_log SET fin = now(), filas_leidas = %s, filas_cargadas = %s,
                  filas_duplicadas = %s, filas_rechazadas = %s, estado = %s, error = %s
           WHERE id = %s""",
        (leidas, cargadas, duplicadas, rechazadas, estado, error, log_id),
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM lectura_demo")
    total = cur.fetchone()[0]
    print(f"ETL {estado}: leidas={leidas} cargadas={cargadas} duplicadas={duplicadas} "
          f"rechazadas={rechazadas}")
    print(f"SELECT COUNT(*) FROM lectura_demo -> {total}")
    if error:
        print(f"Error: {error}", file=sys.stderr)
    conn.close()
    return 0 if estado == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
