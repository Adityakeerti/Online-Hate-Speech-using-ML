from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import re
import joblib
from symspellpy import SymSpell, Verbosity
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
import os  # For accessing environment variables

# Initialize Flask app
app = Flask(__name__)

# Load the trained model and TF-IDF vectorizer
cv = joblib.load('vectorizer.pkl')  # Load the vectorizer
model = joblib.load('hate_speech_model.pkl')  # Load the trained model

# Initialize SymSpell object
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
sym_spell.load_dictionary("frequency_dictionary_en.txt", term_index=0, count_index=1)

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^A-Za-z\s]", "", text)
    text = text.strip()
    return text

def sentiment_analysis(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def symspell_clean(text):
    preprocessed_text = preprocess_text(text)
    corrected_text = " ".join([
        sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)[0].term
        if sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2) else word
        for word in preprocessed_text.split()
    ])
    sentiment_score = sentiment_analysis(corrected_text)
    return corrected_text, sentiment_score

# Route for the main page (serve index.html)
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# API route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()  # Get input text
        input_text = data['text']
        
        # Apply symspell cleaning and sentiment analysis
        cleaned_text, sentiment_score = symspell_clean(input_text)
        
        # Extract features using TF-IDF
        transformed_input_text = cv.transform([cleaned_text])
        transformed_input_sentiment = np.array([[sentiment_score]])
        
        # Combine TF-IDF and sentiment score features
        transformed_input = hstack([transformed_input_text, transformed_input_sentiment])
        
        # Make the prediction
        prediction = model.predict(transformed_input)
        
        # Return the prediction as a JSON response
        result = {'prediction': prediction[0]}
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})

# Run the Flask app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Get port from environment variable, default to 10000
    app.run(debug=True, host='0.0.0.0', port=port)  # Use 0.0.0.0 to listen on all IPs
