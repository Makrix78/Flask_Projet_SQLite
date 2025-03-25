from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def est_authentifie():
    return session.get('authentifie')

def est_admin():
    return session.get('role') == 'admin'

@app.route('/')
def accueil():
    return render_template('accueil.html')

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
    return redirect(url_for('accueil'))

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

@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Quantite FROM Livres WHERE ID_livre = ?", (livre_id,))
        livre = cursor.fetchone()

        if livre and livre[0] > 0:
            cursor.execute("UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?", (livre_id,))
            cursor.execute(\"\"\"INSERT INTO Emprunts (ID_utilisateur, ID_livre, Date_retour_prevue)
                              VALUES (?, ?, DATE('now', '+14 days'))\"\"\", (session['user_id'], livre_id))
            conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))
    except Exception as e:
        print(\"Erreur emprunt:\", e)
        return redirect(url_for('liste_livres'))

if __name__ == \"__main__\":
    app.run(debug=True)
