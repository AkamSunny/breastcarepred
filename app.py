import os
from flask import Flask, render_template, request
import requests
import re

# Create app - templates are in the 'templates' folder in the same directory
app = Flask(__name__)

# Hugging Face API URL
HF_API_URL = "https://chemman-breastcare-predict.hf.space/predict"

# Diagnostic logging
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))
print("Templates directory exists?:", os.path.exists('templates'))
if os.path.exists('templates'):
    print("Files in templates:", os.listdir('templates'))

@app.route("/ping")
def ping():
    return {"status": "ok", "message": "Flask app is alive!"}

@app.route("/")
def home():
    return render_template("home.html", query="")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/predict", methods=["POST"])
def cancerPrediction():
    try:
        # Get inputs from form
        inputQuery1 = float(request.form['query1'])
        inputQuery2 = float(request.form['query2'])
        inputQuery3 = float(request.form['query3'])
        inputQuery4 = float(request.form['query4'])
        inputQuery5 = float(request.form['query5'])

        # Prepare input for Hugging Face API
        input_data = [inputQuery1, inputQuery2, inputQuery3, inputQuery4, inputQuery5]
        
        data = {"data": input_data}
        response = requests.post(HF_API_URL, json=data)
        
        # DEBUG: See what we're getting
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        # Try to parse as JSON first
        try:
            result = response.json()
            if "data" in result:
                # If it's JSON with data field, extract the text
                prediction_text = result["data"]
            else:
                prediction_text = str(result)
        except:
            # If not JSON, use the raw text
            prediction_text = response.text
        
        print(f"Prediction text: {prediction_text}")
        
        # EXTRACT DIAGNOSIS AND CONFIDENCE FROM THE TEXT
        if "Breast Cancer" in prediction_text and "confidence" in prediction_text:
            # Parse the text output
            diagnosis = "Breast Cancer" if "Breast Cancer" in prediction_text else "No Breast Cancer"
            
            # Extract confidence number - look for pattern like "confidence": 99.66
            confidence_match = re.search(r'"confidence":\s*([\d.]+)', prediction_text)
            if confidence_match:
                confidence = float(confidence_match.group(1))
            else:
                confidence = 95.0  # default if not found
            
            output1 = f"The patient is diagnosed with {diagnosis}"
            output2 = f"Confidence: {confidence}%"
        else:
            output1 = "Processing prediction..."
            output2 = prediction_text  # Show raw response for debugging

        return render_template("home.html", output1=output1, output2=output2,
                               query1=request.form['query1'], query2=request.form['query2'],
                               query3=request.form['query3'], query4=request.form['query4'],
                               query5=request.form['query5'])

    except Exception as e:
        error_message = f"Error: {e}"
        print(f"Prediction error: {e}")
        return render_template("home.html", output1=error_message, output2="")

@app.route("/health")
def health():
    return {"status": "ok", "message": "Flask app is alive!"}

# For Render deployment
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)