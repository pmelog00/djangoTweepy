import tweepy
import numpy as np
import pandas as pd
import json
import datetime
import csv
import time

from django.conf import settings
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse



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
					tweets = client.search_recent_tweets(query=tema + " -is:retweet", tweet_fields=['created_at'], max_results=maximo)
				except tweepy.errors.BadRequest:
					print("error")		    
				context = {
					'tweets' : tweets,
				}
				return render(request, 'main/buscarTweets.html', context)
		return render(request=request, template_name='main/buscarTweets.html')
	else:
		return redirect('djangoApp:login')
def scrapping_csv(request):
	if request.method == 'POST':
		print(request.POST)
		keywords = request.POST['keywords']
		maximo = request.POST['max']
		keywords_replace = keywords.replace("-"," OR ")
		if request.POST['idioma'] == "option1":
			idioma = "es"
		else:
			idioma = "en" 
		client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
		text_tweet_check = request.POST.get('tweet_text', False)
		creation_date_check = request.POST.get('creation_date', False)
		id_author_check = request.POST.get('id_author', False)
		conv_id_check = request.POST.get('conv_id', False)
		username_check = request.POST.get('user_name',False)
		name_check = request.POST.get('name',False)
		likes_check = request.POST.get('number_likes',False)
		retweets_check = request.POST.get('number_retweets',False)
		replies_check = request.POST.get('number_replies',False)
		device_check = request.POST.get('device',False)

		try:
			tweets = client.search_recent_tweets(query=keywords + " -is:retweet " + "lang:" + idioma, user_fields=['description','username','name','profile_image_url'], expansions=['author_id'], tweet_fields=['created_at','author_id','conversation_id','public_metrics','source'], max_results=maximo)
			users = {u["id"]: u for u in tweets.includes['users']}		
		except tweepy.errors.BadRequest:
			print("error al acceder a la API")

		response = HttpResponse(
        	content_type='text/csv',
        	headers={'Content-Disposition': 'attachment; filename=scrapping_'+ str(datetime.datetime.now())+'.csv'},
    	)
		writer = csv.writer(response)
		for tweet in tweets.data:
			row = [tweet.id]
			if text_tweet_check != False:
				row.append(tweet.text.replace('\n',' '))
			if creation_date_check != False:
				row.append(tweet.created_at)
			if id_author_check != False:
				row.append(tweet.author_id)
			if conv_id_check != False:
				row.append(tweet.conversation_id)
			if username_check != False:
				if users[tweet.author_id]:
					user = users[tweet.author_id]
					row.append(user.username)
			if name_check != False:
				if users[tweet.author_id]:
					user = users[tweet.author_id]
					row.append(user.name)
			if likes_check != False:
				row.append(tweet.public_metrics.get("like_count"))
			if retweets_check != False:
				row.append(tweet.public_metrics.get("retweet_count"))
			if replies_check != False:
				row.append(tweet.public_metrics.get("reply_count"))
			if device_check != False:
				row.append(tweet.source)	
			writer.writerow(row)	
		
		return response
	else:
		return render(request=request, template_name='main/scrapearcsv.html')
class MyStream(tweepy.Stream):
	def on_connect(self):
		print("Stream connected")
	def on_status(self, status):
		row = [status.id]
		if hasattr(status, "retweeted_status"):  # Check if Retweet
			try:
				row.append(status.retweeted_status.extended_tweet["full_text"].replace('\n',' '))			
			except AttributeError:
				row.append(status.retweeted_status.text.replace('\n',' '))	
		else:
			try:
				row.append(status.extended_tweet["full_text"].replace('\n',' '))
			except AttributeError:
				row.append(status.text.replace('\n',' '))
		with open('djangoApp/resources/OutputStreaming.csv', 'a', encoding='utf-8') as f:
			writer = csv.writer(f)
			writer.writerow(row)

printer = MyStream(
        settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
        settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET
    )

def streaming_csv(request):
	
	if 'start' in request.POST:
		with open('djangoApp/resources/OutputStreaming.csv', 'w', encoding='utf-8') as f:
			writer = csv.writer(f)
		printer.filter(track=["bitcoin"], threaded=True, languages=["en", "es"])		
		return render(request=request, template_name='main/streamingcsv.html')
	elif 'finish' in request.POST:
		printer.disconnect()
		"""
		keywords = request.POST['keywords']
		maximo = request.POST['max']
		keywords_replace = keywords.replace("-"," OR ")
		if request.POST['idioma'] == "option1":
			idioma = "es"
		else:
			idioma = "en" 
		client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
		id_tweet = request.POST['id_tweet']
		text_tweet = request.POST['text']
		print(id_tweet,text_tweet)
		
		try:
			tweets = client.search_recent_tweets(query=keywords + " -is:retweet " + "lang:" + idioma, user_fields=['description','username','name','profile_image_url'], expansions=['author_id'], tweet_fields=['created_at','author_id','conversation_id'], max_results=maximo)
			users = {u["id"]: u for u in tweets.includes['users']}
			for tweet in tweets.data:
				if users[tweet.author_id]:
					user = users[tweet.author_id]
					print(user.profile_image_url)
				print(tweet.created_at, tweet.text, tweet.id, tweet.author_id, tweet.conversation_id)
		except tweepy.errors.BadRequest:
			print("error")

		response = HttpResponse(
        	content_type='text/csv',
        	headers={'Content-Disposition': 'attachment; filename=scrapping'+ str(datetime.datetime.now())+'.csv'},
    	)
		writer = csv.writer(response)
		for tweet in tweets.data:

			writer.writerow([tweet.text,tweet.created_at])
		
		return response
		"""
		return render(request=request, template_name='main/streamingcsv.html')
	else:
		return render(request=request, template_name='main/streamingcsv.html')
def seguidores(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			username = request.POST['username']

			if username:
				client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)
				try:
					user = client.get_user(username=username)
					lista_seguidores = client.get_users_followers(id=user.data.id)
				except tweepy.errors.BadRequest:
					print("error")		    
				context = {
					'lista_seguidores' : lista_seguidores
				}
				return render(request, 'main/seguidores.html', context)
		return render(request=request, template_name='main/seguidores.html')
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