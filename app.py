import os
from flask import Flask, render_template, request
import requests

# Create app - templates are in the 'templates' folder in the same directory
app = Flask(__name__)

# Hugging Face API URL
HF_API_URL = "https://chemman-breastcare-predict.hf.space/run/predict"

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
        
        # Data format for Gradio
        data = {
            "data": input_data
        }
        
        # Call Hugging Face API
        response = requests.post(HF_API_URL, json=data)
        result = response.json()
        
        # Parse Hugging Face response
        if response.status_code == 200 and "data" in result:
            prediction_data = result["data"]
            
            # Extract diagnosis and confidence from Hugging Face response
            diagnosis = prediction_data[0]  # "Breast Cancer" or "No Breast Cancer"
            confidence = float(prediction_data[1])  # confidence percentage
            
            output1 = f"The patient is diagnosed with {diagnosis}"
            output2 = f"Confidence: {confidence:.2f}%"
        else:
            output1 = "Error: Unexpected response from ML API"
            output2 = ""

        return render_template("home.html", output1=output1, output2=output2,
                               query1=request.form['query1'], query2=request.form['query2'],
                               query3=request.form['query3'], query4=request.form['query4'],
                               query5=request.form['query5'])

    except Exception as e:
        error_message = f"Error: {e}"
        print(f"Prediction error: {e}")
        return render_template("home.html", output1=error_message, output2="")

# For Render deployment
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)