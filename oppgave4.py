#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oppgave 4 – Python og MySQL Connector for databasen ga_bibliotek

Mål
- Koble til MySQL databasen ga_bibliotek
- Kjøres 12 eksempelspørringer
- Skrive ut resultater pent med kolonnenavn
- Samtidig lagre hele utskriften til filen oppgave4_rapor.txt

Bruk
  python oppgave4.py --host 127.0.0.1 --port 3306 --user root --password ***** --database ga_bibliotek

Miljøvariabler kan også brukes for HOST, PORT, USER, PASSWORD og DATABASE.
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional

# Forsøk å importere MySQL Connector
try:
    import mysql.connector
except ImportError:
    print("Pakke mysql-connector-python mangler. Kjør: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def parse_args():
    """Leser inn kommandolinjeflagg på norsk."""
    parser = argparse.ArgumentParser(
        description="Oppgave 4 – Python og MySQL for ga_bibliotek"
    )
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"),
                        help="Vert eller IP for MySQL tjeneren")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "3306")),
                        help="Port for MySQL tjeneren")
    parser.add_argument("--user", default=os.getenv("USER", "root"),
                        help="Brukernavn for MySQL")
    parser.add_argument("--password", default=os.getenv("PASSWORD", ""),
                        help="Passord for MySQL brukeren")
    parser.add_argument("--database", default=os.getenv("DATABASE", "ga_bibliotek"),
                        help="Navn på databasen som skal brukes")
    return parser.parse_args()


def connect_db(host: str, port: int, user: str, password: str, database: str):
    """Oppretter tilkobling og returnerer connection objektet."""
    try:
        conn = mysql.connector.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Tilkoblingsfeil: {err}", file=sys.stderr)
        sys.exit(1)


def run_query(conn, sql: str, params: Optional[Tuple] = None) -> Tuple[List[str], List[Tuple]]:
    """Kjører en spørring og returnerer kolonnenavn og rader."""
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    colnames = [d[0] for d in cur.description] if cur.description else []
    cur.close()
    return colnames, rows


def format_table(title: str, columns: List[str], rows: List[Tuple]) -> List[str]:
    """Formaterer en tabell som tekstlinjer slik at den kan skrives både til skjerm og til fil."""
    out: List[str] = []
    out.append("=" * 80)
    out.append(title)
    out.append("=" * 80)
    if not rows:
        out.append("(Ingen rader)")
        return out

    widths = [len(col) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    header = " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
    out.append(header)
    out.append("-" * len(header))
    for row in rows:
        out.append(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))
    out.append("")  # tom linje til slutt
    return out


def queries() -> List[Tuple[str, str]]:
    return [
        ("1) Alle bøker publisert etter år 2000",
         "SELECT ISBN, Tittel, Forfatter, UtgittÅr FROM bok WHERE UtgittÅr > 2000 ORDER BY UtgittÅr DESC, Tittel"),
        ("2) Forfatter og tittel på alle bøker (alfabetisk)",
         "SELECT Forfatter, Tittel FROM bok ORDER BY Forfatter, Tittel"),
        ("3) Alle bøker med mer enn 300 sider",
         "SELECT ISBN, Tittel, AntallSider FROM bok WHERE AntallSider > 300 ORDER BY AntallSider DESC"),
        ("4) Alle utlån med låner og boktittel",
         """SELECT u.UtlånsNr, u.Utlånsdato, l.Fornavn, l.Etternavn, b.Tittel
            FROM utlån u
            JOIN låner l     ON l.LNr = u.LNr
            JOIN eksemplar e ON e.ISBN = u.ISBN AND e.EksNr = u.EksNr
            JOIN bok b       ON b.ISBN = e.ISBN
            ORDER BY u.Utlånsdato DESC, u.UtlånsNr DESC"""),
        ("5) Antall eksemplarer per bok",
         """SELECT b.ISBN, b.Tittel, COUNT(e.EksNr) AS AntallEksemplarer
            FROM bok b
            LEFT JOIN eksemplar e ON e.ISBN = b.ISBN
            GROUP BY b.ISBN, b.Tittel
            ORDER BY AntallEksemplarer DESC, b.Tittel"""),
        ("6) Antall utlån per låner også de uten utlån",
         """SELECT l.LNr, l.Fornavn, l.Etternavn, COUNT(u.UtlånsNr) AS AntallUtlån
            FROM låner l
            LEFT JOIN utlån u ON u.LNr = l.LNr
            GROUP BY l.LNr, l.Fornavn, l.Etternavn
            ORDER BY AntallUtlån DESC, l.Etternavn, l.Fornavn"""),
        ("7) Antall utlån per bok",
         """SELECT b.ISBN, b.Tittel, COUNT(u.UtlånsNr) AS AntallUtlån
            FROM bok b
            LEFT JOIN eksemplar e ON e.ISBN = b.ISBN
            LEFT JOIN utlån u ON u.ISBN = e.ISBN AND u.EksNr = e.EksNr
            GROUP BY b.ISBN, b.Tittel
            ORDER BY AntallUtlån DESC, b.Tittel"""),
        ("8) Utlån som ikke er levert",
         "SELECT UtlånsNr, ISBN, EksNr, LNr, Utlånsdato FROM utlån WHERE Levert = 0 ORDER BY Utlånsdato DESC"),
        ("9) Lånere og deres siste utlån hvis det finnes",
         """SELECT l.LNr, l.Fornavn, l.Etternavn, MAX(u.Utlånsdato) AS SisteUtlån
            FROM låner l
            LEFT JOIN utlån u ON u.LNr = l.LNr
            GROUP BY l.LNr, l.Fornavn, l.Etternavn
            ORDER BY SisteUtlån DESC"""),
        ("10) Bøker utgitt på 1800 tallet tittel og år",
         "SELECT Tittel, UtgittÅr FROM bok WHERE UtgittÅr BETWEEN 1800 AND 1899 ORDER BY UtgittÅr, Tittel"),
        ("11) 400 sider eller mer og nyere enn 1950",
         "SELECT Tittel, AntallSider, UtgittÅr FROM bok WHERE AntallSider >= 400 AND UtgittÅr >= 1950 ORDER BY UtgittÅr DESC, AntallSider DESC"),
        ("12) Lånere uten aktive utlån Levert lik 0 finnes ikke",
         """SELECT l.LNr, l.Fornavn, l.Etternavn
            FROM låner l
            LEFT JOIN utlån u ON u.LNr = l.LNr AND u.Levert = 0
            WHERE u.UtlånsNr IS NULL
            ORDER BY l.Etternavn, l.Fornavn"""),
    ]


def main():
    """Hovedløp – kjør alle spørringer og skriv både til skjerm og til rapportfil."""
    args = parse_args()
    conn = connect_db(args.host, args.port, args.user, args.password, args.database)

    # Åpner rapportfil i skrivemodus hver gang scriptet kjøres
    with open("oppgave4_rapor.txt", "w", encoding="utf-8") as rap:
        try:
            for title, sql in queries():
                cols, rows = run_query(conn, sql)
                lines = format_table(title, cols, rows)

                # Skriv til skjerm
                for line in lines:
                    print(line)

                # Skriv til fil
                for line in lines:
                    rap.write(line + "\n")

        finally:
            conn.close()


if __name__ == "__main__":
    main()
