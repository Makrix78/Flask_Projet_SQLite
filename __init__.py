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
                session['role'] = utilisateur[5]  # Récupère le rôle de l'utilisateur
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

# Route pour supprimer un livre
@app.route('/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre(livre_id):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Suppression du livre en fonction de son ID
        cursor.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('liste_livres'))  # Redirection après suppression

    except sqlite3.DatabaseError as e:
        print("Erreur de base de données lors de la suppression :", e)
        return redirect(url_for('liste_livres'))  # Retour à la liste en cas d'erreur

# Route pour emprunter un livre
@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_authentifie():  # Vérifier si l'utilisateur est authentifié
        return redirect(url_for('authentification'))  # Redirige si non authentifié

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Vérifier la quantité disponible avant l'emprunt
        cursor.execute("SELECT quantite FROM livres WHERE id = ?", (livre_id,))
        livre = cursor.fetchone()

        if livre and livre[0] > 0:
            # Réduire la quantité de 1
            cursor.execute("UPDATE livres SET quantite = quantite - 1 WHERE id = ?", (livre_id,))
            conn.commit()

            # Enregistrer l'emprunt dans la table "emprunts"
            cursor.execute("INSERT INTO emprunts (user_id, livre_id) VALUES (?, ?)", (session['user_id'], livre_id))
            conn.commit()

            conn.close()
            return redirect(url_for('liste_livres'))  # Rediriger après l'emprunt
        else:
            conn.close()
            return redirect(url_for('liste_livres', message="Quantité insuffisante pour emprunter ce livre."))

    except sqlite3.DatabaseError as e:
        print("Erreur de base de données lors de l'emprunt :", e)
        return redirect(url_for('liste_livres', message="Erreur lors de l'emprunt du livre."))

    except Exception as e:
        print("Erreur serveur :", e)
        return redirect(url_for('liste_livres', message="Erreur serveur."))

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
