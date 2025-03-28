from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def est_authentifie():
    return session.get('authentifie')

def est_admin():
    return session.get('role') == 'admin'

@app.route('/')
def accueil():
    return redirect(url_for('authentification'))

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')

        if not email or not mot_de_passe:
            return render_template('formulaire_authentification.html', error="Veuillez remplir tous les champs.")

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Utilisateurs WHERE Email = ? AND Mot_de_passe = ?", (email, mot_de_passe))
            utilisateur = cursor.fetchone()
            conn.close()

            if utilisateur:
                session['authentifie'] = True
                session['role'] = utilisateur[5]
                session['user_id'] = utilisateur[0]
                return redirect(url_for('liste_livres'))
            else:
                return render_template('formulaire_authentification.html', error="Identifiant ou mot de passe incorrect.")
        except Exception as e:
            return render_template('formulaire_authentification.html', error=f"Erreur : {e}")

    return render_template('formulaire_authentification.html', error=False)

@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('authentification'))

@app.route('/liste_livres')
def liste_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Livres WHERE Quantite > 0")
        livres = cursor.fetchall()
        conn.close()
        return render_template('liste_livres.html', livres=livres)
    except Exception as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur : {e}")

@app.route('/mes_emprunts')
def mes_emprunts():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Emprunts.ID_emprunt, Livres.Titre, Livres.Auteur, Emprunts.Date_emprunt, Emprunts.Date_retour_prevue, Emprunts.Date_retour_effective
            FROM Emprunts
            JOIN Livres ON Emprunts.ID_livre = Livres.ID_livre
            WHERE Emprunts.ID_utilisateur = ?
        """, (session['user_id'],))
        emprunts = cursor.fetchall()
        conn.close()
        return render_template('mes_emprunts.html', emprunts=emprunts)
    except Exception as e:
        return render_template('mes_emprunts.html', emprunts=[], message=f"Erreur : {e}")

@app.route('/retourner_livre/<int:emprunt_id>', methods=['POST'])
def retourner_livre(emprunt_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Récupérer l'ID du livre associé à l'emprunt
        cursor.execute("SELECT ID_livre FROM Emprunts WHERE ID_emprunt = ? AND ID_utilisateur = ?", (emprunt_id, session['user_id']))
        result = cursor.fetchone()

        if result:
            id_livre = result[0]
            cursor.execute("UPDATE Emprunts SET Date_retour_effective = ? WHERE ID_emprunt = ?", (datetime.now().date(), emprunt_id))
            cursor.execute("UPDATE Livres SET Quantite = Quantite + 1 WHERE ID_livre = ?", (id_livre,))
            conn.commit()

        conn.close()
        return redirect(url_for('mes_emprunts'))

    except Exception as e:
        print("Erreur retour livre :", e)
        return redirect(url_for('mes_emprunts'))

@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('accueil'))

    if request.method == 'POST':
        titre = request.form.get('titre')
        auteur = request.form.get('auteur')
        annee = request.form.get('annee')
        quantite = request.form.get('quantite')

        if not titre or not auteur or not annee or not quantite:
            return render_template('ajouter_livre.html', error="Veuillez remplir tous les champs.")

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Livres (Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?)",
                           (titre, auteur, annee, quantite))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_livres'))
        except Exception as e:
            return render_template('ajouter_livre.html', error=f"Erreur : {e}")

    return render_template('ajouter_livre.html')

@app.route('/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre(livre_id):
    if not est_authentifie() or not est_admin():
        return redirect(url_for('accueil'))
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Livres WHERE ID_livre = ?", (livre_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))
    except Exception as e:
        print("Erreur de suppression :", e)
        return redirect(url_for('liste_livres'))

@app.route('/formulaire_emprunt/<int:livre_id>', methods=['GET', 'POST'])
def formulaire_emprunt(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            cursor.execute("SELECT Quantite FROM Livres WHERE ID_livre = ?", (livre_id,))
            livre = cursor.fetchone()
            if livre and livre[0] > 0:
                cursor.execute("UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?", (livre_id,))
                cursor.execute("INSERT INTO Emprunts (ID_utilisateur, ID_livre, Date_retour_prevue) VALUES (?, ?, DATE('now', '+14 days'))",
                               (session['user_id'], livre_id))
                conn.commit()
            conn.close()
            return redirect(url_for('liste_livres'))
        except Exception as e:
            conn.close()
            return f"Erreur lors de l'emprunt : {e}", 500

    cursor.execute("SELECT * FROM Livres WHERE ID_livre = ?", (livre_id,))
    livre_info = cursor.fetchone()
    conn.close()

    if not livre_info:
        return "Livre non trouvé", 404

    return render_template("formulaire_emprunt.html", livre=livre_info)

@app.route('/api/emprunter_livre', methods=['POST'])
def api_emprunter_livre():
    data = request.get_json()
    if not data or 'user_id' not in data or 'livre_id' not in data:
        return jsonify({"success": False, "error": "Champs requis : user_id et livre_id"}), 400

    user_id = data['user_id']
    livre_id = data['livre_id']

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Quantite FROM Livres WHERE ID_livre = ?", (livre_id,))
        livre = cursor.fetchone()

        if livre and livre[0] > 0:
            cursor.execute("UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?", (livre_id,))
            cursor.execute("INSERT INTO Emprunts (ID_utilisateur, ID_livre, Date_retour_prevue) VALUES (?, ?, DATE('now', '+14 days'))",
                           (user_id, livre_id))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "message": "Livre emprunté avec succès."}), 200
        else:
            conn.close()
            return jsonify({"success": False, "error": "Livre non disponible."}), 400

    except Exception as e:
        print("Erreur API emprunt :", e)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
