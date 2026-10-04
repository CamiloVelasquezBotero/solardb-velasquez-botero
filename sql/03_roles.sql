-- 03_roles.sql : gobernanza aplicada, minimo privilegio.
-- Las claves NO van en este archivo: se pasan como variables de psql, por ejemplo:
--   psql -U postgres -d solardb -v pwd_lector="'ClaveLector'" -v pwd_ingesta="'ClaveIngesta'" -v pwd_admin="'ClaveAdmin'" -f sql/03_roles.sql
-- Ejecutar una sola vez (CREATE ROLE falla si el rol ya existe).

CREATE ROLE solar_lector  LOGIN PASSWORD :pwd_lector;
CREATE ROLE solar_ingesta LOGIN PASSWORD :pwd_ingesta;
CREATE ROLE solar_admin   LOGIN PASSWORD :pwd_admin;

-- Quitar permisos por defecto
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- Conexion y uso del esquema
GRANT CONNECT ON DATABASE solardb TO solar_lector, solar_ingesta, solar_admin;
GRANT USAGE ON SCHEMA public TO solar_lector, solar_ingesta, solar_admin;

-- solar_lector: solo lectura (rol de consulta)
GRANT SELECT ON lectura_demo, etl_log TO solar_lector;

-- solar_ingesta: usado por el proceso ETL
GRANT SELECT, INSERT, TRUNCATE ON stg_lectura_raw TO solar_ingesta;
GRANT SELECT, INSERT           ON lectura_demo    TO solar_ingesta;
GRANT SELECT, INSERT, UPDATE   ON etl_log         TO solar_ingesta;
GRANT USAGE ON SEQUENCE stg_lectura_raw_id_seq, etl_log_id_seq TO solar_ingesta;

-- solar_admin: control total para mantenimiento
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO solar_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO solar_admin;
