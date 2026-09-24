"""SQLite database creation and connection management."""

from pathlib import Path
import os
import sqlite3


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS bok (
    ISBN TEXT PRIMARY KEY,
    Tittel TEXT NOT NULL,
    Forfatter TEXT NOT NULL,
    Forlag TEXT NOT NULL,
    UtgittÅr INTEGER NOT NULL,
    AntallSider INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS eksemplar (
    ISBN TEXT NOT NULL,
    EksNr INTEGER NOT NULL,
    PRIMARY KEY (ISBN, EksNr),
    FOREIGN KEY (ISBN) REFERENCES bok (ISBN)
);

CREATE TABLE IF NOT EXISTS låner (
    LNr INTEGER PRIMARY KEY AUTOINCREMENT,
    Fornavn TEXT NOT NULL,
    Etternavn TEXT NOT NULL,
    Adresse TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS utlån (
    UtlånsNr INTEGER PRIMARY KEY AUTOINCREMENT,
    ISBN TEXT NOT NULL,
    EksNr INTEGER NOT NULL,
    LNr INTEGER NOT NULL,
    Utlånsdato TEXT NOT NULL,
    Levert INTEGER NOT NULL CHECK (Levert IN (0, 1)),
    FOREIGN KEY (ISBN, EksNr) REFERENCES eksemplar (ISBN, EksNr),
    FOREIGN KEY (LNr) REFERENCES låner (LNr)
);

CREATE INDEX IF NOT EXISTS idx_eksemplar_isbn ON eksemplar (ISBN);
CREATE INDEX IF NOT EXISTS idx_utlan_isbn_eksnr ON utlån (ISBN, EksNr);
CREATE INDEX IF NOT EXISTS idx_utlan_lnr ON utlån (LNr);
CREATE INDEX IF NOT EXISTS idx_bok_forfatter ON bok (Forfatter);
"""

SEED = """
INSERT OR IGNORE INTO bok
    (ISBN, Tittel, Forfatter, Forlag, UtgittÅr, AntallSider)
VALUES
    ('9788205342291', 'Forvandlingen', 'Franz Kafka', 'Gyldendal', 1915, 88),
    ('9000000000001', 'Sult', 'Knut Hamsun', 'Gyldendal', 1890, 200),
    ('9000000000002', 'Et dukkehjem', 'Henrik Ibsen', 'Aschehoug', 1879, 120),
    ('9000000000003', 'Kürk Mantolu Madonna', 'Sabahattin Ali', 'YKY', 1943, 160),
    ('9000000000004', 'Kar', 'Orhan Pamuk', 'İletişim', 2002, 460),
    ('9000000000005', 'Suç og Ceza', 'Fyodor Dostoyevski', 'Eksmo', 1866, 545),
    ('9000000000006', 'Savaş og Barış', 'Lev Tolstoy', 'Penguin', 1869, 1225),
    ('9000000000007', 'Pride and Prejudice', 'Jane Austen', 'T. Egerton', 1813, 279),
    ('9000000000008', 'One Hundred Years of Solitude', 'Gabriel García Márquez', 'Harper & Row', 1967, 417),
    ('9000000000009', 'Les Misérables', 'Victor Hugo', 'A. Lacroix', 1862, 1232);

INSERT OR IGNORE INTO eksemplar (ISBN, EksNr)
SELECT ISBN, 1 FROM bok;

INSERT OR IGNORE INTO låner (LNr, Fornavn, Etternavn, Adresse)
VALUES
    (1, 'Vincent', 'van Gogh', 'Zundert'),
    (2, 'Sabahattin', 'Ali', 'Edirne'),
    (3, 'Edvard', 'Munch', 'Oslo'),
    (4, 'Harriet', 'Backer', 'Holmestrand'),
    (5, 'Pablo', 'Picasso', 'Málaga');

INSERT OR IGNORE INTO utlån (UtlånsNr, ISBN, EksNr, LNr, Utlånsdato, Levert)
VALUES (1, '9788205342291', 1, 2, '2025-10-29', 0);
"""


def database_path():
    configured = os.getenv("DB_PATH")
    if configured:
        return Path(configured).expanduser()
    return Path.cwd() / "library_loans.db"


def connect(path=None):
    db_path = Path(path).expanduser() if path else database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executescript(SEED)
    return conn
