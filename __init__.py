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

@app.route('/liste_livres', methods=['GET', 'POST'])
def liste_livres():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")
        livres = cursor.fetchall()

        # Si un emprunt est effectué, on traite les données du formulaire
        if request.method == 'POST':
            livre_id = request.form.get('livre_id')
            nom_utilisateur = request.form.get('nom_utilisateur')
            date_emprunt = request.form.get('date_emprunt')

            # Optionnel : ici on pourrait enregistrer l'emprunt dans une base de données, mais comme tu ne veux pas stocker, on ignore cette partie
            print(f"Emprunt effectué : Livre ID {livre_id}, Nom : {nom_utilisateur}, Date : {date_emprunt}")
            return redirect(url_for('liste_livres'))

        conn.close()
        return render_template('liste_livres.html', livres=livres)

    except sqlite3.DatabaseError as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur de base de données : {e}")

    except Exception as e:
        return render_template('liste_livres.html', livres=[], message=f"Erreur serveur : {e}")

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
