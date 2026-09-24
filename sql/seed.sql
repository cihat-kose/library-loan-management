-- Demonstration data only; synthetic ISBNs and fictional borrower records.
-- Legger inn eksempeldata i "bok"
INSERT INTO `bok` (`ISBN`, `Tittel`, `Forfatter`, `Forlag`, `UtgittÅr`, `AntallSider`)
VALUES ('9788205342291', 'Forvandlingen', 'Franz Kafka', 'Gyldendal', 1915, 88),
       ('9000000000001', 'Sult', 'Knut Hamsun', 'Gyldendal', 1890, 200),
       ('9000000000002', 'Et dukkehjem', 'Henrik Ibsen', 'Aschehoug', 1879, 120),
       ('9000000000003', 'Kürk Mantolu Madonna', 'Sabahattin Ali', 'YKY', 1943, 160),
       ('9000000000004', 'Kar', 'Orhan Pamuk', 'İletişim', 2002, 460),
       ('9000000000005', 'Suç og Ceza', 'Fyodor Dostoyevski', 'Eksmo', 1866, 545),
       ('9000000000006', 'Savaş og Barış', 'Lev Tolstoy', 'Penguin', 1869, 1225),
       ('9000000000007', 'Pride and Prejudice', 'Jane Austen', 'T. Egerton', 1813, 279),
       ('9000000000008', 'One Hundred Years of Solitude', 'Gabriel García Márquez', 'Harper & Row', 1967, 417),
       ('9000000000009', 'Les Misérables', 'Victor Hugo', 'A. Lacroix', 1862, 1232);

-- Legger inn eksempeldata i "eksemplar"
INSERT INTO `eksemplar` (`ISBN`, `EksNr`)
VALUES ('9788205342291', 1),
       ('9000000000001', 1),
       ('9000000000002', 1),
       ('9000000000003', 1),
       ('9000000000004', 1),
       ('9000000000005', 1),
       ('9000000000006', 1),
       ('9000000000007', 1),
       ('9000000000008', 1),
       ('9000000000009', 1);

-- Legger inn eksempeldata i "låner"
INSERT INTO `låner` (`Fornavn`, `Etternavn`, `Adresse`)
VALUES ('Vincent', 'van Gogh', 'Zundert'),
       ('Sabahattin', 'Ali', 'Edirne'),
       ('Edvard', 'Munch', 'Oslo'),
       ('Harriet', 'Backer', 'Holmestrand'),
       ('Pablo', 'Picasso', 'Málaga');

-- Registrerer ett eksempelutlån (ikke levert ennå)
INSERT INTO `utlån` (`ISBN`, `EksNr`, `LNr`, `Utlånsdato`, `Levert`)
VALUES ('9788205342291', 1, 2, '2025-10-29', 0);

