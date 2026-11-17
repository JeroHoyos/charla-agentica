-- La base del proyecto: los apartamentos en venta de la Inmobiliaria Señor Gato (inventados) y las visitas.
-- El precio es el valor del apartamento, en pesos.

DROP TABLE IF EXISTS apartamentos;
DROP TABLE IF EXISTS visitas;

CREATE TABLE apartamentos (
    codigo       TEXT PRIMARY KEY,  -- el número del apartamento: 101
    barrio       TEXT,
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
    ('101', 'Laureles',   380000000, 3, 1, 1),
    ('102', 'Laureles',   415000000, 3, 0, 1),
    ('103', 'Laureles',   310000000, 2, 1, 1),
    ('107', 'Laureles',   365000000, 3, 1, 0),
    ('201', 'El Poblado', 420000000, 1, 1, 1),
    ('203', 'El Poblado', 395000000, 1, 1, 0),
    ('301', 'Envigado',   520000000, 3, 1, 1),
    ('302', 'Envigado',   470000000, 3, 1, 1),
    ('303', 'Sabaneta',   330000000, 2, 1, 1),
    ('304', 'Sabaneta',   305000000, 2, 0, 1),
    ('401', 'Belén',      295000000, 3, 1, 1),
    ('403', 'Belén',      320000000, 3, 1, 1),
    ('406', 'Robledo',    215000000, 2, 1, 0),
    ('407', 'Robledo',    230000000, 2, 1, 0);
