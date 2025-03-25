import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Ajouter des livres de test
cur.execute("INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)", 
            ('Emilie', 'Victor', 2024, 10))
cur.execute("INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)", 
            ('Didier', 'Laurent', 2023, 5))

# Ajouter un utilisateur admin
cur.execute("INSERT INTO Utilisateurs (Nom, Prenom, Email, Mot_de_passe, Role) VALUES (?, ?, ?, ?, ?)", 
            ('Admin', 'Super', 'admin@example.com', 'admin123', 'admin'))

connection.commit()
connection.close()
