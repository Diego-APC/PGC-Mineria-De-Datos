
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
     return pgc()

@app.route("/PGC/")
def pgc():
     return render_template("DescripcionProyecto.html")

if __name__ == "__main__":
    app.run()
