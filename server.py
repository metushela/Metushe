from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram actif !"

# Pas besoin de lancer app.run ici — c'est main.py qui le fera