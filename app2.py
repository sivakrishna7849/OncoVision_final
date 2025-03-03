import os
from flask import Flask, request, jsonify, render_template
from PIL import Image
from io import BytesIO
from ensemble2 import ensemble_predict, get_image_from_url
from openai_handler import get_openai_analysis, generate_recommendation

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    image = None
    image_path = None
    
    # Case 1: Image file upload
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        try:
            image = Image.open(BytesIO(file.read())).convert("RGB")
            image_path = file.filename
        except Exception as e:
            return jsonify({'error': f'Error processing uploaded image: {str(e)}'}), 400
    
    # Case 2: Image URL
    elif 'image_url' in request.form and request.form['image_url']:
        url = request.form['image_url']
        try:
            image = get_image_from_url(url)
            image_path = url
            if not image:
                return jsonify({'error': 'Could not retrieve image from URL'}), 400
        except Exception as e:
            return jsonify({'error': f'Error retrieving image from URL: {str(e)}'}), 400
    
    # Case 3: No image provided
    else:
        return jsonify({'error': 'No image or image URL provided'}), 400
    
    try:
        # Get prediction from ensemble model
        result = ensemble_predict(image, image_path)
        
        # If prediction is non-cancerous, make sure areas of concern is empty
        if result['prediction'] == 'Non-Cancerous':
            result['areasOfConcern'] = []
            result['recommendation'] = 'No signs of oral cancer detected. Continue regular oral check-ups.'
        else:
            # For cancerous predictions, get detailed analysis from OpenAI
            openai_result = get_openai_analysis(
                image, 
                result['prediction'], 
                result.get('areasOfConcern', [])
            )
            
            if openai_result:
                # Add OpenAI analysis to the result
                result['openai_analysis'] = openai_result.get('analysis_text')
                result['cancer_type'] = openai_result.get('cancer_type', 'Unspecified')
                result['symptoms'] = openai_result.get('symptoms', [])
                result['risk_factors'] = openai_result.get('risk_factors', [])
                
                # Generate a tailored recommendation
                result['recommendation'] = generate_recommendation(
                    result['cancer_type'],
                    result.get('areasOfConcern', [])
                )
            else:
                # Default recommendation if OpenAI analysis fails
                result['recommendation'] = 'Patterns suggestive of oral cancer detected. Please consult with a healthcare professional immediately.'
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)