CREATE TABLE Livres (
    ID_livre INTEGER PRIMARY KEY AUTOINCREMENT,
    Titre VARCHAR(255) NOT NULL,
    Auteur VARCHAR(255) NOT NULL,
    Annee_publication INT NOT NULL,
    Quantite INT NOT NULL CHECK (Quantite >= 0)
);

CREATE TABLE Utilisateurs (
    ID_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom VARCHAR(255) NOT NULL,
    Prenom VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Mot_de_passe VARCHAR(255) NOT NULL,  -- Ajout du champ mot de passe
    Role VARCHAR(50) DEFAULT 'user',     -- Ajout d'un rôle (admin ou user)
    Date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Emprunts (
    ID_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_utilisateur INTEGER NOT NULL,
    ID_livre INTEGER NOT NULL,
    Date_emprunt DATE DEFAULT CURRENT_DATE,
    Date_retour_prevue DATE NOT NULL,
    Date_retour_effective DATE,
    FOREIGN KEY (ID_utilisateur) REFERENCES Utilisateurs(ID_utilisateur) ON DELETE CASCADE,
    FOREIGN KEY (ID_livre) REFERENCES Livres(ID_livre) ON DELETE CASCADE
);
