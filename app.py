from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TMDB_API_KEY = "516adf1e1567058f8ecbf30bf2eb9378"  # <- coloca tua chave TMDb aqui
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def buscar_filmes_apple_tv_populares():
    url_populares = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR&page=1'
    resp = requests.get(url_populares)
    dados = resp.json()
    filmes = dados.get('results', [])[:24]  # só os 24 primeiros
    return filmes


    filmes_apple = []
    for filme in filmes:
        movie_id = filme['id']
        url_providers = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}'
        prov_resp = requests.get(url_providers).json()
        providers_br = prov_resp.get('results', {}).get('BR', {})
        if 'flatrate' in providers_br:
            providers_ids = [p['provider_id'] for p in providers_br['flatrate']]
            if 2552 in providers_ids:  # 2552 é Apple TV+
                filmes_apple.append(filme)
                if len(filmes_apple) >= 10:
                    break
    return filmes_apple

def pesquisar_filmes_apple_tv(search):
    url_search = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={requests.utils.quote(search)}&page=1"
    resp = requests.get(url_search)
    dados = resp.json()
    filmes = dados.get('results', [])
    return filmes


    filmes_apple = []
    for filme in filmes:
        movie_id = filme['id']
        url_providers = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}'
        prov_resp = requests.get(url_providers).json()
        providers_br = prov_resp.get('results', {}).get('BR', {})
        if 'flatrate' in providers_br:
            providers_ids = [p['provider_id'] for p in providers_br['flatrate']]
            if 2552 in providers_ids:
                filmes_apple.append(filme)
    return filmes_apple

def buscar_filme_no_megafilmes(titulo):
    # Busca no site https://megafilmeshdz.cyou/?s=titulo
    url = f"https://megafilmeshdz.cyou/?s={titulo.replace(' ', '+')}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        article = soup.select_one("article")
        if not article:
            return None

        link_tag = article.find("a", href=True)
        capa_tag = article.find("img")

        if not link_tag or not capa_tag:
            return None

        filme_url = link_tag['href']
        capa = capa_tag['src']

        # Pegar iframe do vídeo
        filme_page = requests.get(filme_url, headers=HEADERS, timeout=10)
        filme_page.raise_for_status()
        filme_soup = BeautifulSoup(filme_page.text, 'html.parser')
        iframe = filme_soup.find("iframe")
        video_link = iframe["src"] if iframe else None

        return {
            "titulo": titulo,
            "url": video_link,
            "capa": capa,
            "pagina": filme_url
        }
    except Exception:
        return None

@app.route('/')
def index():
    search = request.args.get('search')
    if search:
        filmes = pesquisar_filmes_apple_tv(search)
    else:
        filmes = buscar_filmes_apple_tv_populares()
    return render_template("index.html", filmes=filmes, search=search)

@app.route('/filme')
def filme():
    titulo = request.args.get('titulo')
    if not titulo:
        return "Filme não especificado.", 400

    filme_detalhes = buscar_filme_no_megafilmes(titulo)
    if not filme_detalhes:
        return render_template("filme.html", error="Filme não encontrado no megafilmeshdz.cyou.")

    return render_template("filme.html", filme=filme_detalhes)

if __name__ == '__main__':
    app.run(debug=True)




