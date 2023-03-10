from django.urls import path
from . import views

urlpatterns = [
    path('<int:pelicula_id>/', views.recomendacion_peliculas, name='recomendacion_peliculas'),
    path('', views.lista_peliculas, name='lista_peliculas'),
]