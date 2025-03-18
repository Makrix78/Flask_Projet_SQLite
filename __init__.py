from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

# Fonction pour vérifier si l'utilisateur est un administrateur
def est_admin():
    return session.get('role') == 'admin'

# Fonction pour connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route pour la page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route d'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Rechercher l'utilisateur dans la base de données
        cursor.execute("SELECT * FROM utilisateurs WHERE username = ? AND password = ?", (username, password))
        utilisateur = cursor.fetchone()
        conn.close()

        if utilisateur:
            session['authentifie'] = True
            session['role'] = utilisateur['role']
            session['user_id'] = utilisateur['id']
            return redirect(url_for('accueil'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

# Route pour la déconnexion
@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

# Route pour l'enregistrement d'un livre (admin)
@app.route('/enregistrer_livre', methods=['GET', 'POST'])
def enregistrer_livre():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        annee_publication = request.form['annee_publication']
        quantite = request.form['quantite']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                       (titre, auteur, annee_publication, quantite))
        conn.commit()
        conn.close()

        return redirect(url_for('liste_livres'))

    return render_template('formulaire_enregistrement_livre.html')

# Route pour supprimer un livre (admin)
@app.route('/supprimer_livre/<int:id>', methods=['POST'])
def supprimer_livre(id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('authentification'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM livres WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('liste_livres'))

# Route pour afficher la liste des livres disponibles
@app.route('/liste_livres')
def liste_livres():
    if not est_authentifie():
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


# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:id>', methods=['POST'])
def emprunter_livre(id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si le livre est disponible
    cursor.execute("SELECT quantite FROM livres WHERE id = ?", (id,))
    livre = cursor.fetchone()

    if livre and livre['quantite'] > 0:
        # Mettre à jour la quantité disponible
        cursor.execute("UPDATE livres SET quantite = quantite - 1 WHERE id = ?", (id,))
        conn.commit()

        # Ajouter un enregistrement dans la table des emprunts
        cursor.execute("INSERT INTO emprunts (user_id, livre_id) VALUES (?, ?)", (session['user_id'], id))
        conn.commit()

        conn.close()
        return redirect(url_for('liste_livres'))

    conn.close()
    return "<h2>Le livre est actuellement indisponible.</h2>"

# Route pour rechercher un livre
@app.route('/rechercher_livre', methods=['GET', 'POST'])
def rechercher_livre():
    if request.method == 'POST':
        recherche = request.form['recherche']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?",
                       ('%' + recherche + '%', '%' + recherche + '%'))
        livres = cursor.fetchall()
        conn.close()
        return render_template('liste_livres.html', livres=livres)

    return render_template('rechercher_livre.html')

# Route pour voir les emprunts de l'utilisateur
@app.route('/mes_emprunts')
def mes_emprunts():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT livres.titre, livres.auteur FROM emprunts "
                   "JOIN livres ON emprunts.livre_id = livres.id "
                   "WHERE emprunts.user_id = ?", (session['user_id'],))
    emprunts = cursor.fetchall()
    conn.close()

    return render_template('mes_emprunts.html', emprunts=emprunts)

# API pour obtenir la liste des livres
@app.route('/api/livres', methods=['GET'])
def api_livres():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres WHERE quantite > 0")
    livres = cursor.fetchall()
    conn.close()

    return jsonify([dict(livre) for livre in livres])

if __name__ == "__main__":
    app.run(debug=True)
