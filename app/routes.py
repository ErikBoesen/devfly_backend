from flask import render_template, request, jsonify, g
from app import app, db, scraper
#from app.models import


@app.route('/')
def index():
    return render_template('index.html')
