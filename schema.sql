CREATE TABLE Livres (
    ID_livre INT PRIMARY KEY,
    Titre VARCHAR(255),
    Auteur VARCHAR(255),
    Annee_publication INT,
    Quantite INT
);

CREATE TABLE Utilisateurs (
    ID_utilisateur INT PRIMARY KEY,
    Nom VARCHAR(255),
    Prenom VARCHAR(255),
    Email VARCHAR(255),
    Date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Emprunts (
    ID_emprunt INT PRIMARY KEY,
    ID_utilisateur INT,
    ID_livre INT,
    Date_emprunt DATE,
    Date_retour_prevue DATE,
    Date_retour_effective DATE,
    FOREIGN KEY (ID_utilisateur) REFERENCES Utilisateurs(ID_utilisateur),
    FOREIGN KEY (ID_livre) REFERENCES Livres(ID_livre)
);
