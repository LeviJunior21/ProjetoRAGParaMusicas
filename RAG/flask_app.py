import re, torch
from flask import Flask, request, render_template, jsonify
import main as m

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = Flask(__name__)

@app.route('/')
def home():
    # Renderiza a página HTML onde o chatbot será exibido
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Recebe a mensagem do usuário
    user_message = request.form['user_input']
    
    # Gera a resposta usando a função 'chat'
    bot_message = m.chat(user_message)
    
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

if __name__ == '__main__':
    app.run()