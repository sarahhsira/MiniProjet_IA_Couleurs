import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Charger l'image
image_path = os.path.join('Images', 'Test_Image.jpg')
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir BGR → RGB

# Redimensionner pour accélérer le traitement (optionnel)
image = cv2.resize(image, (300, 300))

# Transformer l'image en tableau de pixels (R, G, B)
pixels = image.reshape((-1, 3))  

# Appliquer K-Means pour détecter les couleurs dominantes
num_colors = 10  # Nombre de couleurs dominantes
kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
kmeans.fit(pixels)

# Récupérer les couleurs dominantes
colors = kmeans.cluster_centers_.astype(int)

# Fonction pour calculer la luminosité
def luminosity(color):
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

# Trier les couleurs par luminosité (du plus foncé au plus clair)
colors = sorted(colors, key=luminosity)

# Trouver combien de pixels appartiennent à chaque cluster
labels, counts = np.unique(kmeans.labels_, return_counts=True)

# Trier les couleurs en fonction du nombre de pixels
sorted_indices = np.argsort(-counts)  # Tri décroissant
sorted_colors = [colors[i] for i in sorted_indices]  # Appliquer l'index trié aux couleurs
sorted_counts = counts[sorted_indices]

# Normalisation des couleurs pour l'affichage dans matplotlib (de 0 à 1)
normalized_colors = [c/255 for c in sorted_colors]

# Fonction pour obtenir une couleur approximative (nom de la couleur)
def get_color_name(color):
    hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
    return hex_color

# Affichage côte à côte : Image originale, palette triée par luminosité et histogramme
fig, ax = plt.subplots(1, 3, figsize=(18, 6))  # Taille de la figure agrandie

# Image originale
ax[0].imshow(image)
ax[0].axis("off")
ax[0].set_title("Image Originale")

# Palette de couleurs triées au centre
ax[1].imshow([colors])
ax[1].axis("off")
ax[1].set_title("Couleurs Dominantes")

# Affichage de l’histogramme à droite
bars = ax[2].bar(range(len(sorted_colors)), sorted_counts, color=normalized_colors, width=0.8)  # Augmenter la largeur des barres
ax[2].set_xticks(range(len(sorted_colors)))  # Afficher les ticks de l'axe x pour chaque couleur
ax[2].set_xticklabels([get_color_name(c) for c in sorted_colors], rotation=45, ha='right')  # Afficher les noms hexadécimaux des couleurs
ax[2].set_xlabel("Couleurs")
ax[2].set_ylabel("Nombre de Pixels")
ax[2].set_title("Répartition des Couleurs Dominantes")

# Limiter l'échelle de l'axe des ordonnées
ax[2].set_ylim(0, 100000)  # Limiter jusqu'à 100 000 pixels

# Ajuster l'échelle des barres pour mieux les répartir
ax[2].tick_params(axis="y", labelsize=8)  # Réduire la taille des ticks sur l'axe y

# Ajouter les valeurs du nombre de pixels à côté des barres (plutôt qu'au-dessus)
for bar, count in zip(bars, sorted_counts):
    height = bar.get_height()
    if height > 1000:  # Afficher les valeurs uniquement si elles sont au-dessus de 1000 pixels
        ax[2].text(bar.get_x() + bar.get_width() / 2, height + 500, str(count),
                   ha='center', va='bottom', fontsize=7, color='black')


# Ajuster l'espacement entre les sous-graphes pour mieux les espacer
plt.subplots_adjust(wspace=0.3)  # Ajouter de l'espace entre les sous-graphes

# Afficher la figure
plt.show()
