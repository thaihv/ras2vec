'''
Created on May 27, 2020

@author: thaih
'''

import requests
import json
import sys, codecs

# latitude = 21.0813699
# longitude = 105.7887625

latitude = 21.02996368610165
longitude = 105.76350223108444

place_id='EkgxOCBQaOG7kSBUcuG6p24gSOG7r3UgROG7sWMsIE3hu7kgxJDDrG5oLCBU4burIExpw6ptLCBIw6AgTuG7mWksIFZpZXRuYW0iGhIYChQKEgnxaMONvFQ0MRGGw1f-AIi43xAS'


url = 'https://maps.googleapis.com/maps/api/geocode/json'
#params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'address': 'Mountain View, CA'}
#params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'latlng': '{},{}'.format(latitude,longitude)}
params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'place_id': place_id}

r = requests.get(url, params=params)
results = r.json()

stringJson = json.dumps(results)

decoded = stringJson.encode(sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
#print(results)
#r = results['results'][0]['address_components'] [0]['long_name']
# 
#stringJson = json.dumps(results)
#sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
#print(json.dumps(results).encode("utf-8"))
print(json.dumps(results).encode("utf-8"))