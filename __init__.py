from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Fonction pour vérifier si l'utilisateur est authentifié
def est_authentifie():
    return session.get('authentifie')

# Route d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

# Route de l'authentification
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')

        # Vérification de l'utilisateur dans la base de données
        # Logique d'authentification ici...
        session['authentifie'] = True  # Exemple d'authentification réussie
        return redirect(url_for('accueil'))

    return render_template('formulaire_authentification.html', error=False)

# Route de liste des livres
@app.route('/liste_livres')
def liste_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    # Récupérer les livres depuis la base de données
    # Logique pour afficher les livres
    return render_template('liste_livres.html')

# Lancer l'application
if __name__ == "__main__":
    app.run(debug=True)
