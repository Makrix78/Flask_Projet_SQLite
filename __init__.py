from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def est_authentifie():
    return 'user_id' in session

def est_admin():
    return session.get('role') == 'admin'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['mot_de_passe'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error=True)
    return render_template('login.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not est_authentifie():
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session.get('role'))

@app.route('/livres', methods=['GET', 'POST'])
def livres():
    conn = get_db_connection()
    if request.method == 'POST' and est_admin():
        data = request.form
        conn.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                     (data['titre'], data['auteur'], data['annee_publication'], data['quantite']))
        conn.commit()
    livres = conn.execute("SELECT * FROM livres").fetchall()
    conn.close()
    return render_template('livres.html', livres=livres)

@app.route('/livres/delete/<int:livre_id>', methods=['POST'])
def delete_livre(livre_id):
    if not est_admin():
        return jsonify({'error': 'Accès refusé'}), 403
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('livres'))

@app.route('/emprunter/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('login'))
    conn = get_db_connection()
    livre = conn.execute('SELECT * FROM livres WHERE id = ? AND quantite > 0', (livre_id,)).fetchone()
    if livre:
        conn.execute('INSERT INTO emprunts (utilisateur_id, livre_id, date_retour_prevu) VALUES (?, ?, date("now", "+14 days"))',
                     (session['user_id'], livre_id))
        conn.execute('UPDATE livres SET quantite = quantite - 1 WHERE id = ?', (livre_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('livres'))

@app.route('/retourner/<int:emprunt_id>', methods=['POST'])
def retourner_livre(emprunt_id):
    if not est_authentifie():
        return redirect(url_for('login'))
    conn = get_db_connection()
    emprunt = conn.execute('SELECT * FROM emprunts WHERE id = ? AND date_retour_effectif IS NULL', (emprunt_id,)).fetchone()
    if emprunt:
        conn.execute('UPDATE emprunts SET date_retour_effectif = date("now") WHERE id = ?', (emprunt_id,))
        conn.execute('UPDATE livres SET quantite = quantite + 1 WHERE id = ?', (emprunt['livre_id'],))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
