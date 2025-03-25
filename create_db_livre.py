import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Ajouter un utilisateur adminn
cur.execute("""
INSERT INTO Utilisateurs (Nom, Prenom, Email, Mot_de_passe, Role)
VALUES (?, ?, ?, ?, ?)
""", ('Admin', 'Super', 'admin@biblio.com', 'password', 'admin'))

# Générer 500 livres
for i in range(1, 501):
    titre = f"Livre {i}"
    auteur = f"Auteur {i}"
    annee = 2000 + (i % 24)
    quantite = (i % 10) + 1

    cur.execute(
        "INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)",
        (titre, auteur, annee, quantite)
    )

connection.commit()
connection.close()
