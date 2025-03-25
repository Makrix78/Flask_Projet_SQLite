import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Ajouter des livres
cur.execute("INSERT INTO Livres (ID_livre, Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?, ?)", (1, 'Emilie', 'Victor', 2024, 10))
cur.execute("INSERT INTO Livres (ID_livre, Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?, ?)", (2, 'Didier', 'Laurent', 2023, 5))

# Ajouter un utilisateur admin
cur.execute("""
INSERT INTO Utilisateurs (ID_utilisateur, Nom, Prenom, Email, Mot_de_passe, Role)
VALUES (?, ?, ?, ?, ?, ?)
""", (1, 'Admin', 'Super', 'admin@biblio.com', 'password', 'admin'))

connection.commit()
connection.close()
