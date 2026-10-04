-- 05_consultas_jsonb.sql : consultas con operadores nativos de JSONB (respuesta I4)
-- Se ejecutan sobre lectura_demo.payload (o stg_lectura_raw.payload).

-- 1) Operadores -> y ->> : extraer atributos como JSON o como texto
SELECT payload->>'ts'                      AS ts,
       (payload->>'p_ac')::numeric         AS p_ac_kw,
       payload->>'voltaje_dc'              AS voltaje_dc_v
FROM lectura_demo
WHERE (payload->>'device_id')::int = 1
ORDER BY ts
LIMIT 5;

-- 2) Operadores ? y @> : existencia de clave y contenencia
SELECT dispositivo_id, ts, payload->>'alarma' AS alarma
FROM lectura_demo
WHERE payload ? 'alarma'
  AND payload @> '{"alarma": "GRID_FAULT"}';
