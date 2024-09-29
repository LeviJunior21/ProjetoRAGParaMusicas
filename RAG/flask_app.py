#import torch
from flask import Flask, request, render_template, jsonify
import main as m
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

app = Flask(__name__)

# Carregar o DB quando o aplicativo é iniciado
#db = m.load_faiss() # No FAISS, caso não exista, ele tenta criar outro e salva
mem = m.load_vectordb("./save.pkl") # No VectorDB, caso não exista, é preciso criar manualmente e fornecer o caminho do arquivo

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
    print("Extracted Answer:", bot_message)
    return {'response': bot_message}

@app.route("/voice-to-text", methods=["POST"])
def voice_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    audio_file = request.files['file']

    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    audio_seg = AudioSegment.from_file(audio_file)
    wav_io = BytesIO()
    audio_seg.export(wav_io, format='wav')
    wav_io.seek(0)

    r = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio_dt = r.record(source)
    try:
        txt = r.recognize_google(audio_dt, language="pt-BR")
        print(f"Transcrição: {txt}")
        return jsonify({"transcription": txt}), 200
    except sr.UnknownValueError:
        return jsonify({"error": "Não foi possível entender o áudio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Erro ao tentar usar o serviço de reconhecimento de fala: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
