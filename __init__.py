from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

# Fonction pour vérifier si l'utilisateur est un administrateur
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

        if not email or not mot_de_passe:
            return render_template('formulaire_authentification.html', error="Veuillez remplir tous les champs.")

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, mot_de_passe))
            utilisateur = cursor.fetchone()
            conn.close()

            if utilisateur:
                session['authentifie'] = True
                session['role'] = utilisateur[5]
                session['user_id'] = utilisateur[0]
                return redirect(url_for('accueil'))
            else:
                return render_template('formulaire_authentification.html', error="Identifiant ou mot de passe incorrect.")

        except sqlite3.DatabaseError as e:
            return render_template('formulaire_authentification.html', error=f"Erreur de base de données : {e}")

        except Exception as e:
            return render_template('formulaire_authentification.html', error=f"Erreur serveur : {e}")

    return render_template('formulaire_authentification.html', error=False)

# Route pour la déconnexion
@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

# Route pour afficher la liste des livres
@app.route('/liste_livres')
def liste_livres():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")
        livres = cursor.fetchall()
        conn.close()
        return render_template('liste_livres.html', livres=livres)

    except sqlite3.DatabaseError as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur de base de données : {e}")

    except Exception as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur serveur : {e}")

# Route pour ajouter un livre
@app.route('/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    if not est_authentifie() or not est_admin():
        return redirect(url_for('accueil'))  # Redirection si l'utilisateur n'est pas admin

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
            cursor.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                           (titre, auteur, annee, quantite))
            conn.commit()
            conn.close()
            return redirect(url_for('liste_livres'))  # Redirection vers la liste des livres après ajout

        except sqlite3.DatabaseError as e:
            return render_template('ajouter_livre.html', error=f"Erreur de base de données : {e}")

        except Exception as e:
            return render_template('ajouter_livre.html', error=f"Erreur serveur : {e}")

    return render_template('ajouter_livre.html')  # Affichage du formulaire d'ajout

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
