from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Your Hugging Face Space URL
HF_API_URL = "https://chemman-breast-care.hf.space/predict"

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
        data = {
            'perimeter_worst': float(request.form['query1']),
            'concave_points_worst': float(request.form['query2']),
            'concave_points_mean': float(request.form['query3']),
            'area_mean': float(request.form['query4']),
            'area_worst': float(request.form['query5'])
        }
        
        # Call Hugging Face API
        response = requests.post(HF_API_URL, json=data)
        result = response.json()
        
        if "error" in result:
            return render_template("home.html", output1=f"Error: {result['error']}", output2="")
        
        output1 = f"The patient is diagnosed with {result['diagnosis']}"
        output2 = f"Confidence: {result['confidence']}%"
        
        return render_template("home.html", output1=output1, output2=output2,
                               query1=request.form['query1'], query2=request.form['query2'],
                               query3=request.form['query3'], query4=request.form['query4'],
                               query5=request.form['query5'])
                               
    except Exception as e:
        return render_template("home.html", output1=f"Error: {e}", output2="")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Flask app is alive!"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)