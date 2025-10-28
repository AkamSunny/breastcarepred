from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# CORRECT Hugging Face API URL
HF_API_URL = "https://chemman-breastcare-predict.hf.space/run/predict"

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
        # Get inputs from form - CORRECT ORDER for Gradio
        input_data = [
            float(request.form['query1']),  # perimeter_worst
            float(request.form['query2']),  # concave_points_worst
            float(request.form['query3']),  # concave_points_mean  
            float(request.form['query4']),  # area_mean
            float(request.form['query5'])   # area_worst
        ]
        
        # CORRECT data format for Gradio
        data = {
            "data": input_data
        }
        
        # Call Hugging Face API
        response = requests.post(HF_API_URL, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        result = response.json()
        
        # Gradio returns data in different format
        if "data" in result:
            prediction_result = result["data"]
            diagnosis = "Breast Cancer" if prediction_result[0] == 1 else "No Breast Cancer"
            confidence = float(prediction_result[1]) * 100
            
            output1 = f"The patient is diagnosed with {diagnosis}"
            output2 = f"Confidence: {confidence:.2f}%"
        else:
            output1 = "Error: Unexpected response format from ML API"
            output2 = ""
        
        return render_template("home.html", output1=output1, output2=output2,
                               query1=request.form['query1'], query2=request.form['query2'],
                               query3=request.form['query3'], query4=request.form['query4'],
                               query5=request.form['query5'])
                               
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(f"Prediction error: {e}")
        return render_template("home.html", output1=error_message, output2="")

@app.route("/debug-predict", methods=["POST"])
def debugPrediction():
    try:
        input_data = [100.0, 0.1, 0.05, 500.0, 800.0]  # Sample values
        
        data = {"data": input_data}
        response = requests.post(HF_API_URL, json=data)
        
        return jsonify({
            "status_code": response.status_code,
            "response_text": response.text,
            "response_json": response.json() if response.text else "No response"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Flask app is alive!"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)