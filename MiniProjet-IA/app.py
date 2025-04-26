# Importation des modules nécessaires
from flask import Flask, render_template, request, send_from_directory
import os
import cv2  # OpenCV pour le traitement d'image
import numpy as np
from sklearn.cluster import KMeans  # Algorithme de clustering
import matplotlib
matplotlib.use('Agg')  # Configuration du backend pour matplotlib (nécessaire pour Flask)
import matplotlib.pyplot as plt
from io import BytesIO  # Pour gérer les flux mémoire
import base64  # Pour encoder les images en base64

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de l'application
UPLOAD_FOLDER = 'uploads'  # Dossier pour stocker les images uploadées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Extensions de fichier autorisées
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Création du dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(image_path, num_colors=10):
    """
    Analyse une image pour en extraire les couleurs dominantes
    Args:
        image_path: Chemin vers l'image à analyser
        num_colors: Nombre de couleurs dominantes à extraire
    Returns:
        plot_data: Image du graphique encodée en base64
        color_data: Liste des couleurs dominantes avec leurs informations
    """
    # Chargement et traitement de l'image
    image = cv2.imread(image_path)  # Lecture de l'image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Conversion BGR vers RGB
    image = cv2.resize(image, (300, 300))  # Redimensionnement pour traitement plus rapide
    
    # Préparation des données pour le clustering
    pixels = image.reshape((-1, 3))  # Aplatir l'image en tableau 2D de pixels
    
    # Application de l'algorithme K-means pour trouver les couleurs dominantes
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Récupération des couleurs dominantes (centres des clusters)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Fonction pour calculer la luminosité d'une couleur
    def luminosity(color):
        return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    
    # Tri des couleurs par luminosité
    colors_by_luminosity = sorted(colors, key=luminosity)
    
    # Comptage des pixels dans chaque cluster et tri par fréquence
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_indices = np.argsort(-counts)  # Indices triés par ordre décroissant
    sorted_colors = [colors[i] for i in sorted_indices]  # Couleurs triées
    sorted_counts = counts[sorted_indices]  # Comptes triés
    
    # Création des graphiques
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))  # 3 subplots côte à côte
    
    # Subplot 1: Image originale
    ax[0].imshow(image)
    ax[0].axis("off")
    ax[0].set_title("Original Image")
    
    # Subplot 2: Palette de couleurs triée par luminosité
    ax[1].imshow([colors_by_luminosity])
    ax[1].axis("off")
    ax[1].set_title("Colors by Luminosity")
    
    # Subplot 3: Histogramme de distribution des couleurs
    normalized_colors = [c/255 for c in sorted_colors]  # Normalisation pour matplotlib
    bars = ax[2].bar(range(len(sorted_colors)), sorted_counts, 
                     color=normalized_colors, width=0.8)
    ax[2].set_xticks(range(len(sorted_colors)))
    # Étiquettes des ticks avec les codes hexadécimaux
    ax[2].set_xticklabels([f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in sorted_colors], 
                         rotation=45, ha='right')
    ax[2].set_xlabel("Colors")
    ax[2].set_ylabel("Pixel Count")
    ax[2].set_title("Color Distribution")
    ax[2].set_ylim(0, max(sorted_counts) * 1.1)  # Marge de 10% en haut
    
    # Ajout des valeurs sur les barres
    for bar, count in zip(bars, sorted_counts):
        height = bar.get_height()
        ax[2].text(bar.get_x() + bar.get_width() / 2, height + max(sorted_counts)*0.05, str(count),
                   ha='center', va='bottom', fontsize=7, color='black')
    
    plt.tight_layout()  # Ajustement automatique de la mise en page
    
    # Sauvegarde du graphique dans un buffer mémoire
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()  # Fermeture de la figure pour libérer la mémoire
    buf.seek(0)
    # Encodage en base64 pour l'affichage HTML
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    
    # Préparation des données de couleur pour le template HTML
    color_data = []
    for i, (color, count) in enumerate(zip(sorted_colors, sorted_counts)):
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"  # Conversion en hexadécimal
        color_data.append({
            'hex': hex_color,
            'rgb': f"rgb({color[0]}, {color[1]}, {color[2]})",  # Format RGB
            'count': int(count),  # Nombre de pixels
            'percentage': f"{(count / sum(sorted_counts)) * 100:.1f}%"  # Pourcentage
        })
    
    return plot_data, color_data

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Gère l'upload des fichiers et l'affichage des résultats"""
    if request.method == 'POST':
        # Vérification de la présence du fichier
        if 'file' not in request.files:
            return render_template('index.html', error="No file selected")
        
        file = request.files['file']
        num_colors = int(request.form.get('num_colors', 10))  # Valeur par défaut: 10
        
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        # Vérification de l'extension et traitement du fichier
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)  # Sauvegarde du fichier uploadé
            
            try:
                # Analyse de l'image
                plot_data, color_data = analyze_image(filename, num_colors)
                return render_template('index.html', 
                                    plot_data=plot_data,
                                    color_data=color_data,
                                    filename=file.filename)
            except Exception as e:
                # Gestion des erreurs
                return render_template('index.html', error=f"Error processing image: {str(e)}")
    
    # Affichage du formulaire pour les requêtes GET
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Route pour servir les fichiers uploadés"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Lancement de l'application en mode debug
    app.run(debug=True)