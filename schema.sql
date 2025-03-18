DROP TABLE IF EXISTS utilisateurs;
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'utilisateur')) NOT NULL
);

DROP TABLE IF EXISTS livres;
CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    annee_publication INTEGER NOT NULL,
    quantite INTEGER NOT NULL CHECK(quantite >= 0)
);

DROP TABLE IF EXISTS emprunts;
CREATE TABLE emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    livre_id INTEGER NOT NULL,
    date_emprunt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_retour_prevu TIMESTAMP NOT NULL,
    date_retour_effectif TIMESTAMP,
    FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY(livre_id) REFERENCES livres(id)
);
