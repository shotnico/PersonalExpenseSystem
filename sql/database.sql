PRAGMA foreign_keys = ON;

CREATE TABLE categorie (
    id_categoria INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(trim(nome)) > 0)
);

CREATE TABLE spese (
    id_spesa INTEGER PRIMARY KEY,
    data TEXT NOT NULL CHECK (date(data) IS NOT NULL AND date(data) = data),
    importo REAL NOT NULL CHECK (importo > 0),
    id_categoria INTEGER NOT NULL,
    descrizione TEXT,
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria) ON DELETE RESTRICT
);

CREATE TABLE budget (
    id_budget INTEGER PRIMARY KEY,
    mese TEXT NOT NULL CHECK (
        mese GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        AND substr(mese, 6, 2) BETWEEN '01' AND '12'
    ),
    id_categoria INTEGER NOT NULL,
    importo REAL NOT NULL CHECK (importo > 0),
    UNIQUE (mese, id_categoria),
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria) ON DELETE RESTRICT
);

INSERT INTO categorie (nome) VALUES
    ('Alimentari'),
    ('Trasporti'),
    ('Casa'),
    ('Svago'),
    ('Salute'),
    ('Regali');

INSERT INTO spese (data, importo, id_categoria, descrizione) VALUES
    ('2025-01-03', 85.40, 1, 'Spesa al supermercato'),
    ('2025-01-15', 25.00, 1, 'Pranzo'),
    ('2025-01-17', 118.00, 1, 'Scorte per la dispensa'),
    ('2025-01-05', 60.00, 2, 'Carburante'),
    ('2025-01-20', 35.00, 2, 'Abbonamento autobus'),
    ('2025-01-08', 450.00, 3, 'Affitto quota'),
    ('2025-01-25', 40.00, 4, 'Cinema e cena'),
    ('2025-02-02', 70.30, 1, 'Frutta e verdura'),
    ('2025-02-04', 25.00, 2, 'Parcheggio'),
    ('2025-02-12', 18.50, 5, 'Farmacia'),
    ('2025-02-14', 55.00, 4, NULL);

INSERT INTO budget (mese, id_categoria, importo) VALUES
    ('2025-01', 1, 300.00),
    ('2025-01', 2, 150.00),
    ('2025-01', 4, 50.00),
    ('2025-02', 1, 250.00),
    ('2025-02', 4, 50.00);


-- categoria già presente
-- INSERT INTO categorie (nome) VALUES ('Alimentari');
-- importo negativo
-- INSERT INTO spese (data, importo, id_categoria) VALUES ('2025-01-01', -5, 1);
-- categoria inesistente
-- INSERT INTO spese (data, importo, id_categoria) VALUES ('2025-01-01', 10, 99);

-- totale per categoria
SELECT c.nome, ROUND(SUM(s.importo), 2) AS totale
FROM categorie c
JOIN spese s ON s.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nome
ORDER BY totale DESC;

-- confronto con il budget
SELECT b.mese, c.nome, b.importo,
    ROUND(COALESCE(SUM(s.importo), 0), 2) AS speso
FROM budget b
JOIN categorie c ON c.id_categoria = b.id_categoria
LEFT JOIN spese s ON s.id_categoria = b.id_categoria
    AND substr(s.data, 1, 7) = b.mese
GROUP BY b.mese, c.nome, b.importo
ORDER BY b.mese, c.nome;

-- elenco spese
SELECT s.data, c.nome, s.importo, COALESCE(s.descrizione, '') AS descrizione
FROM spese s
JOIN categorie c ON c.id_categoria = s.id_categoria
ORDER BY s.data, s.id_spesa;
