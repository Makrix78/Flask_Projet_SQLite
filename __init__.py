from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    print("Vérification de l'authentification: ", session.get('authentifie'))
    return session.get('authentifie')

# Fonction pour vérifier si l'utilisateur est un admin
def est_admin():
    return session.get('role') == 'admin'

@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route d'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')

        # Vérification si les champs sont vides
        if not email or not mot_de_passe:
            return render_template('formulaire_authentification.html', error="Veuillez remplir tous les champs.")

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Recherche de l'utilisateur dans la base de données
            cursor.execute("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, mot_de_passe))
            utilisateur = cursor.fetchone()
            conn.close()

            # Debug : log l'utilisateur trouvé
            print("Utilisateur trouvé:", utilisateur)

            # Si l'utilisateur existe, on l'authentifie
            if utilisateur:
                session['authentifie'] = True
                session['role'] = utilisateur[5]  # Récupère le rôle (admin/utilisateur)
                session['user_id'] = utilisateur[0]  # Récupère l'ID de l'utilisateur
                return redirect(url_for('accueil'))
            else:
                return render_template('formulaire_authentification.html', error="Identifiant ou mot de passe incorrect.")

        except sqlite3.DatabaseError as e:
            print("Erreur de base de données:", e)
            return render_template('formulaire_authentification.html', error=f"Erreur de base de données : {e}")

        except Exception as e:
            print("Erreur serveur:", e)
            return render_template('formulaire_authentification.html', error=f"Erreur serveur : {e}")

    return render_template('formulaire_authentification.html', error=False)

# Route pour la déconnexion
@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

# Route pour l'enregistrement d'un livre
@app.route('/enregistrer_livre', methods=['GET', 'POST'])
def enregistrer_livre():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        annee_publication = request.form['annee_publication']
        quantite = request.form['quantite']

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                           (titre, auteur, annee_publication, quantite))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_livres'))

        except sqlite3.DatabaseError as e:
            print("Erreur de base de données lors de l'ajout du livre:", e)
            return f"<h2>Erreur de base de données : {e}</h2>"

    return render_template('formulaire_enregistrement_livre.html')

# Route pour afficher la liste des livres
@app.route('/liste_livres')
def liste_livres():
    # Vérifier si l'utilisateur est authentifié
    if not est_authentifie():
        print("Utilisateur non authentifié. Redirection vers la page d'authentification.")
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")  # Afficher uniquement les livres disponibles
        livres = cursor.fetchall()
        conn.close()

        # Vérifier si des livres sont trouvés
        if not livres:
            return "<h2>Aucun livre disponible.</h2>"

        return render_template('liste_livres.html', livres=livres)

    except sqlite3.DatabaseError as e:
        print("Erreur de base de données lors de l'affichage des livres:", e)
        return f"<h2>Erreur de base de données : {e}</h2>"

    except Exception as e:
        print("Erreur serveur:", e)
        return f"<h2>Erreur serveur : {e}</h2>"

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
