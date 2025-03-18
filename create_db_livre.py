import sqlite3
import random
from faker import Faker

# Connexion à la base de données
connection = sqlite3.connect('database.db')

# Créer un générateur de livres fictifs
fake = Faker()

# Fonction pour insérer des livres
def insert_books(cur, num_books):
    for _ in range(num_books):
        titre = fake.sentence(nb_words=5)  # Générer un titre fictif
        auteur = fake.name()  # Générer un auteur fictif
        annee_publication = random.randint(1900, 2023)  # Générer une année de publication
        quantite = random.randint(1, 10)  # Générer une quantité disponible

        # Insérer dans la table livres
        cur.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                    (titre, auteur, annee_publication, quantite))

# Ajouter des utilisateurs s'ils n'existent pas déjà
cur = connection.cursor()

# Vérifier si l'utilisateur Admin existe déjà
cur.execute("SELECT * FROM utilisateurs WHERE email = 'admin@biblio.com'")
if not cur.fetchone():
    cur.execute("INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?, ?, ?, ?, ?)",
                ('Admin', 'Super', 'admin@biblio.com', 'password', 'admin'))

# Vérifier si l'utilisateur Dupont existe déjà
cur.execute("SELECT * FROM utilisateurs WHERE email = 'jean.dupont@email.com'")
if not cur.fetchone():
    cur.execute("INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, role) VALUES (?, ?, ?, ?, ?)",
                ('Dupont', 'Jean', 'jean.dupont@email.com', 'user123', 'utilisateur'))

# Insérer seulement 50 livres
insert_books(cur, 50)

# Sauvegarder les changements dans la base de données
connection.commit()

# Fermer la connexion
connection.close()

print("50 livres ont été insérés avec succès dans la base de données.")
