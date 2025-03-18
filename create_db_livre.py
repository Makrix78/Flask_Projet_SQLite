import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Ajouter des utilisateurs
cur.execute("INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?, ?, ?, ?, ?)",
            ('Admin', 'Super', 'admin@biblio.com', 'password', 'admin'))
cur.execute("INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?, ?, ?, ?, ?)",
            ('Dupont', 'Jean', 'jean.dupont@email.com', 'user123', 'utilisateur'))

# Ajouter des livres
cur.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
            ('1984', 'George Orwell', 1949, 5))
cur.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
            ('Le Petit Prince', 'Antoine de Saint-Exupéry', 1943, 3))

connection.commit()
connection.close()
