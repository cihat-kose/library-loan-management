#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oppgave 4 – Python + MySQL Connector

Formål:
- Koble til databasen ga_bibliotek
- Utføre tolv SQL-spørringer (fra Oppgave 3)
- Skrive resultatene pent formatert til oppgave4_rapor.txt
"""

import os
import sys
import argparse
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------------------------
# Oppretter databaseforbindelse
# ---------------------------------------------------------------------------
def connect_to_database():
    parser = argparse.ArgumentParser(description="Koble til MySQL-database")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 3306)))
    parser.add_argument("--user", default=os.getenv("USER", "root"))
    parser.add_argument("--password", default=os.getenv("PASSWORD", ""))
    parser.add_argument("--database", default=os.getenv("DATABASE", "ga_bibliotek"))
    args = parser.parse_args()

    try:
        conn = mysql.connector.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database
        )
        return conn
    except Error as err:
        print(f"Tilkoblingsfeil: {err}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Kjøres for SELECT-spørringer og formaterer resultatene pent
# ---------------------------------------------------------------------------
def run_query(conn, query: str, title: str, outfile):
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]

    # Skriv overskrift
    outfile.write("=" * 80 + "\n")
    outfile.write(f"{title}\n")
    outfile.write("=" * 80 + "\n")

    # Ingen rader
    if not rows:
        outfile.write("(ingen data)\n\n")
        cursor.close()
        return

    # Kolonnavn
    col_line = " | ".join(cols)
    outfile.write(col_line + "\n")
    outfile.write("-" * len(col_line) + "\n")

    # Rader
    for r in rows:
        outfile.write(" | ".join(str(x) for x in r) + "\n")
    outfile.write("\n")

    cursor.close()

# ---------------------------------------------------------------------------
# Hovedprogram
# ---------------------------------------------------------------------------
def main():
    conn = connect_to_database()

    queries = [
        # 1)
        ("1) Alle bøker publisert etter år 2000",
         "SELECT ISBN, Tittel, Forfatter, UtgittÅr "
         "FROM bok WHERE UtgittÅr > 2000 "
         "ORDER BY UtgittÅr;"),

        # 2)
        ("2) Forfatter og tittel på alle bøker (alfabetisk)",
         "SELECT Forfatter, Tittel FROM bok ORDER BY Forfatter, Tittel;"),

        # 3)
        ("3) Alle bøker med mer enn 300 sider",
         "SELECT ISBN, Tittel, AntallSider FROM bok WHERE AntallSider > 300;"),

        # 4)
        ("4) Alle utlån med låner og boktittel",
         "SELECT u.UtlånsNr, u.Utlånsdato, l.Fornavn, l.Etternavn, b.Tittel "
         "FROM utlån u "
         "JOIN låner l ON u.LNr = l.LNr "
         "JOIN bok b ON b.ISBN = u.ISBN;"),

        # 5)
        ("5) Antall eksemplarer per bok",
         "SELECT b.ISBN, b.Tittel, COUNT(e.EksNr) AS AntallEksemplarer "
         "FROM bok b LEFT JOIN eksemplar e ON b.ISBN = e.ISBN "
         "GROUP BY b.ISBN, b.Tittel;"),

        # 6)
        ("6) Antall utlån per låner også de uten utlån",
         "SELECT l.LNr, l.Fornavn, l.Etternavn, COUNT(u.UtlånsNr) AS AntallUtlån "
         "FROM låner l LEFT JOIN utlån u ON l.LNr = u.LNr "
         "GROUP BY l.LNr, l.Fornavn, l.Etternavn;"),

        # 7)
        ("7) Antall utlån per bok",
         "SELECT b.ISBN, b.Tittel, COUNT(u.UtlånsNr) AS AntallUtlån "
         "FROM bok b LEFT JOIN utlån u ON b.ISBN = u.ISBN "
         "GROUP BY b.ISBN, b.Tittel;"),

        # 8)
        ("8) Utlån som ikke er levert",
         "SELECT UtlånsNr, ISBN, EksNr, LNr, Utlånsdato "
         "FROM utlån WHERE Levert = 0;"),

        # 9)
        ("9) Lånere og deres siste utlån hvis det finnes",
         "SELECT l.LNr, l.Fornavn, l.Etternavn, MAX(u.Utlånsdato) AS SisteUtlån "
         "FROM låner l LEFT JOIN utlån u ON l.LNr = u.LNr "
         "GROUP BY l.LNr, l.Fornavn, l.Etternavn;"),

        # 10)
        ("10) Bøker utgitt på 1800 tallet tittel og år",
         "SELECT Tittel, UtgittÅr FROM bok "
         "WHERE UtgittÅr BETWEEN 1800 AND 1899;"),

        # 11)
        ("11) 400 sider eller mer og nyere enn 1950",
         "SELECT Tittel, AntallSider, UtgittÅr "
         "FROM bok WHERE AntallSider >= 400 AND UtgittÅr > 1950;"),

        # 12)
        ("12) Lånere uten aktive utlån Levert lik 0 finnes ikke",
         "SELECT l.LNr, l.Fornavn, l.Etternavn "
         "FROM låner l "
         "WHERE l.LNr NOT IN (SELECT LNr FROM utlån WHERE Levert = 0);"),
    ]

    with open("oppgave4_rapor.txt", "w", encoding="utf-8") as f:
        for title, q in queries:
            run_query(conn, q, title, f)

    conn.close()
    print("✅ Rapport ferdig generert: oppgave4_rapor.txt")

if __name__ == "__main__":
    main()
