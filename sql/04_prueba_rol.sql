-- 04_prueba_rol.sql : demostracion del rol de solo lectura.
-- Ejecutar conectado como solar_lector:
--   psql -U solar_lector -d solardb -f sql/04_prueba_rol.sql
SELECT current_user AS usuario;
SELECT COUNT(*) AS filas FROM lectura_demo;           -- debe funcionar

-- Este INSERT debe ser rechazado: ERROR: permission denied for table lectura_demo
INSERT INTO lectura_demo (dispositivo_id, ts, p_ac)
VALUES (99, now(), 1.000);
