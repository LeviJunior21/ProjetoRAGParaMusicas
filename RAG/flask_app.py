import re, torch
from flask import Flask, request, render_template, jsonify
import main as m
from openai import OpenAI
client = OpenAI(api_key="sk-eGvZCSqrDCHZ67Q5K07q7ELmVRcHcS2vpwNhVPh_R-T3BlbkFJ0Iarg9b4HudzgrBhdahfXNWhSNuvXaRjrfcd_sCU0A")
device = torch.device("cpu")

app = Flask(__name__)

# Carregar o DB quando o aplicativo é iniciado
#db = m.load_faiss()
#save_vectordb(create_sections("../WebScrapingLyrics/top_musicas.csv"))
mem = m.load_vectordb("./save.pkl")

@app.route('/')
def home():
    # Renderiza a página HTML onde o chatbot será exibido
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Recebe a mensagem do usuário
    user_message = request.form['user_input']
    
    # Gera a resposta usando a função 'chat'
    #bot_message = m.chat_faiss(user_message, db)
    bot_message = m.chat_vectordb(user_message, mem)
    
    # Define o padrão regex para extrair a resposta do modelo, se necessário
    '''pattern = r"Answer:\s*(.*)"
    match = re.search(pattern, bot_message, re.DOTALL)

    if match:
        answer = match.group(1).strip()
        print("Extracted Answer:", answer)
        return {'response': answer}
    else:
        print("Answer not found")
        return {'response': "Answer not found as per context"}'''
    print("Extracted Answer:", bot_message)
    return {'response': bot_message}

@app.route("/voice-to-text", methods=["POST"])
def voice_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    audio_file = request.files['file']

    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        translation = openai.Audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text"
        )
        return jsonify({"transcription": translation.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()