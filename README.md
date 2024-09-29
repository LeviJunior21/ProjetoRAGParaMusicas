# Projeto RAG - Recuperação Aumentada por Geração com Letra de Músicas

Este é um projeto para a disciplina de Processamento de Linguagem Natural em que utiliza a técnica de *Retrieval-Augmented Generation* (RAG) para gerar respostas sobre músicas, dado um trecho de letra. A aplicação cria embeddings das letras de músicas, armazena-os em uma base vetorial (FAISS ou VectorDB), e usa um modelo de linguagem grande (LLM) hospedado no Hugging Face para retornar a música mais apropriada ao contexto fornecido.

## Funcionalidades
- **Web Scraping**: Coleta letras de músicas do site letras.mus.br.
- **Criação de Embeddings**: Gera embeddings das letras e armazena-os em uma base vetorial FAISS ou VectorDB.
- **Chatbot**: Interface via Flask (local) que recebe mensagens ou transcrições de áudio e retorna a música mais próxima.
- **Reconhecimento de Fala**: Converte áudio em texto para busca de músicas.

### Arquivo de dependências

Execute para instalar as dependências listadas no arquivo `requirements.txt` caso queira utilizar com Flask:
```bash
pip install -r requirements.txt
```

Adicionalmente, é preciso ter o `ffmpeg` instalado para processamento de áudio:

```bash
sudo apt-get install ffmpeg
```

## Executar com Flask

Para rodar a aplicação com interface de chatbot:

1. Garanta que você tenha como gerar os embeddings no `main.py` ou tenha uma base vetorial (FAISS ou VectorDB) salva.
2. Rode o comando para iniciar o servidor Flask:
    ```bash
    python flask_app.py
    ```
3. Acesse a interface via navegador (`http://127.0.0.1:5000/`).
4. Use a caixa de texto ou envie áudios para consultar o chatbot.
