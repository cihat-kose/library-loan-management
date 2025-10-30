# Arbeidskrav 2 – Tema 2: Databasesystemer  
### Cihat Köse  

---

## 1. Introduksjon

Databasen **ga_bibliotek** er utviklet for å modellere et lite bibliotek som holder oversikt over bøker, eksemplarer, lånere og utlån.  
Strukturen bygger på prinsippene for relasjonsdatabaser og sikrer dataintegritet gjennom riktig bruk av primærnøkler, fremmednøkler og constraints.

---

## 2. Tabellstrukturer

### 2.1 bok
| Kolonne | Datatype | Beskrivelse | Constraint |
|----------|-----------|-------------|-------------|
| ISBN | VARCHAR(13) | Unik identifikator for boken | PRIMARY KEY |
| Tittel | VARCHAR(255) | Boktittel | NOT NULL |
| Forfatter | VARCHAR(100) | Forfatterens navn | NOT NULL |
| Forlag | VARCHAR(100) | Utgiver | NOT NULL |
| UtgittÅr | INT | Utgivelsesår | NOT NULL |
| AntallSider | INT | Antall sider i boken | NOT NULL |

**Begrunnelse:**  
Denne tabellen inneholder den grunnleggende bibliografiske informasjonen. ISBN fungerer som naturlig primærnøkkel.

---

### 2.2 eksemplar
| Kolonne | Datatype | Beskrivelse | Constraint |
|----------|-----------|-------------|-------------|
| ISBN | VARCHAR(13) | Refererer til `bok.ISBN` | FOREIGN KEY |
| EksNr | INT | Nummer for hvert eksemplar | PRIMARY KEY (kombinert) |

**Begrunnelse:**  
Kombinasjonen av ISBN og eksemplarnummer (EksNr) gjør hvert fysisk eksemplar unikt.

---

### 2.3 låner
| Kolonne | Datatype | Beskrivelse | Constraint |
|----------|-----------|-------------|-------------|
| LNr | INT | Unik identifikator for låner | PRIMARY KEY, AUTO_INCREMENT |
| Fornavn | VARCHAR(100) | Lånerens fornavn | NOT NULL |
| Etternavn | VARCHAR(100) | Lånerens etternavn | NOT NULL |
| Adresse | VARCHAR(255) | Lånerens adresse | NOT NULL |

**Begrunnelse:**  
Hver låner har et unikt LNr, og navn/adresse kreves for å kunne spore utlån.

---

### 2.4 utlån
| Kolonne | Datatype | Beskrivelse | Constraint |
|----------|-----------|-------------|-------------|
| UtlånsNr | INT | Unik identifikator for utlånet | PRIMARY KEY, AUTO_INCREMENT |
| ISBN | VARCHAR(13) | Bok som lånes | FOREIGN KEY → eksemplar.ISBN |
| EksNr | INT | Eksemplarnummer | FOREIGN KEY → eksemplar.EksNr |
| LNr | INT | Lånerens ID | FOREIGN KEY → låner.LNr |
| Utlånsdato | DATE | Dato utlånet ble registrert | NOT NULL |
| Levert | TINYINT | 0 = ikke levert, 1 = levert | CHECK (Levert IN (0,1)) |

**Begrunnelse:**  
Tabellen kobler sammen låner og bokeksemplar og registrerer status for utlånet.

---

## 3. Primærnøkler og Fremmednøkler

| Tabell | Primærnøkkel | Fremmednøkler |
|---------|----------------|----------------|
| bok | ISBN | – |
| eksemplar | (ISBN, EksNr) | ISBN → bok.ISBN |
| låner | LNr | – |
| utlån | UtlånsNr | LNr → låner.LNr<br> (ISBN, EksNr) → eksemplar(ISBN, EksNr) |

**Forklaring:**  
Fremmednøkler sikrer at utlån kun kan registreres for eksisterende bøker, eksemplarer og lånere.  
Dette ivaretar referanseintegritet i databasen.

---

## 4. Constraints og dataintegritet

| Constraint-type | Bruk | Formål |
|------------------|------|--------|
| PRIMARY KEY | Alle tabeller | Unik identifikasjon |
| FOREIGN KEY | eksemplar, utlån | Referanseintegritet |
| NOT NULL | Viktige felt | Hindrer manglende data |
| CHECK | utlån.Levert | Sikrer gyldige statusverdier |
| AUTO_INCREMENT | låner, utlån | Automatisk genererte ID-er |

---

## 5. Normalisering

Databasen er normalisert til **tredje normalform (3NF)**:
1. **1NF:** Alle attributter er atomære.  
2. **2NF:** Alle ikke-nøkkelfelt er fullt avhengige av primærnøkkelen.  
3. **3NF:** Ingen transitive avhengigheter – hver tabell beskriver kun ett konsept.

---

## 6. Relasjoner (oversikt)

- En bok (`bok`) kan ha flere eksemplarer (`eksemplar`).  
- Hvert eksemplar kan lånes ut flere ganger (`utlån`).  
- Hver utlån er knyttet til én låner (`låner`).  

Skjemaet nedenfor viser koblingene mellom tabellene:

![Databaseskjema](oppgave2_skjema.png)

---

## 7. Konklusjon

Databasen **ga_bibliotek** er strukturert og konsistent.  
Gjennom bruk av relasjoner, constraints og riktig normalisering ivaretas både dataintegritet og fleksibilitet i systemet.  
Strukturen støtter alle forespurte operasjoner som søk, registrering og historikk over utlån.

---
