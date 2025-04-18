from flask import Flask, render_template, request, send_from_directory
import os
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(image_path, num_colors=10):
    # Load and process image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (300, 300))
    
    # Reshape and cluster
    pixels = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get dominant colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Sort by luminosity
    def luminosity(color):
        return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
    colors_by_luminosity = sorted(colors, key=luminosity)
    
    # Sort by pixel count
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_indices = np.argsort(-counts)
    sorted_colors = [colors[i] for i in sorted_indices]
    sorted_counts = counts[sorted_indices]
    
    # Generate plots
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    
    # Original image
    ax[0].imshow(image)
    ax[0].axis("off")
    ax[0].set_title("Original Image")
    
    # Color palette (sorted by luminosity)
    ax[1].imshow([colors_by_luminosity])
    ax[1].axis("off")
    ax[1].set_title("Colors by Luminosity")
    
    # Histogram
    normalized_colors = [c/255 for c in sorted_colors]
    bars = ax[2].bar(range(len(sorted_colors)), sorted_counts, 
                     color=normalized_colors, width=0.8)
    ax[2].set_xticks(range(len(sorted_colors)))
    ax[2].set_xticklabels([f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in sorted_colors], 
                         rotation=45, ha='right')
    ax[2].set_xlabel("Colors")
    ax[2].set_ylabel("Pixel Count")
    ax[2].set_title("Color Distribution")
    ax[2].set_ylim(0, max(sorted_counts) * 1.1)
    
    for bar, count in zip(bars, sorted_counts):
        height = bar.get_height()
        ax[2].text(bar.get_x() + bar.get_width() / 2, height + max(sorted_counts)*0.05, str(count),
                   ha='center', va='bottom', fontsize=7, color='black')
    
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    
    # Prepare color data for HTML
    color_data = []
    for i, (color, count) in enumerate(zip(sorted_colors, sorted_counts)):
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        color_data.append({
            'hex': hex_color,
            'rgb': f"rgb({color[0]}, {color[1]}, {color[2]})",
            'count': int(count),
            'percentage': f"{(count / sum(sorted_counts)) * 100:.1f}%"
        })
    
    return plot_data, color_data

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error="No file selected")
        
        file = request.files['file']
        num_colors = int(request.form.get('num_colors', 10))
        
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            try:
                plot_data, color_data = analyze_image(filename, num_colors)
                return render_template('index.html', 
                                    plot_data=plot_data,
                                    color_data=color_data,
                                    filename=file.filename)
            except Exception as e:
                return render_template('index.html', error=f"Error processing image: {str(e)}")
    
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)