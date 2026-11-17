-- Base de datos de la Inmobiliaria Señor Gato (inventada), Medellín.
-- Se puede correr las veces que quieras: borra las tablas y las vuelve a crear.
-- Precios en pesos. En venta, «precio» es el valor del inmueble; en arriendo, el canon mensual.
-- Es SQLite. «politicas» guarda las reglas de la inmobiliaria: también se consultan con SQL.

DROP TABLE IF EXISTS politicas;
DROP TABLE IF EXISTS visitas;
DROP TABLE IF EXISTS apartamentos;
DROP TABLE IF EXISTS asesores;

CREATE TABLE asesores (
    id        INTEGER PRIMARY KEY,
    nombre    TEXT NOT NULL,
    telefono  TEXT NOT NULL,
    zonas     TEXT NOT NULL
);

CREATE TABLE apartamentos (
    codigo          TEXT PRIMARY KEY,
    zona            TEXT NOT NULL,
    barrio          TEXT NOT NULL,
    negocio         TEXT NOT NULL CHECK (negocio IN ('venta', 'arriendo')),
    precio          INTEGER NOT NULL,
    alcobas         INTEGER NOT NULL,
    banos           INTEGER NOT NULL,
    area_m2         REAL NOT NULL,
    piso            INTEGER NOT NULL,
    estrato         INTEGER NOT NULL,
    administracion  INTEGER NOT NULL,
    parqueadero     INTEGER NOT NULL,
    ascensor        INTEGER NOT NULL,
    mascotas        INTEGER NOT NULL,
    estado          TEXT NOT NULL CHECK (estado IN ('disponible', 'reservado', 'vendido', 'arrendado')),
    asesor_id       INTEGER NOT NULL REFERENCES asesores (id),
    descripcion     TEXT NOT NULL
);

CREATE TABLE visitas (
    id       INTEGER PRIMARY KEY,
    codigo   TEXT NOT NULL REFERENCES apartamentos (codigo),
    cliente  TEXT NOT NULL,
    fecha    DATE NOT NULL,
    hora     TIME NOT NULL,
    estado   TEXT NOT NULL CHECK (estado IN ('programada', 'realizada', 'cancelada'))
);

CREATE TABLE politicas (
    id     INTEGER PRIMARY KEY,
    tema   TEXT NOT NULL,
    regla  TEXT NOT NULL,
    fuente TEXT NOT NULL
);

INSERT INTO asesores (nombre, telefono, zonas) VALUES
    ('Mariana Restrepo', '300 123 4501', 'Laureles-Estadio'),
    ('Julián Ospina',    '300 123 4502', 'El Poblado'),
    ('Catalina Gómez',   '300 123 4503', 'Envigado y Sabaneta'),
    ('Andrés Zapata',    '300 123 4504', 'Belén, La América, Robledo, Castilla, Buenos Aires y La Candelaria');

INSERT INTO apartamentos VALUES
    ('SG-101', 'Laureles-Estadio', 'Laureles',           'venta',     380000000, 3, 2,  92.0,  4, 5,  420000, 1,  0, 1,  'disponible', 1, 'Cocina remodelada, balcón y a 8 minutos a pie de la estación Estadio del metro.'),
    ('SG-102', 'Laureles-Estadio', 'Laureles',           'venta',     415000000, 3, 2,  98.0,  7, 5,  480000, 1,  1,  0, 'disponible', 1, 'Piso alto con ascensor y vista a la avenida Nutibara.'),
    ('SG-103', 'Laureles-Estadio', 'Laureles',           'arriendo',    2600000, 2, 2,  74.0,  3, 5,  350000, 1,  0, 1,  'disponible', 1, 'Remodelado, a tres cuadras de la UPB.'),
    ('SG-104', 'Laureles-Estadio', 'Estadio',            'venta',     455000000, 3, 2, 105.0,  5, 5,  510000, 1,  1,  1,  'reservado',  1, 'Unidad con piscina y gimnasio, a dos cuadras del estadio Atanasio Girardot.'),
    ('SG-105', 'Laureles-Estadio', 'Estadio',            'arriendo',    2900000, 3, 2,  96.0,  2, 5,  430000, 1,  0, 1,  'disponible', 1, 'Amplio, con patio interior y cuarto útil.'),
    ('SG-106', 'Laureles-Estadio', 'Conquistadores',     'venta',     560000000, 3, 3, 118.0,  9, 5,  620000, 1,  1,  0, 'disponible', 1, 'Dos parqueaderos, estudio y vista a la ciudad.'),
    ('SG-107', 'Laureles-Estadio', 'Laureles',           'venta',     365000000, 3, 2,  88.0,  2, 5,  390000, 0, 0, 1,  'disponible', 1, 'Sin parqueadero, por eso está por debajo del precio de la zona.'),
    ('SG-201', 'El Poblado',       'Manila',             'venta',     420000000, 1, 1,  55.0,  6, 6,  380000, 1,  1,  1,  'disponible', 2, 'Apartaestudio amoblado, ideal para renta corta.'),
    ('SG-202', 'El Poblado',       'Castropol',          'venta',     890000000, 3, 3, 140.0, 12, 6,  950000, 1,  1,  1,  'disponible', 2, 'Club house, piscina climatizada y dos parqueaderos.'),
    ('SG-203', 'El Poblado',       'Provenza',           'arriendo',    3800000, 1, 1,  52.0,  4, 6,  400000, 0, 1,  1,  'disponible', 2, 'En plena zona gastronómica; puede haber ruido los fines de semana.'),
    ('SG-204', 'El Poblado',       'Los Balsos',         'venta',    1250000000, 4, 4, 210.0,  8, 6, 1400000, 1,  1,  0, 'disponible', 2, 'Penthouse con terraza y jacuzzi.'),
    ('SG-205', 'El Poblado',       'Patio Bonito',       'arriendo',    4500000, 2, 2,  85.0, 10, 6,  600000, 1,  1,  0, 'arrendado',  2, 'Amoblado, con balcón y gimnasio.'),
    ('SG-301', 'Envigado',         'Zúñiga',             'venta',     520000000, 3, 2,  95.0, 11, 5,  560000, 1,  1,  1,  'disponible', 3, 'Unidad cerrada con zonas verdes y sendero para mascotas.'),
    ('SG-302', 'Envigado',         'La Magnolia',        'arriendo',    3200000, 3, 2,  90.0,  6, 4,  450000, 1,  1,  1,  'disponible', 3, 'Cerca al parque de Envigado y a colegios.'),
    ('SG-303', 'Sabaneta',         'Aves María',         'venta',     330000000, 2, 2,  68.0, 15, 4,  310000, 1,  1,  1,  'disponible', 3, 'Torre nueva, entrega con cocina integral.'),
    ('SG-304', 'Sabaneta',         'Las Lomitas',        'arriendo',    2200000, 2, 2,  64.0,  9, 4,  290000, 1,  1,  0, 'disponible', 3, 'A cinco minutos de la estación Sabaneta.'),
    ('SG-305', 'Envigado',         'El Portal',          'venta',     410000000, 3, 2,  82.0,  3, 4,  340000, 1,  0, 1,  'vendido',    3, 'Vendido en octubre.'),
    ('SG-401', 'Belén',            'La Mota',            'venta',     295000000, 3, 2,  72.0,  5, 4,  280000, 1,  1,  1,  'disponible', 4, 'Cerca al centro comercial Los Molinos.'),
    ('SG-402', 'Belén',            'Loma de los Bernal', 'venta',     520000000, 3, 3, 106.0, 14, 5,  590000, 1,  1,  1,  'disponible', 4, 'Vista panorámica y unidad con cancha sintética.'),
    ('SG-403', 'Belén',            'Rosales',            'arriendo',    2100000, 3, 2,  80.0,  2, 4,  250000, 1,  0, 1,  'disponible', 4, 'Primer piso con patio, ideal para mascotas.'),
    ('SG-404', 'La América',       'Calasanz',           'venta',     310000000, 3, 2,  76.0,  6, 4,  300000, 1,  1,  0, 'disponible', 4, 'A diez minutos de la estación Floresta.'),
    ('SG-405', 'La América',       'Simón Bolívar',      'venta',     340000000, 3, 2,  84.0,  3, 4,  320000, 1,  0, 1,  'reservado',  4, 'Cerca de la iglesia de La América y del parque.'),
    ('SG-406', 'Robledo',          'Pilarica',           'venta',     215000000, 2, 1,  60.0,  4, 3,  160000, 0, 0, 1,  'disponible', 4, 'Cerca de universidades y de la estación Floresta.'),
    ('SG-407', 'Robledo',          'Pilarica',           'arriendo',    1300000, 2, 1,  58.0,  2, 3,  150000, 0, 0, 1,  'disponible', 4, 'Ideal para estudiantes.'),
    ('SG-408', 'Castilla',         'Castilla',           'venta',     190000000, 3, 1,  62.0,  3, 3,  120000, 0, 0, 1,  'disponible', 4, 'Cerca de la estación Caribe.'),
    ('SG-409', 'Buenos Aires',     'Buenos Aires',       'arriendo',    1500000, 2, 1,  65.0,  4, 3,  180000, 0, 0, 1,  'disponible', 4, 'Al lado del tranvía de Ayacucho.'),
    ('SG-410', 'La Candelaria',    'Prado',              'venta',     260000000, 3, 2,  90.0,  2, 3,  200000, 0, 0, 1,  'disponible', 4, 'Barrio patrimonial, techos altos y pisos en baldosa original.');

INSERT INTO visitas (codigo, cliente, fecha, hora, estado) VALUES
    ('SG-101', 'Laura Pérez',     date('now', '+1 day'), '10:00', 'programada'),
    ('SG-104', 'Carlos Mejía',    date('now', '+2 day'), '15:00', 'programada'),
    ('SG-202', 'Ana Ruiz',        date('now', '-3 day'), '11:00', 'realizada'),
    ('SG-101', 'Santiago Vélez',  date('now', '-1 day'), '09:00', 'cancelada'),
    ('SG-303', 'Valentina Gil',   date('now', '+3 day'), '16:30', 'programada');

INSERT INTO politicas (tema, regla, fuente) VALUES
    ('arriendo',   'El arrendatario debe ganar al mes al menos tres veces el canon. Se pueden sumar los ingresos de hasta dos personas.', 'politicas_arriendo.pdf'),
    ('arriendo',   'Se pide un codeudor con propiedad raíz en el Valle de Aburrá o una póliza de arrendamiento. El estudio de la póliza cuesta 90.000 pesos, no es reembolsable y responde en dos días hábiles.', 'politicas_arriendo.pdf'),
    ('arriendo',   'No se cobra depósito en dinero: la Ley 820 de 2003 lo prohíbe en vivienda urbana.', 'politicas_arriendo.pdf'),
    ('arriendo',   'Los contratos son a doce meses y el canon sube cada año según el IPC. Se paga en los primeros cinco días del mes.', 'politicas_arriendo.pdf'),
    ('arriendo',   'Entregar antes de tiempo exige avisar con tres meses o pagar tres cánones de indemnización.', 'politicas_arriendo.pdf'),
    ('mascotas',   'Se permiten hasta dos mascotas por inmueble sin costo, salvo que el reglamento del edificio lo restrinja. La columna apartamentos.mascotas dice si se admiten.', 'politicas_arriendo.pdf'),
    ('visitas',    'Las visitas se agendan con al menos 24 horas de anticipación, de lunes a sábado entre las 8:00 y las 18:00. No hay visitas los domingos ni festivos. Las acompaña el asesor de la zona.', 'politicas_arriendo.pdf'),
    ('compra',     'Pasos: preaprobación del crédito, visita, oferta y promesa con arras del 10 %, estudio de títulos, avalúo, escritura, registro y entrega. De la promesa a la entrega pasan entre 45 y 60 días.', 'guia_compra.pdf'),
    ('credito',    'Los bancos prestan hasta el 70 % del valor: la cuota inicial mínima es del 30 %. La cuota mensual no debería pasar del 30 % de los ingresos del hogar. El plazo va de 5 a 20 años.', 'guia_compra.pdf'),
    ('compra',     'Los gastos de cierre (notaría, registro y beneficencia) son entre el 1,5 % y el 2 % del precio. La comisión del 3 % la paga el vendedor.', 'guia_compra.pdf'),
    ('compra',     'Los precios admiten una negociación de hasta el 5 %. Un apartamento reservado tiene una oferta en curso y no recibe ofertas.', 'guia_compra.pdf'),
    ('edificio',   'Edificio Los Almendros (SG-101): mudanzas de lunes a sábado de 8:00 a 17:00 avisando con tres días, nunca domingos ni festivos. Silencio de 22:00 a 6:00.', 'reglamento_los_almendros.pdf'),
    ('edificio',   'Edificio Los Almendros (SG-101): hasta dos mascotas, perros con traílla en zonas comunes. La terraza con asador cuesta 50.000 pesos por evento.', 'reglamento_los_almendros.pdf');
