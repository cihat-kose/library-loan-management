# 📚 ga_bibliotek – README (Oppgave 2)

## 🔍 Oversikt
Denne databasen modellerer et lite bibliotek som holder orden på **bøker**, **fysiske eksemplarer**, **lånere** og **utlån**.  
Løsningen består av fire tabeller: `bok`, `eksemplar`, `låner` og `utlån`.

- Alle relasjoner er opprettet med **fremmednøkler** for å ivareta referanseintegritet.
- Databasen bruker **utf8mb4** som tegnsett og **InnoDB** som lagringsmotor for å støtte internasjonale tegn og stabile relasjoner.

---

## 📄 Tabellforklaringer

### 📘 bok
Inneholder informasjon om hver bok i biblioteket.

| Felt         | Beskrivelse                    |
|--------------|---------------------------------|
| ISBN (PK)    | Unik identifikator for hver bok |
| Tittel       | Navnet på boken                |
| Forfatter    | Forfatterens navn              |
| Forlag       | Utgiver                        |
| UtgittÅr     | Publiseringsår                 |
| AntallSider  | Antall sider i boken           |

> **Begrunnelse:** ISBN er en naturlig primærnøkkel. Øvrige felt er obligatoriske for en komplett katalog.

---

### 📗 eksemplar
Representerer hvert fysisk eksemplar av en bok.

| Felt     | Beskrivelse                         |
|----------|--------------------------------------|
| ISBN     | Refererer til `bok.ISBN`            |
| EksNr    | Nummer på eksemplaret               |
| PK       | Kombinasjon av `ISBN` og `EksNr`    |

> **Begrunnelse:** Kombinasjonen av ISBN og EksNr gjør hvert eksemplar unikt.

---

### 👤 låner
Inneholder informasjon om personer som låner bøker.

| Felt          | Beskrivelse                            |
|---------------|-----------------------------------------|
| LNr (PK)      | Unik identifikator for hver låner      |
| Fornavn       | Lånerens fornavn                       |
| Etternavn     | Lånerens etternavn                     |
| Adresse       | Lånerens adresse                       |

> **Begrunnelse:** Automatisk økende ID er hensiktsmessig. Navn og adresse kreves for oppfølging.

---

### 🔄 utlån
Registrerer hvert utlån av en bok.

| Felt         | Beskrivelse                               |
|--------------|--------------------------------------------|
| UtlånsNr (PK)| Unik ID for utlånet                        |
| ISBN, EksNr  | Refererer til `eksemplar`                 |
| LNr          | Refererer til `låner`                     |
| Utlånsdato   | Dato utlånet ble registrert               |
| Levert       | 0 = ikke levert, 1 = levert               |

> **Begrunnelse:** Kobler sammen spesifikke eksemplarer med lånere og registrerer status.

---

## 🔗 Relasjoner og Referanseintegritet
- `eksemplar.ISBN` → `bok.ISBN` (**ON UPDATE CASCADE, ON DELETE RESTRICT**)
- `utlån.LNr` → `låner.LNr`
- `utlån (ISBN, EksNr)` → `eksemplar (ISBN, EksNr)`

> Dette sikrer at utlån kun skjer for eksisterende bøker, eksemplarer og lånere. Sletting av bøker/lånere med utlån hindres.

---

## 📐 Normalisering

Databasen er normalisert til **tredje normalform (3NF)**:

1. **1NF:** Alle felt har atomære verdier, ingen gjentakelser.
2. **2NF:** Ingen felt er delvis avhengige av sammensatte nøkler.
3. **3NF:** Ingen transitive avhengigheter – hver tabell beskriver ett entydig tema.

---

## 🔧 Datatyper og Constraints

- `VARCHAR` for tekst  
- `INT` for numeriske verdier  
- `DATE` for datoer  
- `TINYINT` for boolske verdier (`Levert`)  
- `NOT NULL` på påkrevde felt  
- `CHECK (Levert IN (0,1))` sikrer gyldige statusverdier  

---

## 🛡️ Hvordan databasen sikrer gyldige data

- Fremmednøkler hindrer ugyldige referanser  
- `NOT NULL` hindrer tomme verdier i viktige felt  
- `CHECK` sikrer at `Levert` kun er 0 eller 1  
- Bruk av **InnoDB** støtter transaksjoner for konsistens  

---

## 🗂️ Databaseskjema

Skjemaet nedenfor illustrerer relasjonene mellom tabellene og viser hvilke kolonner som er:

- **Primærnøkler (PK)**
- **Fremmednøkler (FK)**

> En bok (`bok`) kan ha flere eksemplarer (`eksemplar`).  
> Hver utlån (`utlån`) er knyttet til et spesifikt eksemplar og én låner (`låner`).

![Databaseskjema](oppgave2_skjema.png)