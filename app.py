import os
from flask import Flask, render_template, request
import requests
import re

# Create app - templates are in the 'templates' folder in the same directory
app = Flask(__name__)

# Hugging Face API URL
HF_API_URL = "https://chemman-breastcare-api.hf.space/predict"


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

        # Prepare input for Hugging Face API in the expected format
        input_data = {
            "perimeter_worst": inputQuery1,
            "concave_points_worst": inputQuery2,
            "concave_points_mean": inputQuery3,
            "area_mean": inputQuery4,
            "area_worst": inputQuery5
        }
        
        response = requests.post(HF_API_URL, json=input_data)
        
        # DEBUG: See what we're getting
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        # Try to parse as JSON first
        try:
            result = response.json()
            if "message" in result and "confidence" in result:
                prediction_text = result["message"]
                confidence = result["confidence"]
                diagnosis = "Breast Cancer" if "Breast Cancer" in prediction_text else "No Breast Cancer"
                output1 = f"The patient is diagnosed with {diagnosis}"
                output2 = f"Confidence: {confidence}%"
            else:
                output1 = "Processing prediction..."
                output2 = str(result)
        except:
            output1 = "Processing prediction..."
            output2 = response.text
        
        print(f"Prediction text: {prediction_text if 'prediction_text' in locals() else 'N/A'}")
        
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
    print(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
