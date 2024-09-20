import requests, time
import pandas as pd
from bs4 import BeautifulSoup

base_url = "https://www.letras.mus.br"

def request_site(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print("Erro ao acessar o site")
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def get_top_musics(url):
    top_url = f"{base_url}/{url}"
    sp = request_site(top_url)
    
    if sp == None:
        return
    
    music_links = sp.select("ol.top-list_mus li a")[:1000]
    dt = []
    for link in music_links:
        music_url = base_url + link['href']
        music_sp = request_site(music_url)
        if music_sp == None:
            return
        
        author = music_sp.select_one("div.textStyle h2").text.strip() if music_sp.select_one("div.textStyle h2") else "desconhecido"
        music = music_sp.select_one("h1").text.strip() if music_sp.select_one("h1") else "desconhecido"
        lyrics = music_sp.select_one("div.lyric-original").text.strip() if music_sp.select_one("div.lyric-original") else "letra não encontrada"

        dt.append({"author": author, "music": music, "lyrics": lyrics})
        #time.sleep(1)
    return dt

def save_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("top_musicas.csv", index=False)

data = get_top_musics("mais-acessadas/")
save_csv(data)
#print(data[:4])