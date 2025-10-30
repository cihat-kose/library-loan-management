#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oppgave 4 – Python + MySQL Connector (kravoppfyllelse A–F)

Funksjoner:
- connect_to_database()  [A]
- vis_alle_boker()       [B]
- sok_bok(sokeord)       [C]
- registrer_utlan(lnr, isbn, eksnr, utlansdato)  [D]
- lever_bok(utlansnr)    [E]
- vis_lanerhistorikk(lnr) [F]

Kjøring (eksempler):
  python oppgave4.py --vis-alle-boker
  python oppgave4.py --sok-bok "tolstoy"
  python oppgave4.py --registrer-utlan --lnr 2 --isbn 9788205342291 --eksnr 1 --dato 2025-10-31
  python oppgave4.py --lever-bok --utlansnr 3
  python oppgave4.py --lanerhistorikk --lnr 2
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional
import mysql.connector
from mysql.connector import Error

# ------------------------- [A] Tilkobling -------------------------
def connect_to_database():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 3306)))
    parser.add_argument("--user", default=os.getenv("USER", "root"))
    parser.add_argument("--password", default=os.getenv("PASSWORD", ""))
    parser.add_argument("--database", default=os.getenv("DATABASE", "ga_bibliotek"))
    args, _ = parser.parse_known_args()

    try:
        conn = mysql.connector.connect(
            host=args.host, port=args.port,
            user=args.user, password=args.password,
            database=args.database
        )
        return conn
    except Error as err:
        print(f"Tilkoblingsfeil: {err}", file=sys.stderr)
        sys.exit(1)

# ------------------------- Hjelpere -------------------------
def _print_rows(cols: List[str], rows: List[Tuple]):
    if not rows:
        print("(ingen data)")
        return
    header = " | ".join(cols)
    sep = "-" * len(header)
    print(header)
    print(sep)
    for r in rows:
        print(" | ".join(str(x) for x in r))

# ------------------------- [B] Vis alle bøker -------------------------
def vis_alle_boker(conn):
    cur = conn.cursor()
    cur.execute("SELECT ISBN, Tittel, Forfatter, Forlag, UtgittÅr, AntallSider FROM bok ORDER BY Tittel;")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    _print_rows(cols, rows)
    cur.close()

# ------------------------- [C] Søk etter bok -------------------------
def sok_bok(conn, sokeord: str):
    cur = conn.cursor()
    like = f"%{sokeord}%"
    cur.execute(
        "SELECT ISBN, Tittel, Forfatter, Forlag, UtgittÅr, AntallSider "
        "FROM bok WHERE Tittel LIKE %s OR Forfatter LIKE %s ORDER BY Forfatter, Tittel;",
        (like, like)
    )
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    _print_rows(cols, rows)
    cur.close()

# ------------------------- [D] Registrer nytt utlån -------------------------
def registrer_utlan(conn, lnr: int, isbn: str, eksnr: int, utlansdato: str):
    cur = conn.cursor()

    # 1) Finnes eksemplaret?
    cur.execute("SELECT 1 FROM eksemplar WHERE ISBN=%s AND EksNr=%s;", (isbn, eksnr))
    if cur.fetchone() is None:
        cur.close()
        print("❌ Eksemplaret finnes ikke.")
        return

    # 2) Allerede utlånt?
    cur.execute(
        "SELECT 1 FROM utlån WHERE ISBN=%s AND EksNr=%s AND Levert=0;",
        (isbn, eksnr)
    )
    if cur.fetchone():
        cur.close()
        print("❌ Eksemplaret er allerede utlånt (Levert=0).")
        return

    # 3) Registrer utlånet (Levert=0)
    try:
        cur.execute(
            "INSERT INTO utlån (ISBN, EksNr, LNr, Utlånsdato, Levert) "
            "VALUES (%s, %s, %s, %s, 0);",
            (isbn, eksnr, lnr, utlansdato)
        )
        conn.commit()
        print("✅ Utlån registrert.")
    except Error as e:
        conn.rollback()
        print(f"❌ Feil ved innsending: {e}")
    finally:
        cur.close()

# ------------------------- [E] Lever tilbake bok -------------------------
def lever_bok(conn, utlansnr: int):
    cur = conn.cursor()
    cur.execute("UPDATE utlån SET Levert=1 WHERE UtlånsNr=%s;", (utlansnr,))
    if cur.rowcount == 0:
        print("❌ Fant ikke utlånsnummeret.")
    else:
        conn.commit()
        print("✅ Markert som levert.")
    cur.close()

# ------------------------- [F] Vis lånerhistorikk -------------------------
def vis_lanerhistorikk(conn, lnr: int):
    cur = conn.cursor()
    # Lånerens info
    cur.execute("SELECT Fornavn, Etternavn, Adresse FROM låner WHERE LNr=%s;", (lnr,))
    info = cur.fetchone()
    if not info:
        print("❌ Låner finnes ikke.")
        cur.close()
        return
    print(f"Låner: {info[0]} {info[1]} – {info[2]}")

    # Alle utlån (aktive og returnerte) med bokinfo
    cur.execute(
        "SELECT u.UtlånsNr, b.Tittel, b.Forfatter, u.Utlånsdato, "
        "CASE WHEN u.Levert=0 THEN 'utlånt' ELSE 'levert' END AS Status "
        "FROM utlån u "
        "JOIN bok b ON b.ISBN = u.ISBN "
        "WHERE u.LNr=%s "
        "ORDER BY u.Utlånsdato DESC, u.UtlånsNr DESC;",
        (lnr,)
    )
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    _print_rows(cols, rows)
    cur.close()

# ------------------------- CLI -------------------------
def main():
    base = argparse.ArgumentParser()
    base.add_argument("--vis-alle-boker", action="store_true")
    base.add_argument("--sok-bok", dest="sok", type=str)
    base.add_argument("--registrer-utlan", action="store_true")
    base.add_argument("--lever-bok", action="store_true")
    base.add_argument("--lanerhistorikk", action="store_true")
    base.add_argument("--lnr", type=int)
    base.add_argument("--isbn", type=str)
    base.add_argument("--eksnr", type=int)
    base.add_argument("--dato", type=str)
    base.add_argument("--utlansnr", type=int)

    args = base.parse_args()
    conn = connect_to_database()

    try:
        if args.vis_alle_boker:
            vis_alle_boker(conn)
        if args.sok:
            sok_bok(conn, args.sok)
        if args.registrer_utlan:
            if args.lnr is None or args.isbn is None or args.eksnr is None or args.dato is None:
                print("❌ Mangler --lnr, --isbn, --eksnr eller --dato")
            else:
                registrer_utlan(conn, args.lnr, args.isbn, args.eksnr, args.dato)
        if args.lever_bok:
            if args.utlansnr is None:
                print("❌ Mangler --utlansnr")
            else:
                lever_bok(conn, args.utlansnr)
        if args.lanerhistorikk:
            if args.lnr is None:
                print("❌ Mangler --lnr")
            else:
                vis_lanerhistorikk(conn, args.lnr)
        if not any([args.vis_alle_boker, args.sok, args.registrer_utlan, args.lever_bok, args.lanerhistorikk]):
            print("Bruk --help for alternativer.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
