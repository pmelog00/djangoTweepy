from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
def homepage(request):
	return render(request=request, template_name='main/home.html')

def login_request(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, username)
			return redirect('djangoApp:homepage')
		else:
			messages.info(request, 'El nombre de usuario o la contraseña son incorrectos')
	
	context = {}
	return render(request, "main/login.html", context)

def register_request(request):
	form = NewUserForm()

	if request.method == 'POST':
		form = NewUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request,'Cuenta registrada para ' + user)

			return redirect("login")

	context = {'form':form}
	return render(request, "main/register.html", context)
		
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect("djangoApp:homepage")