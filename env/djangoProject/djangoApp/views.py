import tweepy
import numpy as np
import pandas as pd
import json

from django.conf import settings
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm



# Create your views here.
def homepage(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			username = request.POST['username']
			quantity = request.POST['quantity']
			if username and quantity:
				auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
				auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)				
					
				api = tweepy.API(auth)
				try:
					# Devuelve los últimos tweets según el número en el count que pongamos del usuario que indiquemos
					tweets = api.user_timeline(screen_name=username, count=quantity)
					df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
					df['Fecha'] = np.array([tweet.created_at for tweet in tweets])
					#df['Texto'] = np.array([tweet.text for tweet in tweets])
					#print(df['Texto'])
					df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
					#print(df['Likes'])
					df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
					likes = pd.Series(data=df['Likes'].values, index=df['Fecha'])					
					retweets = pd.Series(data=df['Retweets'].values, index=df['Fecha'])
				except tweepy.errors.NotFound:
					print("error")
				
				#print(df['Fecha'])
				fechasString = df['Fecha'].dt.strftime('%d/%m/%Y').tolist()
				fechasString = ",".join(fechasString)
				fechas=fechasString.split(",")				
				likes = df['Likes'].tolist()
				retweets = df['Retweets'].tolist()	
				print(retweets)		    
				context = {
					'fechas' :  fechas,
					'likes' : likes,
					'retweets' : retweets,
				}
				return render(request, 'main/home.html', context)
		return render(request=request, template_name='main/home.html')
	else:
		return redirect('djangoApp:login')
def buscarTweets(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			tema = request.POST['tema']
			maximo = request.POST['max']
			if tema and maximo:
				client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
				try:
					tweets = client.search_recent_tweets(query= tema + " -is:retweet", tweet_fields=['created_at'], max_results=maximo)
				except tweepy.errors.BadRequest:
					print("error")		    
				context = {
					'tweets' : tweets,
				}
				return render(request, 'main/buscarTweets.html', context)
		return render(request=request, template_name='main/buscarTweets.html')
	else:
		return redirect('djangoApp:login')
def login_request(request):
	if request.user.is_authenticated:
		return redirect('djangoApp:homepage')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('djangoApp:homepage')
			else:
				messages.info(request, 'El nombre de usuario o la contraseña son incorrectos')
		
		context = {}
		return render(request, "main/login.html", context)

def register_request(request):
	if request.user.is_authenticated:
		return redirect('djangoApp:homepage')
	else:
		form = NewUserForm()

		if request.method == 'POST':
			form = NewUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request,'Cuenta registrada para ' + user)

				return redirect("djangoApp:login")
			else:
				for error in form.errors:	
					if error == 'username':	
						messages.info(request, 'El nombre de usuario no es válido')
					elif error=='password2':
						messages.info(request, 'Las contraseñas no son iguales o no tiene un formato válido; recuerde que no puede ser similar a su nombre de usuario, tiene que tener una longitud de al menos 8 caracteres y no puede ser muy común ni tampoco solo numérica')

		context = {'form':form}
		return render(request, "main/register.html", context)
		
def logout_request(request):
	logout(request)
	messages.info(request, "Has cerrado la sesión correctamente")
	return redirect("djangoApp:login")