-- Run once in an empty database. Existing data is never dropped.
SET NAMES utf8mb4;

CREATE TABLE `bok`
(
    `ISBN`        VARCHAR(13) PRIMARY KEY,
    `Tittel`      VARCHAR(255) NOT NULL,
    `Forfatter`   VARCHAR(100) NOT NULL,
    `Forlag`      VARCHAR(100) NOT NULL,
    `UtgittÅr`    INT          NOT NULL,
    `AntallSider` INT          NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Oppretter tabellen "eksemplar" (hvert fysisk eksemplar av en bok)
CREATE TABLE `eksemplar`
(
    `ISBN`  VARCHAR(13) NOT NULL,
    `EksNr` INT         NOT NULL,
    PRIMARY KEY (`ISBN`, `EksNr`),
    CONSTRAINT `fk_eksemplar_bok`
        FOREIGN KEY (`ISBN`) REFERENCES `bok` (`ISBN`)
            ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Oppretter tabellen "låner" (personer som låner bøker)
CREATE TABLE `låner`
(
    `LNr`       INT AUTO_INCREMENT PRIMARY KEY,
    `Fornavn`   VARCHAR(100) NOT NULL,
    `Etternavn` VARCHAR(100) NOT NULL,
    `Adresse`   VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Oppretter tabellen "utlån" (registrerer utlån og leveringsstatus)
CREATE TABLE `utlån`
(
    `UtlånsNr`   INT AUTO_INCREMENT PRIMARY KEY,
    `ISBN`       VARCHAR(13) NOT NULL,
    `EksNr`      INT         NOT NULL,
    `LNr`        INT         NOT NULL,
    `Utlånsdato` DATE        NOT NULL,
    `Levert`     TINYINT     NOT NULL,
    CONSTRAINT `fk_utlån_eksemplar`
        FOREIGN KEY (`ISBN`, `EksNr`) REFERENCES `eksemplar` (`ISBN`, `EksNr`)
            ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT `fk_utlån_låner`
        FOREIGN KEY (`LNr`) REFERENCES `låner` (`LNr`)
            ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT `chk_utlån_levert` CHECK (`Levert` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ytelsesforbedrende indekser for hyppig brukte kolonner
CREATE INDEX idx_eksemplar_isbn ON eksemplar (ISBN);
CREATE INDEX idx_utlan_isbn_eksnr ON utlån (ISBN, EksNr);
CREATE INDEX idx_utlan_lnr ON utlån (LNr);
CREATE INDEX idx_bok_forfatter ON bok (Forfatter);
