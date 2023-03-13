from django.shortcuts import render
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def recomendacion_peliculas(request, pelicula_id):
    pelicula = get_pelicula(pelicula_id)
    peliculas_similares = recomendar_api(pelicula_id)
    peli = recomendar_sklearn(pelicula)
    peliculas_similares.extend(peli)
    videos = get_pelicula_video(pelicula_id)
    return render(request, 'recomendacion.html', 
                  {'pelicula': pelicula, 
                   'peliculas_similares': peliculas_similares,
                   'videos': videos})

def recomendar_sklearn(pelicula):
    url_generos = "https://api.themoviedb.org/3/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'es'}
    todas_peliculas = buscar_por_genero(pelicula['genres'])
    peliculas = [p for p in todas_peliculas if p['id'] != pelicula['id']]
    vectorizer = TfidfVectorizer()
    descripciones = [p['overview'] for p in peliculas]
    matriz_caracteristicas = vectorizer.fit_transform(descripciones)
    pelicula_matriz = vectorizer.transform([pelicula['overview']])
    similitud_cos = cosine_similarity(matriz_caracteristicas, pelicula_matriz)
    indices_similares = similitud_cos.argsort(axis=0)[-5:]
    peliculas_similares = [peliculas[idx[0]] for idx in indices_similares]
    response_generos = requests.get(url_generos, params=params)
    generos = response_generos.json()['genres']
    for p_similar in peliculas_similares:
        categoria_ids = p_similar['genre_ids']
        p_similar['generos'] = [genero['name'] for genero in generos if genero['id'] in categoria_ids]
    return peliculas_similares

def recomendar_api(pelicula_id):
    url = f'https://api.themoviedb.org/3/movie/{pelicula_id}/recommendations'
    url_generos = "https://api.themoviedb.org/3/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'es','page':1, 'limit': 5}
    response = requests.get(url, params=params)
    peliculas_similares = response.json()['results'][:5]
    response_generos = requests.get(url_generos, params=params)
    generos = response_generos.json()['genres']
    for pelicula in peliculas_similares:
        categoria_ids = pelicula['genre_ids']
        pelicula['generos'] = [genero['name'] for genero in generos if genero['id'] in categoria_ids]
    return peliculas_similares

def lista_peliculas(request):
    if 'q' in request.GET:
        query = request.GET['q']
        peliculas = buscar_peliculas(query)
        return render(request, 'busqueda.html', {'peliculas': peliculas, 'busco': True})
    else:
        peliculas_popular = get_peliculas_genero("popular")
        peliculas_mejor = get_peliculas_genero("top_rated")
        peliculas_proximamente = get_peliculas_genero("upcoming")
        return render(request, 'lista.html', 
                      {'peliculas_popular': peliculas_popular,
                       'peliculas_mejor': peliculas_mejor,
                       'peliculas_proximamente': peliculas_proximamente})

def get_peliculas_genero(tipo):
    url = f'https://api.themoviedb.org/3/movie/{tipo}'
    url_generos = "https://api.themoviedb.org/3/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'es'}
    response_peliculas = requests.get(url, params=params)
    peliculas = response_peliculas.json()['results']
    response_generos = requests.get(url_generos, params=params)
    generos = response_generos.json()['genres']
    for pelicula in peliculas:
        categoria_ids = pelicula['genre_ids']
        pelicula['generos'] = [genero['name'] for genero in generos if genero['id'] in categoria_ids]
    return peliculas

def buscar_peliculas(query):
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {'api_key': TMDB_API_KEY, 'language': 'es', 'query': query}
    response = requests.get(url, params=params)
    peliculas = response.json()['results']
    return peliculas

def get_pelicula(id):
    url = f'https://api.themoviedb.org/3/movie/{id}'
    url_generos = "https://api.themoviedb.org/3/genre/movie/list"
    params = {'api_key': TMDB_API_KEY, 'language': 'es'}
    response = requests.get(url, params=params)
    pelicula = response.json()
    response_generos = requests.get(url_generos, params=params)
    generos = response_generos.json()['genres']
    categoria_ids = pelicula['genres']
    pelicula['generos'] = [genero['name'] for genero in generos if genero['id'] in categoria_ids]
    return pelicula

def buscar_por_genero(generos):
    generos_id = [genero['id'] for genero in generos]
    url = 'https://api.themoviedb.org/3/discover/movie'
    params = {'api_key': TMDB_API_KEY, 'language': 'es', 'sort_by': 'popularity.desc', 'with_genres': generos_id}
    response = requests.get(url, params=params)
    resultados = response.json()['results']
    return resultados

def get_pelicula_video(id):
    url = f'https://api.themoviedb.org/3/movie/{id}/videos'
    params = {'api_key': TMDB_API_KEY, 'language': 'es'}
    response = requests.get(url, params=params)
    videos = response.json()['results']
    if response.status_code == 200:
        return videos
    else:
        return None