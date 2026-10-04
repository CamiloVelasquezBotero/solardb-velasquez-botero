-- 01_tablas.sql : staging, tabla destino y bitacora ETL (PostgreSQL 15+)
-- Se usa IF NOT EXISTS para que el script pueda ejecutarse varias veces.

CREATE TABLE IF NOT EXISTS stg_lectura_raw (
  id          BIGSERIAL PRIMARY KEY,
  payload     JSONB NOT NULL,
  cargado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lectura_demo (
  dispositivo_id INT NOT NULL,
  ts             TIMESTAMPTZ NOT NULL,
  p_ac           NUMERIC(10,3) CHECK (p_ac >= 0),
  irradiancia    NUMERIC(8,1)  CHECK (irradiancia BETWEEN 0 AND 1500),
  temp_modulo    NUMERIC(5,1),
  payload        JSONB,
  PRIMARY KEY (dispositivo_id, ts)
);

-- Bitacora del proceso ETL (ver respuesta E4)
CREATE TABLE IF NOT EXISTS etl_log (
  id                BIGSERIAL PRIMARY KEY,
  proceso           TEXT NOT NULL DEFAULT 'carga_lecturas',
  inicio            TIMESTAMPTZ NOT NULL DEFAULT now(),
  fin               TIMESTAMPTZ,
  archivo           TEXT,
  filas_leidas      INT,
  filas_cargadas    INT,
  filas_duplicadas  INT,
  filas_rechazadas  INT,
  estado            TEXT NOT NULL DEFAULT 'EN_CURSO'
                    CHECK (estado IN ('EN_CURSO', 'OK', 'ERROR')),
  error             TEXT
);
