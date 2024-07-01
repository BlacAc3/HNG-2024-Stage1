from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from django.conf import settings
from .views import get_location, get_weather

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.hello_url = reverse('hello')  # Ensure your URL name is 'hello'
        self.valid_ip = '8.8.8.8'
        self.invalid_ip = '0.0.0.0'
        self.visitor_name = 'John Doe'
        self.weather_api_key = 'test_api_key'
        self.ip_access_token = 'test_ip_token'

    @patch('api.views.get_location')
    @patch('api.views.get_weather')
    def test_hello_view(self, mock_get_weather, mock_get_location):
        mock_get_location.return_value = ('Mountain View', 37.386, -122.0838)
        mock_get_weather.return_value = 20

        response = self.client.get(self.hello_url, {'visitor_name': self.visitor_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['location'], 'Mountain View')
        self.assertIn('Hello, John Doe!', response.json()['greeting'])
        
        mock_get_location.assert_called_once()
        mock_get_weather.assert_called_once()

    @patch('api.views.get_location')
    @patch('api.views.get_weather')
    def test_hello_view_location_not_found(self, mock_get_weather, mock_get_location):
        mock_get_location.return_value = (None, None, None)
        mock_get_weather.return_value = 11

        response = self.client.get(self.hello_url, {'visitor_name': self.visitor_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['location'], 'Not Found')
        self.assertIn('Hello, John Doe!', response.json()['greeting'])


class FunctionsTestCase(TestCase):
    @patch('geocoder.ip')
    def test_get_location_valid_ip(self, mock_geocoder_ip):
        mock_geocoder_ip.return_value.ok = True
        mock_geocoder_ip.return_value.city = 'Mountain View'
        mock_geocoder_ip.return_value.latlng = [37.386, -122.0838]

        city, lat, lon = get_location('8.8.8.8')
        self.assertEqual(city, 'Mountain View')
        self.assertEqual(lat, 37.386)
        self.assertEqual(lon, -122.0838)

    @patch('geocoder.ip')
    def test_get_location_invalid_ip(self, mock_geocoder_ip):
        mock_geocoder_ip.return_value.ok = False

        city, lat, lon = get_location('0.0.0.0')
        self.assertIsNone(city)
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    @patch('requests.get')
    def test_get_weather_valid_location(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'cod': 200,
            'main': {'temp': 25}
        }
        mock_requests_get.return_value = mock_response

        temp = get_weather(37.386, -122.0838)
        self.assertEqual(temp, 25)

    @patch('requests.get')
    def test_get_weather_invalid_location(self, mock_requests_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'cod': 404
        }
        mock_requests_get.return_value = mock_response

        temp = get_weather(0.0, 0.0)
        self.assertEqual(temp, 11)
