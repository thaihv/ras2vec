import pandas as pd 
import requests
import utils
import json
from flask import Flask,render_template

#---------Reading CSV to get latitude and Longitude---------
data = pd.read_csv("data.csv",skiprows=5,nrows=1) 

list_value = data.values.tolist()
api_key = '1TQrfWgsvqgE9LKy1zvQRrNvC9o2MOhbjx2NBZp-Uv8'

#print(list_value[0])

#Latitude and Longitude
# latitude = list_value[0][1]
# longitude = list_value[0][2]
# Here 72 : (105.7658211185765, 21.030637544689217)
# Here 73 : (105.76568726052923, 21.030685828395196)
# Here 74 : (105.7658455177934, 21.03069873872236)

#Here 36
# latitude = 21.02996368610165
# longitude = 105.76350223108444

latitude = 21.02996368610165
longitude = 105.76350223108444

# For Google Geocode
# data = utils.getlocationinformation(latitude, longitude, 'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU')
# address = data['results']

# For Here platform location services
URL = "https://revgeocode.search.hereapi.com/v1/revgeocode"
PARAMS = {
            'at': '{},{}'.format(latitude,longitude),
            'apikey': api_key
         }
r = requests.get(url = URL, params = PARAMS)  
data = r.json() 
address = data 





# place_id='EkgxOCBQaOG7kSBUcuG6p24gSOG7r3UgROG7sWMsIE3hu7kgxJDDrG5oLCBU4burIExpw6ptLCBIw6AgTuG7mWksIFZpZXRuYW0iGhIYChQKEgnxaMONvFQ0MRGGw1f-AIi43xAS'
# url = 'https://maps.googleapis.com/maps/api/geocode/json'
# #params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'address': 'Mountain View, CA'}
# #params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'latlng': '{},{}'.format(latitude,longitude)}
# params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'place_id': place_id}
# r = requests.get(url, params=params)
# results = r.json()
# address = results
#---------Flask Code for creating Map--------- 
app = Flask(__name__)
@app.route('/')

def map_func():
    return render_template('map.html',apikey=api_key,latitude=latitude,longitude=longitude,address=address)

if __name__ == '__main__':
    app.run(debug = False)