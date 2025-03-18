from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

# Fonction pour vérifier le rôle de l'utilisateur (admin ou utilisateur)
def est_admin():
    return session.get('role') == 'admin'

@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route d'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, mot_de_passe))
        utilisateur = cursor.fetchone()
        conn.close()

        if utilisateur:
            session['authentifie'] = True
            session['role'] = utilisateur[5]  # Récupère le rôle (admin/utilisateur)
            session['user_id'] = utilisateur[0]  # Récupère l'ID de l'utilisateur
            return redirect(url_for('accueil'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

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

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                       (titre, auteur, annee_publication, quantite))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))

    return render_template('formulaire_enregistrement_livre.html')

# Route pour supprimer un livre
@app.route('/supprimer_livre/<int:livre_id>', methods=['GET', 'POST'])
def supprimer_livre(livre_id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_livres'))

# Route pour afficher la liste des livres
@app.route('/liste_livres')
def liste_livres():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres WHERE quantite > 0")  # Afficher uniquement les livres disponibles
    livres = cursor.fetchall()
    conn.close()
    return render_template('liste_livres.html', livres=livres)

# Route pour rechercher un livre par titre ou auteur
@app.route('/rechercher_livre', methods=['GET', 'POST'])
def rechercher_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        recherche = request.form['recherche']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?", ('%' + recherche + '%', '%' + recherche + '%'))
        livres = cursor.fetchall()
        conn.close()
        return render_template('liste_livres.html', livres=livres)

    return render_template('formulaire_recherche_livre.html')

# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:livre_id>', methods=['GET'])
def emprunter_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Vérifier la disponibilité du livre
    cursor.execute("SELECT quantite FROM livres WHERE id = ?", (livre_id,))
    livre = cursor.fetchone()
    if livre and livre[0] > 0:
        # Réduire la quantité de ce livre
        cursor.execute("UPDATE livres SET quantite = quantite - 1 WHERE id = ?", (livre_id,))
        # Ajouter l'emprunt dans la table des emprunts
        cursor.execute("INSERT INTO emprunts (utilisateur_id, livre_id, date_retour_prevu) VALUES (?, ?, datetime('now', '+14 days'))",
                       (session['user_id'], livre_id))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))
    else:
        conn.close()
        return "Désolé, ce livre n'est pas disponible en ce moment."

if __name__ == "__main__":
    app.run(debug=True)
