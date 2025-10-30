# 📘 Arbeidskrav 2 – Databasebeskrivelse

Denne README-filen dokumenterer databasen `ga_bibliotek` slik den er definert i `oppgave1.sql`. Beskrivelsen oppsummerer strukturen, nøklene og constraint-ene som kreves i oppgavebeskrivelsen for Arbeidskrav 2.

## Tabellstrukturer

### `bok`
| Kolonne | Datatype | Constraint | Beskrivelse |
| --- | --- | --- | --- |
| `ISBN` | `VARCHAR(13)` | `PRIMARY KEY` | Unik identifikator for hver bok.【F:oppgave1.sql†L12-L19】 |
| `Tittel` | `VARCHAR(255)` | `NOT NULL` | Navn på boken.【F:oppgave1.sql†L12-L19】 |
| `Forfatter` | `VARCHAR(100)` | `NOT NULL` | Navn på forfatter.【F:oppgave1.sql†L12-L19】 |
| `Forlag` | `VARCHAR(100)` | `NOT NULL` | Utgiver av boken.【F:oppgave1.sql†L12-L19】 |
| `UtgittÅr` | `INT` | `NOT NULL` | Publiseringsår.【F:oppgave1.sql†L12-L19】 |
| `AntallSider` | `INT` | `NOT NULL` | Antall sider i boken.【F:oppgave1.sql†L12-L19】 |

### `eksemplar`
| Kolonne | Datatype | Constraint | Beskrivelse |
| --- | --- | --- | --- |
| `ISBN` | `VARCHAR(13)` | Del av `PRIMARY KEY`, `NOT NULL`, `FOREIGN KEY` til `bok.ISBN` | Hvilken bok eksemplaret tilhører.【F:oppgave1.sql†L22-L29】 |
| `EksNr` | `INT` | Del av `PRIMARY KEY`, `NOT NULL` | Løpenummer for eksemplaret.【F:oppgave1.sql†L22-L29】 |

### `låner`
| Kolonne | Datatype | Constraint | Beskrivelse |
| --- | --- | --- | --- |
| `LNr` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unik identifikator for hver låner.【F:oppgave1.sql†L32-L37】 |
| `Fornavn` | `VARCHAR(100)` | `NOT NULL` | Lånerens fornavn.【F:oppgave1.sql†L32-L37】 |
| `Etternavn` | `VARCHAR(100)` | `NOT NULL` | Lånerens etternavn.【F:oppgave1.sql†L32-L37】 |
| `Adresse` | `VARCHAR(255)` | `NOT NULL` | Postadresse til låneren.【F:oppgave1.sql†L32-L37】 |

### `utlån`
| Kolonne | Datatype | Constraint | Beskrivelse |
| --- | --- | --- | --- |
| `UtlånsNr` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unik identifikator for utlånet.【F:oppgave1.sql†L40-L54】 |
| `ISBN` | `VARCHAR(13)` | `NOT NULL`, del av `FOREIGN KEY` til `eksemplar` | Hvilken bok som lånes.【F:oppgave1.sql†L40-L54】 |
| `EksNr` | `INT` | `NOT NULL`, del av `FOREIGN KEY` til `eksemplar` | Hvilket eksemplar som lånes.【F:oppgave1.sql†L40-L54】 |
| `LNr` | `INT` | `NOT NULL`, `FOREIGN KEY` til `låner.LNr` | Hvem som låner boken.【F:oppgave1.sql†L40-L54】 |
| `Utlånsdato` | `DATE` | `NOT NULL` | Datoen utlånet starter.【F:oppgave1.sql†L40-L54】 |
| `Levert` | `TINYINT` | `NOT NULL`, `CHECK (Levert IN (0,1))` | Status for om eksemplaret er levert.【F:oppgave1.sql†L40-L54】 |

## Primærnøkler og fremmednøkler
- `bok.ISBN` er en naturlig primærnøkkel som identifiserer hver bok.【F:oppgave1.sql†L12-L19】
- `eksemplar` har en sammensatt primærnøkkel (`ISBN`, `EksNr`) slik at hvert fysiske eksemplar blir unikt. Fremmednøkkelen `fk_eksemplar_bok` binder eksemplaret til en gyldig bok og oppdaterer `ISBN` automatisk ved endringer.【F:oppgave1.sql†L22-L29】
- `låner.LNr` er autoinkrement, noe som gir hver låner en unik identitet uten manuell oppfølging.【F:oppgave1.sql†L32-L37】
- `utlån.UtlånsNr` er autoinkrement, mens fremmednøklene `fk_utlån_eksemplar` og `fk_utlån_låner` sikrer at hvert utlån peker til et eksisterende eksemplar og en eksisterende låner.【F:oppgave1.sql†L40-L54】

### Relasjoner
- Én rad i `bok` kan knyttes til flere rader i `eksemplar` via `fk_eksemplar_bok`, og gir en én-til-mange-relasjon for fysiske kopier.【F:oppgave1.sql†L22-L29】
- `utlån` kobler sammen låner og eksemplar og danner mange-til-én-relasjoner mot begge tabeller, slik at hvert utlån gjelder én låner og ett bestemt eksemplar.【F:oppgave1.sql†L40-L54】

## Constraints og dataintegritet
- `NOT NULL` på sentrale kolonner hindrer ufullstendige oppføringer i alle tabellene.【F:oppgave1.sql†L12-L54】
- `AUTO_INCREMENT` på `låner.LNr` og `utlån.UtlånsNr` genererer nye nøkler automatisk og forenkler registrering av nye rader.【F:oppgave1.sql†L32-L54】
- `CHECK (Levert IN (0,1))` i `utlån` begrenser statusfeltet til lovlige verdier og reflekterer kravene om 0/1-status i oppgaven.【F:oppgave1.sql†L40-L54】
- `ENGINE=InnoDB` brukes for alle tabellene for å få referanseintegritet og støtte for fremmednøkler.【F:oppgave1.sql†L12-L54】
- Databasen settes opp med `utf8mb4` og `utf8mb4_unicode_ci` slik at norske tegn og andre spesialtegn blir lagret korrekt.【F:oppgave1.sql†L4-L9】

## ER-diagram
![Databaseskjema](oppgave2_skjema.png)
