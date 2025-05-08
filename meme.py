import json
import os
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import server  # Import ton fichier Flask

TOKEN = "7980302462:AAFS3EBrr1qaeWVwsY63W_fusboMlNKETE8"  # remplace avec le vrai

FICHIER_QR = "base_qr.json"

def charger_base():
    if os.path.exists(FICHIER_QR):
        with open(FICHIER_QR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_base(base):
    with open(FICHIER_QR, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)

base_qr = charger_base()
en_attente = {}

clavier = ReplyKeyboardMarkup([
    [KeyboardButton("📄 Lister les questions")],
    [KeyboardButton("➕ Apprendre une question")],
    [KeyboardButton("❌ Oublier une question")]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Utilise les boutons ci-dessous ou pose-moi une question.", reply_markup=clavier)

async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Utilisation : /forget question à effacer")
        return
    question = " ".join(context.args).lower().strip()
    if question in base_qr:
        del base_qr[question]
        sauvegarder_base(base_qr)
        await update.message.reply_text(f"La question « {question} » a été oubliée.")
    else:
        await update.message.reply_text("Je ne connais pas cette question.")

async def lister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not base_qr:
        await update.message.reply_text("Je n’ai encore appris aucune question.")
    else:
        questions = "\n".join(f"- {q}" for q in base_qr.keys())
        await update.message.reply_text(f"Voici les questions que je connais :\n{questions}")

async def repondre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texte = update.message.text.strip().lower()

    if texte == "📄 lister les questions":
        questions = "\n".join(f"- {q}" for q in base_qr) or "Aucune question connue."
        await update.message.reply_text(f"Voici ce que je connais :\n{questions}")
        return
    if texte == "➕ apprendre une question":
        await update.message.reply_text("Pose-moi directement ta question, puis je te demanderai sa réponse.")
        return
    if texte == "❌ oublier une question":
        await update.message.reply_text("Utilise la commande : /forget ta question exacte.")
        return

    if user_id in en_attente:
        question = en_attente.pop(user_id)
        base_qr[question] = texte
        sauvegarder_base(base_qr)
        await update.message.reply_text("Merci ! J’ai bien retenu ça.")
        return

    if texte in base_qr:
        await update.message.reply_text(base_qr[texte])
    elif texte.endswith("?"):
        await update.message.reply_text("Je ne connais pas encore cette réponse. Peux-tu me dire quoi répondre ?")
        en_attente[user_id] = texte
    else:
        await update.message.reply_text("Pose-moi une question ou utilise les boutons ci-dessous.")

# Lancement du bot + Flask pour cron-job
if __name__ == "__main__":
    Thread(target=server.app.run, kwargs={"host": "0.0.0.0", "port": 8080}).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("forget", forget))
    app.add_handler(CommandHandler("list", lister))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, repondre))
    app.run_polling()
    from flask import Flask
from threading import Thread

web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot en ligne"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()