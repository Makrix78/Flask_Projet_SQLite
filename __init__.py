from flask import Flask, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Authentification utilisateur
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['mot_de_passe'], password):
        session['user_id'] = user['id']
        session['role'] = user['role']
        return jsonify({'message': 'Connexion réussie'}), 200
    return jsonify({'error': 'Identifiants incorrects'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

# Ajouter un livre (admin seulement)
@app.route('/livres', methods=['POST'])
def add_livre():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("INSERT INTO livres (titre, auteur, annee_publication, quantite) VALUES (?, ?, ?, ?)",
                 (data['titre'], data['auteur'], data['annee_publication'], data['quantite']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livre ajouté'}), 201

# Supprimer un livre (admin seulement)
@app.route('/livres/<int:livre_id>', methods=['DELETE'])
def delete_livre(livre_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livre supprimé'}), 200

# Recherche de livres
@app.route('/livres', methods=['GET'])
def search_livres():
    titre = request.args.get('titre', '')
    conn = get_db_connection()
    livres = conn.execute("SELECT * FROM livres WHERE titre LIKE ?", ('%' + titre + '%',)).fetchall()
    conn.close()
    return jsonify([dict(livre) for livre in livres])

# Emprunter un livre
@app.route('/emprunts', methods=['POST'])
def emprunter_livre():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentification requise'}), 401
    
    data = request.get_json()
    livre_id = data['livre_id']
    utilisateur_id = session['user_id']
    
    conn = get_db_connection()
    livre = conn.execute('SELECT * FROM livres WHERE id = ? AND quantite > 0', (livre_id,)).fetchone()
    if not livre:
        conn.close()
        return jsonify({'error': 'Livre indisponible'}), 400
    
    conn.execute('INSERT INTO emprunts (utilisateur_id, livre_id, date_retour_prevu) VALUES (?, ?, date("now", "+14 days"))', 
                 (utilisateur_id, livre_id))
    conn.execute('UPDATE livres SET quantite = quantite - 1 WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livre emprunté'}), 201

# Retourner un livre
@app.route('/emprunts/<int:emprunt_id>', methods=['PUT'])
def retourner_livre(emprunt_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentification requise'}), 401
    
    conn = get_db_connection()
    emprunt = conn.execute('SELECT * FROM emprunts WHERE id = ? AND date_retour_effectif IS NULL', (emprunt_id,)).fetchone()
    if not emprunt:
        conn.close()
        return jsonify({'error': 'Emprunt introuvable'}), 400
    
    conn.execute('UPDATE emprunts SET date_retour_effectif = date("now") WHERE id = ?', (emprunt_id,))
    conn.execute('UPDATE livres SET quantite = quantite + 1 WHERE id = ?', (emprunt['livre_id'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Livre retourné'}), 200

if __name__ == "__main__":
    app.run(debug=True)
