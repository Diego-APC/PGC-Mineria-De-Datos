
from flask import Flask, render_template

import Clustering

app = Flask(__name__)

@app.route("/")

def home():
     return "hello World"

@app.route("/PGC/")
def pgc():
     return render_template("DescripcionProyecto.html")

@app.route("/Cluster/")
def cluster():
     info = Clustering.RealizarClustering()
     return render_template("ClusterResults.html", resultados = info["resumenCluster"])
