from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema import Document
from vectordb import Memory
import pickle, os
import pandas as pd

HF_API_TOKEN = "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" # token do HuggingFace

model = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    huggingfacehub_api_token=HF_API_TOKEN,
    temperature=0.1,
    max_new_tokens=2048,
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

def chat_faiss(msg, db):
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
    prompt = f"{context}\n\nQuestion: Qual dessas músicas corresponde a '{msg}'? Fale sobre a música escolhida, não precisa informar qual ordem da música escolhida, só informe qual a música e a explicação.\n\Resposta: "
    return model.invoke(prompt)

def load_vectordb(path):
  return Memory(chunking_strategy={"mode": "sliding_window", "window_size": 14, "overlap": 10}, memory_file=path)

def save_vectordb(memory, sections, file_name):
  for i in range(0, len(sections)):
    letra = sections[i].page_content

    metadata = {
      "author": sections[i].metadata["author"],
      "tittle": sections[i].metadata["tittle"],
      "lyrics": sections[i].metadata["lyrics"]
    }

def create_sections(path):
  dataframe = pd.read_csv(path)
  sections = [
      Document(
          page_content = row["lyrics"],
          metadata = {
              "author": row["author"],
              "tittle": row["music"],
              "lyrics": row["lyrics"]
          }
      )
      for index, row in dataframe.iterrows()
  ]
  return sections

def chat_vectordb(msg, mem):
   top_songs = mem.search(msg, top_n=4)
   seen = set()
   context = []
   for song in top_songs:
      artist = song['metadata']['autor']
      tittle = song['metadata']['musica']
      unique_key = (artist, tittle)
      if unique_key not in seen:
         seen.add(unique_key)
         lyrics = song['metadata']['letra'][:3000]
         context.append(f"Artist: {artist}, Song Name: {tittle}, Lyrics: {lyrics}")
   # Converte a lista de context para uma string
   context = "\n\n".join(context)
   prompt = f"{context}\n\nQuestion: Qual dessas músicas corresponde a '{msg}'? Fale sobre a música escolhida, não precisa informar qual ordem da música escolhida, só informe qual a música e a explicação.\n\Resposta: "
   return model.invoke(prompt)

#mem = Memory(chunking_strategy={"mode": "sliding_window", "window_size": 14, "overlap": 10})
#save_vectordb(mem, create_sections("../WebScrapingLyrics/song_lyrics.csv"), "./mem1.pkl")