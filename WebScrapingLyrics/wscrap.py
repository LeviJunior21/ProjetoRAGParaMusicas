import requests
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
    return dt

def get_top_artists(url):
    top_url = f"{base_url}/{url}"
    sp = request_site(top_url)
    
    if sp == None:
        return
    
    art_links = sp.select("ol.top-list_art li a")
    dt = []
    for link in art_links:
        art_url = base_url + link['href']
        art_sp = request_site(art_url)
        if art_sp == None:
            continue
        music_links = art_sp.select("ol.cnt-list li a")
        for mlink in music_links:
            music_url = base_url + mlink['href']
            music_sp = request_site(music_url)
            if music_sp == None:
                continue
            author = music_sp.select_one("div.textStyle h2").text.strip() if music_sp.select_one("div.textStyle h2") else "desconhecido"
            music = music_sp.select_one("h1").text.strip() if music_sp.select_one("h1") else "desconhecido"
            lyrics = music_sp.select_one("div.lyric-original").text.strip() if music_sp.select_one("div.lyric-original") else "letra não encontrada"
            dt.append({"author": author, "music": music, "lyrics": lyrics})
    return dt

def get_top_songs_comparing(url, existing_data):
    top_url = f"{base_url}/{url}"
    sp = request_site(top_url)
    
    if sp is None:
        return
    
    music_links = sp.select("ol.top-list_mus li a")[:1000]
    dt = []
    existing_music_set = set(existing_data['music'])  # Conjunto com músicas existentes
    
    for link in music_links:
        music_title = link['title']
        if music_title in existing_music_set:
            continue
        music_url = base_url + link['href']
        music_sp = request_site(music_url)
        if music_sp == None:
            continue
        
        author = music_sp.select_one("div.textStyle h2").text.strip() if music_sp.select_one("div.textStyle h2") else "desconhecido"
        music = music_sp.select_one("h1").text.strip() if music_sp.select_one("h1") else "desconhecido"
        lyrics = music_sp.select_one("div.lyric-original").text.strip() if music_sp.select_one("div.lyric-original") else "letra não encontrada"

        dt.append({"author": author, "music": music, "lyrics": lyrics})
    return dt

def save_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)

#data = get_top_musics("mais-acessadas/")
#save_csv(data, "top1000songs.csv")
#data = get_top_artists("mais-acessadas/")
#save_csv(data, "top20_songs_by_artists.csv")

old_pd = pd.read_csv("top_forrosongs_week.csv")
new_data = get_top_songs_comparing("top.html?genre=8&slug=forro&period=5&page=top", old_pd)
save_csv(new_data, "top_forrosongs_ever.csv")