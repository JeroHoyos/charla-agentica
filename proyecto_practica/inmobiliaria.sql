-- La base del proyecto: los apartamentos de la Inmobiliaria Señor Gato (inventados) y las visitas.
-- En venta, el precio es el valor del apartamento. En arriendo, el canon mensual. Todo en pesos.

DROP TABLE IF EXISTS apartamentos;
DROP TABLE IF EXISTS visitas;

CREATE TABLE apartamentos (
    codigo       TEXT PRIMARY KEY,
    barrio       TEXT,
    negocio      TEXT,      -- venta o arriendo
    precio       INTEGER,
    alcobas      INTEGER,
    mascotas     INTEGER,   -- 1 si las admite
    parqueadero  INTEGER    -- 1 si tiene
);

CREATE TABLE visitas (
    id       INTEGER PRIMARY KEY,
    codigo   TEXT,
    cliente  TEXT,
    fecha    TEXT,
    hora     TEXT
);

INSERT INTO apartamentos VALUES
    ('SG-101', 'Laureles',   'venta',    380000000, 3, 1, 1),
    ('SG-102', 'Laureles',   'venta',    415000000, 3, 0, 1),
    ('SG-103', 'Laureles',   'arriendo',   2600000, 2, 1, 1),
    ('SG-107', 'Laureles',   'venta',    365000000, 3, 1, 0),
    ('SG-201', 'El Poblado', 'venta',    420000000, 1, 1, 1),
    ('SG-203', 'El Poblado', 'arriendo',   3800000, 1, 1, 0),
    ('SG-301', 'Envigado',   'venta',    520000000, 3, 1, 1),
    ('SG-302', 'Envigado',   'arriendo',   3200000, 3, 1, 1),
    ('SG-303', 'Sabaneta',   'venta',    330000000, 2, 1, 1),
    ('SG-304', 'Sabaneta',   'arriendo',   2200000, 2, 0, 1),
    ('SG-401', 'Belén',      'venta',    295000000, 3, 1, 1),
    ('SG-403', 'Belén',      'arriendo',   2100000, 3, 1, 1),
    ('SG-406', 'Robledo',    'venta',    215000000, 2, 1, 0),
    ('SG-407', 'Robledo',    'arriendo',   1300000, 2, 1, 0);
