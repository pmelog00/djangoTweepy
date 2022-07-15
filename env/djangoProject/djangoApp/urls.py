from django.urls import path
from . import views

app_name = "djangoApp"

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('buscarTweets',views.buscarTweets, name="buscarTweets"),
    path('login', views.login_request, name="login"),
    path('registro', views.register_request, name="registro"),
    path('logout', views.logout_request, name="logout")
]