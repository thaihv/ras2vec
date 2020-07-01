'''
Created on Jun 14, 2020

@author: thaih
'''
import cv2    
from requests.utils import quote
from skimage import io
import time
import datetime
import os
import utils
import urllib.request

styleBuildings = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleZones = quote('feature:road|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleArterialRoad = quote('feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayRoad = quote('feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayControlledAccessRoad = quote('feature:road.highway.controlled_access|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleLocalRoad = quote('feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

downloadUrl = "http://maps.googleapis.com/maps/api/staticmap?sensor=false&maptype=roadmap&style=visibility:off&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
# Test My Dinh
# lat = 21.0312246
# lon = 105.7646925
zoom = 18
tilezise = 640

def create_offlinedata(url, org_lat, org_lon, tilezise, zoom, dest_folder, tilenum):
    #Create URL
    getzoom = "&zoom=" + str(zoom)
    getsize = "&size=" + str(tilezise) + "x" + str(tilezise)
    style = "&style="
    url = url + getzoom + getsize
    styles = [styleBuildings, styleZones, styleHighwayRoad, styleLocalRoad, styleArterialRoad, styleHighwayControlledAccessRoad]

    for s in styles:
        
        if s == styleBuildings:
            childfolder = "Buildings"
        elif s == styleZones:
            childfolder = "Zones"  
        elif s == styleHighwayRoad:
            childfolder = "Highways" 
        elif s == styleLocalRoad:
            childfolder = "LocalRoads"  
        elif s == styleArterialRoad:
            childfolder = "ArterialRoads"
        elif s == styleHighwayControlledAccessRoad:
            childfolder = "ControlledAccessRoads" 
        getstyle = style + s            
        geturl = url + getstyle
        
        print('Download for ' + childfolder)
        
        for i in range(-tilenum , tilenum + 1):
            for j in range(-tilenum , tilenum + 1):
                
                directory = dest_folder + childfolder +"\\" + str(i)
                if not os.path.exists(directory):
                    os.makedirs(directory)    
                filename = directory + "\%d.png" % (j)
                if not os.path.isfile(filename):               
                    lat, lon = utils.getPointLatLngFromPixel(int(tilezise /2) + (i * tilezise), int(tilezise /2) + (j * tilezise), org_lat, org_lon, tilezise, zoom)
                    getpostition = "&center=" + str(lat) + "," + str(lon)
                    print ("X = %d; Y= %d" % (i, j), getpostition)
                    url_new = geturl + getpostition
                    
                    
#                     req = urllib.request.Request(url_new, headers={'User-Agent': 'Mozilla/5.0'})
#                     r = urllib.request.urlopen(req).read()
# 
#                     img = io.imread(r)
                    
                    img = io.imread(url_new)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    cv2.imwrite(filename, img)
                else:
                    print (filename + ' for tile (%s,%s) existed.' % (i,j) + ' Skip downloading it')
    print('Download Google Static Map OK!')

#id = 23 --> Ha noi
lat, lon, tilenum = utils.get_metadata_dowload_info(23)

gg_folder = 'C:\Download\Data\Hanoi_1\\'
start_time = time.time()
create_offlinedata(downloadUrl, lat, lon, tilezise, zoom, gg_folder, 3)
seconds = time.time() - start_time
print("--- Total time taken: %s seconds ---" % time.strftime("%H:%M:%S",time.gmtime(seconds)))