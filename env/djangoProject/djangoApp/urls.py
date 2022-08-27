from django.urls import path
from . import views

app_name = "djangoApp"

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('buscarTweets',views.buscarTweets, name="buscarTweets"),
    path('seguidores',views.seguidores, name="seguidores"),
    path('scrapping_csv',views.scrapping_csv, name="scrapping_csv"),
    path('streaming_csv',views.streaming_csv, name="streaming_csv"),
    path('volumen_tweets',views.volumen_tweets, name="volumen_tweets"),
    path('historial_busquedas',views.historial_busquedas, name="historial_busquedas"),
    path('login', views.login_request, name="login"),
    path('registro', views.register_request, name="registro"),
    path('logout', views.logout_request, name="logout")
]