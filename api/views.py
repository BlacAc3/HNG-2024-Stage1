from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings 
WEATHER_API_KEY=settings.WEATHER_API_KEY
IP_ACCESS_TOKEN=settings.IP_ACCESS_TOKEN


# Create your views here.
def hello(request):
	location = "Not found"
	if request.method == "GET":
		visitor_name = request.GET["visitor_name"].strip('"')
		ip_address = request.META.get('REMOTE_ADDR')

		try:
			location = get_location(ip_address)
		except:
			location = None

		if location != None:
			city = location[0]
			lat = location[1][0]
			lon = location[1][1]
			temp = get_weather(lat,lon)
		else:
			city="Not Found"
			temp = 11

		greeting = f"Hello, {visitor_name}!, the temperature is {temp} degrees Celcius in {city}"
		data = {
			"client_ip":ip_address, 
			"location" : city,
			"greeting" : greeting
		}
		return JsonResponse(data)

	else:
		return JsonResponse({"error":"An Error occured"})
	

def get_location(ip_address) -> list:
	url = f'http://ipinfo.io/{ip_address}?token={IP_ACCESS_TOKEN}'
	try:
		response = requests.get(url)
		data = response.json()
		city = data["city"]
		coordinates = data["loc"]
		lat, lon = coordinates.split(",")
		loc = [lat, lon]
		return [city, loc]
	except:
		print("Error")
		return JsonResponse({"Error":"Location not found"})

def get_weather(lat, lon) -> int:
	url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'
	try:
		response = requests.get(url)
		data = response.json()
		if data["cod"] != 200:
			print("City not found")
			return 11
		temperature = data['main']['temp']
		print(temperature)
		return temperature
	except:
		print("error in requesting URL")
		return 11



	
