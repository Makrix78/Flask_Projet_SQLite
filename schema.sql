DROP TABLE IF EXISTS Emprunts;
DROP TABLE IF EXISTS Utilisateurs;
DROP TABLE IF EXISTS Livres;

CREATE TABLE Livres (
    ID_livre INTEGER PRIMARY KEY AUTOINCREMENT,
    Titre VARCHAR(255),
    Auteur VARCHAR(255),
    Annee_publication INT,
    Quantite INT
);

CREATE TABLE Utilisateurs (
    ID_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom VARCHAR(255),
    Prenom VARCHAR(255),
    Email VARCHAR(255),
    Mot_de_passe VARCHAR(255),
    Role VARCHAR(50),
    Date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Emprunts (
    ID_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_utilisateur INTEGER,
    ID_livre INTEGER,
    Date_emprunt DATE DEFAULT (DATE('now')),
    Date_retour_prevue DATE,
    Date_retour_effective DATE,
    FOREIGN KEY (ID_utilisateur) REFERENCES Utilisateurs(ID_utilisateur),
    FOREIGN KEY (ID_livre) REFERENCES Livres(ID_livre)
);
