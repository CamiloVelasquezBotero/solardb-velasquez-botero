# SolarDB Pascual - Consulta Bases de Datos I

**Autor:** Camilo Velasquez Botero
**Curso:** Bases de Datos I (SD1006) - Grupo 811 - Semestre 2026-II
**Institucion:** Institucion Universitaria Pascual Bravo
**Docente:** Ramiro Grisales Montoya

> An idempotent ETL pipeline that loads simulated IoT telemetry into a governed PostgreSQL repository, versioned on GitHub.

## Descripcion

Trabajo de consulta sobre gobernanza de datos, automatizacion ETL e IoT para el proyecto SolarDB Pascual.
Incluye una practica guiada: un simulador IoT genera mensajes JSON de dos dispositivos, los mensajes entran
a una tabla de staging (`stg_lectura_raw`, JSONB) y de alli pasan a una tabla relacional (`lectura_demo`)
con una carga idempotente (`INSERT ... ON CONFLICT DO NOTHING`), bitacora (`etl_log`) y roles de minimo privilegio.

El informe completo esta en `docs/Camilo_Velasquez_Botero_Consulta_BD1_G811.pdf`.

## Estructura

```
solardb-velasquez-botero/
|-- README.md
|-- .gitignore
|-- .env.example        plantilla de variables de entorno (sin claves reales)
|-- requirements.txt
|-- docs/               PDF de la consulta, generar_pdf.py y capturas/
|-- data/               lecturas.jsonl de muestra
|-- etl/                simulador.py, run_etl.py
`-- sql/                01_tablas.sql, 02_carga.sql, 03_roles.sql, 04_prueba_rol.sql, 05_consultas_jsonb.sql
```

## Requisitos

- PostgreSQL 15 o superior (y `psql` disponible)
- Python 3.10 o superior

## Pasos para reproducir (Windows 11, PowerShell)

1. Crear la base de datos:

   ```
   psql -U postgres -c "CREATE DATABASE solardb;"
   ```

2. Configurar credenciales (el archivo `.env` NO se sube a GitHub):

   ```
   copy .env.example .env
   notepad .env
   ```

3. Crear el entorno e instalar dependencias:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Ejecutar el pipeline completo con un unico comando (genera datos si faltan, crea tablas, carga, registra bitacora):

   ```
   python etl/run_etl.py
   ```

5. Prueba de idempotencia: ejecutar el mismo comando una segunda vez y verificar que el conteo no cambia:

   ```
   python etl/run_etl.py
   psql -U postgres -d solardb -c "SELECT COUNT(*) FROM lectura_demo;"
   psql -U postgres -d solardb -c "SELECT * FROM etl_log ORDER BY id;"
   ```

6. Crear los roles (las claves se pasan como variables, no estan en el codigo) y probar el rol de solo lectura:

   ```
   psql -U postgres -d solardb -v pwd_lector="'ClaveLector'" -v pwd_ingesta="'ClaveIngesta'" -v pwd_admin="'ClaveAdmin'" -f sql/03_roles.sql
   psql -U solar_lector -d solardb -f sql/04_prueba_rol.sql
   ```

   El `SELECT` funciona y el `INSERT` es rechazado con `permission denied`.

## Automatizacion (sin implementar)

Cron (cada hora):

```
0 * * * * cd /ruta/solardb-velasquez-botero && python etl/run_etl.py >> logs/etl.log 2>&1
```

Programador de tareas de Windows (equivalente):

```
schtasks /Create /SC HOURLY /TN "SolarDB_ETL" /TR "cmd /c cd /d C:\ruta\solardb-velasquez-botero && python etl\run_etl.py"
```

## Quien hizo que

| Integrante | Contribucion |
| --- | --- |
| Camilo Velasquez Botero | Todo el trabajo: consulta (Parte A), practica ETL (Parte B), repositorio y documentacion (Parte C) |

## Seguridad

Nunca se suben contrasenas ni cadenas de conexion. Las credenciales se leen de variables de entorno o de `.env`, que esta en `.gitignore`.
