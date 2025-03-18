@app.route('/liste_livres')
def liste_livres():
    # Vérifier si l'utilisateur est authentifié
    if not est_authentifie():
        return render_template('formulaire_authentification.html', error="Veuillez vous connecter pour accéder à la liste des livres.")

    try:
        # Connexion à la base de données
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Sélectionner les livres disponibles (quantité > 0)
        cursor.execute("SELECT * FROM livres WHERE quantite > 0")
        livres = cursor.fetchall()
        conn.close()

        # Débogage : Afficher les livres récupérés
        print("Livres récupérés:", livres)

        # Vérifier si des livres sont trouvés
        if not livres:
            return render_template('liste_livres.html', livres=[], message="Aucun livre disponible.")
        
        # Afficher les livres disponibles
        return render_template('liste_livres.html', livres=livres, message="")

    except sqlite3.DatabaseError as e:
        print("Erreur de base de données lors de l'affichage des livres:", e)
        return render_template('liste_livres.html', livres=[], message=f"Erreur de base de données : {e}")

    except Exception as e:
        print("Erreur serveur:", e)
        return render_template('liste_livres.html', livres=[], message=f"Erreur serveur : {e}")
