from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

# Fonction pour forcer l'authentification
def login_requis(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not est_authentifie():
            return redirect(url_for('authentification'))
        return f(*args, **kwargs)
    return decorated_function

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
            cursor.execute("SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe = ?", (email, mot_de_passe))
            utilisateur = cursor.fetchone()
            conn.close()

            if utilisateur:
                session['authentifie'] = True
                session['role'] = utilisateur[5]  # Récupère le rôle (admin/utilisateur)
                session['user_id'] = utilisateur[0]  # Récupère l'ID de l'utilisateur
                return redirect(url_for('accueil'))
            else:
                return render_template('formulaire_authentification.html', error="Identifiant ou mot de passe incorrect.")
        
        except sqlite3.DatabaseError as e:
            return render_template('formulaire_authentification.html', error=f"Erreur de base de données : {e}")
        except Exception as e:
            return render_template('formulaire_authentification.html', error=f"Erreur serveur : {e}")

    return render_template('formulaire_authentification.html', error=False)

@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('accueil'))

@app.route('/liste_livres')
@login_requis
def liste_livres():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")
        livres = cursor.fetchall()
        conn.close()
        
        if not livres:
            return render_template('liste_livres.html', livres=[], message="Aucun livre disponible.")

        return render_template('liste_livres.html', livres=livres, message="")
    
    except sqlite3.DatabaseError as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur de base de données : {e}")
    except Exception as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur serveur : {e}")

if __name__ == "__main__":
    app.run(debug=True)
