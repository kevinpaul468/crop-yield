import requests

# Define the API endpoint URL
def fetchTmpAndRain():
    location = "New%20York,%20NY"
    apikey= "HMY3LJFCPBTX77YGNHNBMKUU2"
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+location+"/?key="+apikey

    try:
        # Send GET request to the API
        response = requests.get(url)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Extract weather data from JSON response
            weather_data = response.json()
            
            # Extract temperature and rainfall data
            temperatures = []
            rainfalls = []
            for day in weather_data['days']:
                temperatures.append(day['temp'])
                rainfalls.append(day['precip'])

            # Calculate the average temperature and rainfall
            average_temperature = sum(temperatures) / len(temperatures)
            average_rainfall = sum(rainfalls) / len(rainfalls)

            print("Average Temperature:", round(average_temperature, 2), "°F")
            print("Average Rainfall:", round(average_rainfall, 2), "inches")
            return (round(average_temperature, 2), round(average_rainfall, 2))

        else:
            # Print error message if request was unsuccessful
            print("Error:", response.status_code, response.text)
            
    except Exception as e:
        # Print any exceptions that occur during the request
        print("Error:", e)
