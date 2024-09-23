from langchain_community.vectorstores import FAISS
#from langchain_community.llms.huggingface_hub import HuggingFaceHub
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_huggingface import HuggingFaceEndpoint
import torch, pickle, os
import pandas as pd

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

HF_API_TOKEN = "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"

'''model = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 512,
        "top_k": 30,
        "temperature": 0.1,
        "repetition_penalty": 1.03,
    },
    huggingfacehub_api_token=HF_API_TOKEN,
)'''

model = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    huggingfacehub_api_token=HF_API_TOKEN,
    temperature=0.1,
    max_new_tokens=512,
    top_k=30,
    repetition_penalty=1.03,
)

def save_faiss(db, file="faiss_index.bin", metadata_file="metadata.pkl"):
    db.save_local(file)
    with open(metadata_file, "wb") as f:
        pickle.dump(db.index_to_docstore_id, f)
        pickle.dump(db.docstore._dict, f)

def load_faiss(file="faiss_index.bin", metadata_file="metadata.pkl"):
    if os.path.exists(file) and os.path.exists(metadata_file):
        db = FAISS.load_local(
            file, 
            HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2", 
                model_kwargs={'device': 'cpu'}, 
                encode_kwargs={'normalize_embeddings': False}), 
            allow_dangerous_deserialization=True)
        with open(metadata_file, "rb") as f:
            db.index_to_docstore_id = pickle.load(f)
            db.docstore._dict = pickle.load(f)
        return db
    else:
        return make_db()

def make_db():
    df = pd.read_csv("../WebScrapingLyrics/top_musicas.csv")
    df['id'] = df['author'] + "-" + df['music']
    txts = df['lyrics'].tolist()
    metadata = [{"author": author, "music": music} for author, music in zip(df['author'], df['music'])]

    # Criar embeddings das letras
    
    #embeddings = HuggingFaceEmbeddings()
    name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(
        model_name=name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    db = FAISS.from_texts(txts, embeddings, metadatas=metadata)
    save_faiss(db)
    return db

def chat(msg):
    db = load_faiss()
    retriever = db.as_retriever()
    docs = retriever.invoke(msg)

    context = "\n\n".join([f"Artist: {d.metadata['author']}, Song Name: {d.metadata['music']}, Lyrics: {d.page_content}" for d in docs])

    '''template = """
    You are a music expert. Based on the following context from song lyrics, answer the question about which song matches the given lyrics. Choose just one and explain your reasoning.

    Context:
    {context}

    Question: {question}

    Answer: 
    """'''
    #llm = Ollama(model="llama3.1")
    #prompt = f"Baseado no seguinte contexto de letras:\n{context}\n\nEscolha uma música e explique sua escolha de forma polida."
    #response = llm(prompt)
    #return f"Resposta: {response}"

    prompt = f"{context}\n\nQuestion: Qual dessas músicas corresponde a '{msg}'? Fale sobre a música escolhida, não precisa informar qual ordem da música escolhida, só informe qual a música e a explicação.\n\Resposta: "
    return model.invoke(prompt)
    #prompt = template.format(context=context, question=msg)
    #return model.invoke(prompt)

#lyric = "So I'ma love you every night like it's the last night"
#lyric = "amiga minha namorada"
#lyric = "For the way I hurt"
lyric = "frozen inside without your"
print(chat(lyric))