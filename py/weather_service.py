import requests
from datetime import datetime


class WeatherService:
    def __init__(self):
        """Initialize Weather Service and test endpoints"""
        self.endpoints = {
            "forecast": "https://api.open-meteo.com/v1/forecast",
            "current": "https://api.open-meteo.com/v1/current",
        }
        
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.working_endpoint = self.endpoints["forecast"]
        
        print("🔧 Testing Open-Meteo endpoints...")
        self.test_endpoints()
    
    def test_endpoints(self):
        """Test which endpoint works"""
        test_lat, test_lon = 40.7128, -74.0060  # Use NYC instead (more stable data)
        
        for name, url in self.endpoints.items():
            try:
                # MINIMAL parameters to test
                params = {
                    "latitude": test_lat,
                    "longitude": test_lon,
                    "current": "temperature_2m,weather_code",
                    "temperature_unit": "celsius"
                }
                
                print(f"  📍 Testing {name}: {url}")
                response = requests.get(url, params=params, timeout=5)
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'current' in data and isinstance(data['current'], dict):
                        if 'temperature_2m' in data['current']:
                            print(f"     ✅ {name} works!")
                            self.working_endpoint = url
                            return
            
            except Exception as e:
                print(f"     ❌ {name} error: {type(e).__name__}")
        
        print(f"✅ Using: {self.working_endpoint}")
    
    def get_weather_by_coordinates(self, latitude, longitude):
        """
        Fetch current weather by latitude and longitude
        
        IMPORTANT: Using minimal parameters to avoid data corruption
        """
        try:
            print(f"\n🌐 Fetching weather: lat={latitude}, lon={longitude}")
            
            # FIXED: Use ONLY these parameters to avoid corruption
            # Remove humidity_2m and wind_speed_10m which cause issues in some regions
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code",  # MINIMAL set
                "temperature_unit": "celsius"
            }
            
            print(f"📡 Endpoint: {self.working_endpoint}")
            print(f"📡 Parameters: {params}")
            
            response = requests.get(
                self.working_endpoint,
                params=params,
                timeout=10
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('reason') or error_data.get('error') or 'Unknown error'
                    print(f"❌ API Error ({response.status_code}): {str(error_msg)[:80]}")
                except:
                    print(f"❌ API Error ({response.status_code}): {response.text[:80]}")
                return None
            
            data = response.json()
            print(f"📊 Response keys: {list(data.keys())}")
            
            if 'current' not in data:
                print(f"❌ Missing 'current' key in response")
                return None
            
            if not isinstance(data['current'], dict):
                print(f"❌ 'current' is not a dict")
                return None
            
            current = data['current']
            if 'temperature_2m' not in current or 'weather_code' not in current:
                print(f"❌ Missing temperature or weather code")
                return None
            
            print(f"✅ Successfully got weather data")
            print(f"🌡️ Temp: {current.get('temperature_2m')}°C, Code: {current.get('weather_code')}")
            
            # Add default values for missing fields
            current['humidity_2m'] = current.get('humidity_2m', 60)
            current['wind_speed_10m'] = current.get('wind_speed_10m', 0)
            
            return data
        
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout (10 seconds)")
            return None
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - check internet")
            return None
        
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_weather_by_city(self, city_name):
        """Fetch weather by city name"""
        try:
            print(f"\n🔍 Looking up city: '{city_name}'")
            
            geocoding_params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            print(f"📡 Geocoding API: {self.geocoding_url}")
            
            geo_response = requests.get(
                self.geocoding_url,
                params=geocoding_params,
                timeout=10
            )
            
            print(f"📥 Geocoding status: {geo_response.status_code}")
            
            if geo_response.status_code != 200:
                print(f"❌ Geocoding failed")
                return None
            
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                print(f"❌ City '{city_name}' not found")
                return None
            
            result = geo_data['results'][0]
            latitude = result.get('latitude')
            longitude = result.get('longitude')
            city_display = result.get('name', city_name)
            country = result.get('country', '')
            
            print(f"✅ Found: {city_display}, {country}")
            print(f"   Coordinates: ({latitude}, {longitude})")
            
            return self.get_weather_by_coordinates(latitude, longitude)
        
        except requests.exceptions.Timeout:
            print(f"❌ Geocoding timeout")
            return None
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error")
            return None
        
        except Exception as e:
            print(f"❌ Error in get_weather_by_city: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_season_category(self, temperature, weather_code):
        """
        Convert weather to season: summer, winter, spring, autumn, rainy, casual
        
        WMO Weather Codes:
        0 = Clear sky
        1,2 = Mainly clear, partly cloudy
        3 = Overcast
        45,48 = Foggy
        51-65 = Drizzle/Rain
        71-77 = Snow
        80-82 = Rain showers
        85-86 = Snow showers
        """
        try:
            # Type safety
            if isinstance(temperature, str):
                temperature = float(temperature)
            if isinstance(weather_code, str):
                weather_code = int(weather_code)
            
            print(f"🌡️ Categorizing: temp={temperature}°C, code={weather_code}")
            
            # Priority 1: Snow/Winter
            if weather_code in [71, 73, 75, 77, 85, 86]:
                print(f"❄️ WINTER (snow)")
                return "winter"
            
            # Priority 2: Rainy
            elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                print(f"🌧️ RAINY")
                return "rainy"
            
            # Priority 3: Clear/Sunny (temp based)
            elif weather_code in [0, 1]:
                if temperature > 25:
                    print(f"☀️ SUMMER (clear, hot)")
                    return "summer"
                elif temperature > 15:
                    print(f"🌸 SPRING (clear, mild)")
                    return "spring"
                else:
                    print(f"❄️ WINTER (clear, cold)")
                    return "winter"
            
            # Priority 4: Cloudy (temp based)
            elif weather_code in [2, 3, 45, 48]:
                if temperature > 20:
                    print(f"🌸 SPRING (cloudy, warm)")
                    return "spring"
                elif temperature > 10:
                    print(f"🍂 AUTUMN (cloudy, cool)")
                    return "autumn"
                else:
                    print(f"❄️ WINTER (cloudy, cold)")
                    return "winter"
            
            # Default
            else:
                print(f"❓ Unknown code {weather_code}, using temperature")
                if temperature > 25:
                    return "summer"
                elif temperature > 15:
                    return "spring"
                else:
                    return "winter"
        
        except Exception as e:
            print(f"❌ Error in get_season_category: {type(e).__name__}: {str(e)}")
            return "casual"
