# Database design

The application uses a self-contained SQLite database. The schema is created
idempotently by `library_loans/database.py` on the first connection.

```mermaid
erDiagram
    BOK {
        TEXT ISBN PK
        TEXT Tittel
        TEXT Forfatter
        TEXT Forlag
        INTEGER UtgittÅr
        INTEGER AntallSider
    }

    EKSEMPLAR {
        TEXT ISBN PK, FK
        INTEGER EksNr PK
    }

    LÅNER {
        INTEGER LNr PK
        TEXT Fornavn
        TEXT Etternavn
        TEXT Adresse
    }

    UTLÅN {
        INTEGER UtlånsNr PK
        TEXT ISBN FK
        INTEGER EksNr FK
        INTEGER LNr FK
        TEXT Utlånsdato
        INTEGER Levert
    }

    BOK ||--o{ EKSEMPLAR : "has physical copies"
    EKSEMPLAR ||--o{ UTLAN : "appears in loans"
    LÅNER ||--o{ UTLÅN : "creates"
```

`EKSEMPLAR` uses `(ISBN, EksNr)` as its composite primary key because a copy
number is unique only within a book. `UTLAN` references both columns so every
loan belongs to a real physical copy and a real borrower.
