import pandas as pd
import torch
from langchain.schema import Document
from vectordb import Memory

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataframe = pd.read_csv("../WebScrapingLyrics/top_musicas.csv")

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

memory = Memory(chunking_strategy={"mode": "sliding_window", "window_size": 14, "overlap": 10})

for i in range(0, len(sections)):
  letra = sections[i].page_content

  metadata = {
    "author": sections[i].metadata["author"],
    "tittle": sections[i].metadata["tittle"],
    "lyrics": sections[i].metadata["lyrics"]
  }

  memory.save(letra, metadata)

top_musicas = memory.search("For the way I hurt", top_n=4)
for top_musica in top_musicas[:4]:
  #print(f"Com distância de: {top_musica['distance']}")
  print(top_musica['metadata']['author']+ " - " + top_musica['metadata']['tittle'])
  #print(f"\n{corrigir_musica(top_musica['metadata']['letra'])}\n\n")