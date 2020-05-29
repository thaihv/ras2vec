'''
Created on May 27, 2020

@author: thaih
'''
import requests
import pandas as pd 

#To read 6th row data
data = pd.read_csv("data.csv",skiprows=5,nrows=1) 

#To print the values
print(data)

#To convert values into list
list_value = data.values.tolist()

#Latitude and Longitude
latitude = list_value[0][1]
longitude = list_value[0][2]
# api-endpoint
URL = "https://revgeocode.search.hereapi.com/v1/revgeocode"

#API key
api_key = '1TQrfWgsvqgE9LKy1zvQRrNvC9o2MOhbjx2NBZp-Uv8'

# Defining a params dictionary for the parameters to be sent to the API 
PARAMS = {
            'at': '{},{}'.format(latitude,longitude),
            'apikey': api_key
         }

# Sending get request and saving the response as response object 
r = requests.get(url = URL, params = PARAMS) 
  
# Extracting data in json format 
data = r.json() 

#Taking out title from JSON
address = data['items'][0]['title'] 

print(address)