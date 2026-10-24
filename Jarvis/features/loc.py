import webbrowser
import requests
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import geocoder


def loc(place):
    try:
        webbrowser.open("https://www.google.com/maps/place/" + place)
        geolocator = Nominatim(user_agent="jarvis_assistant_locator")
        location = geolocator.geocode(place, addressdetails=True)
        if not location:
            return None, {}, "unknown"

        target_latlng = location.latitude, location.longitude
        addr = location.raw.get('address', {})
        target_loc = {
            'city': addr.get('city', addr.get('town', addr.get('village', ''))),
            'state': addr.get('state', ''),
            'country': addr.get('country', '')
        }

        current_loc = geocoder.ip('me')
        current_latlng = current_loc.latlng if current_loc and current_loc.latlng else None

        if current_latlng:
            distance = str(great_circle(current_latlng, target_latlng))
            distance = str(distance.split(' ', 1)[0])
            distance = round(float(distance), 2)
        else:
            distance = "unknown"

        return current_loc, target_loc, distance
    except Exception as e:
        print(f"Location error: {e}")
        return None, {}, "unknown"


def my_location():
    try:
        ip_add = requests.get('https://api.ipify.org', timeout=5).text
        url = 'https://get.geojs.io/v1/ip/geo/' + ip_add + '.json'
        geo_requests = requests.get(url, timeout=5)
        geo_data = geo_requests.json()
        city = geo_data.get('city', 'Unknown City')
        state = geo_data.get('region', 'Unknown State')
        country = geo_data.get('country', 'Unknown Country')
        return city, state, country
    except Exception as e:
        print(f"My location error: {e}")
        return "Unknown", "Unknown", "Unknown"
