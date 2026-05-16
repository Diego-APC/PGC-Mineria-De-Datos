
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
     return render_template("index.html")

@app.route("/PGC/")
def pgc():
     return render_template("DescripcionProyecto.html")

@app.route("/fase1/")
def fase1():
     return render_template("fase1.html")

@app.route("/dashboard/")
def dashboard():
     return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
