from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    data = {
        "status": "success",
        "message": "Flask API berjalan"
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
