from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
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

            # Si l'utilisateur existe, on l'authentifie
            if utilisateur:
                session['authentifie'] = True
                session['role'] = utilisateur[5]  # Récupère le rôle (admin/utilisateur)
                session['user_id'] = utilisateur[0]  # Récupère l'ID de l'utilisateur
                return redirect(url_for('accueil'))
            else:
                return render_template('formulaire_authentification.html', error="Identifiant ou mot de passe incorrect.")

        except sqlite3.DatabaseError as e:
            return render_template('formulaire_authentification.html', error=f"Erreur de base de données : {e}")

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
            return f"<h2>Erreur de base de données : {e}</h2>"

    return render_template('formulaire_enregistrement_livre.html')

# Route pour supprimer un livre
@app.route('/supprimer_livre/<int:livre_id>', methods=['GET', 'POST'])
def supprimer_livre(livre_id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))

    except sqlite3.DatabaseError as e:
        return f"<h2>Erreur de base de données : {e}</h2>"

# Route pour afficher la liste des livres
@app.route('/liste_livres')
def liste_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")
        livres = cursor.fetchall()
        conn.close()

        if not livres:
            return "<h2>Aucun livre disponible.</h2>"

        return render_template('liste_livres.html', livres=livres)

    except sqlite3.DatabaseError as e:
        return f"<h2>Erreur de base de données : {e}</h2>"

    except Exception as e:
        return f"<h2>Erreur serveur : {e}</h2>"

# Route pour rechercher un livre par titre ou auteur
@app.route('/rechercher_livre', methods=['GET', 'POST'])
def rechercher_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        recherche = request.form['recherche']
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?", ('%' + recherche + '%', '%' + recherche + '%'))
            livres = cursor.fetchall()
            conn.close()
            return render_template('liste_livres.html', livres=livres)

        except sqlite3.DatabaseError as e:
            return f"<h2>Erreur de base de données : {e}</h2>"

    return render_template('formulaire_recherche_livre.html')

# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:livre_id>', methods=['GET'])
def emprunter_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT quantite FROM livres WHERE id = ?", (livre_id,))
        livre = cursor.fetchone()

        if livre and livre[0] > 0:
            cursor.execute("UPDATE livres SET quantite = quantite - 1 WHERE id = ?", (livre_id,))
            cursor.execute("INSERT INTO emprunts (utilisateur_id, livre_id, date_retour_prevu) VALUES (?, ?, datetime('now', '+14 days'))",
                           (session['user_id'], livre_id))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_livres'))
        else:
            conn.close()
            return "Désolé, ce livre n'est pas disponible en ce moment."

    except sqlite3.DatabaseError as e:
        return f"<h2>Erreur de base de données : {e}</h2>"

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
