'''
Created on May 11, 2020

@author: thaih
'''
import cv2
import numpy as np     
from requests.utils import quote
from skimage import io
import math

import os
import utils
import globalmaptiles as gt
from osgeo import ogr

tile_dir = 'C:\Download\Data\CG'
level = 18

low_yellow = (0,9,0)
high_yellow = (23,18,255)

low_gray = (0,0,0)
high_gray = (100,5,250)

range_sets = ([low_yellow, high_yellow], [low_gray, high_gray])
kernel = np.ones((3,3),np.uint8)
def process_buildingsdata(data_folder_path, level = 18, tileformat = 'png'):
    # r=root, d=directories, f = files
    for r, d, f in os.walk(data_folder_path):
        for dir_name in d:
            if dir_name == str(level):
                level_dir = data_folder_path + "\\"+ dir_name
                for root, dirs, files in os.walk(level_dir):
                    for file in files:
                        if file.endswith(tileformat):
                            tile_name = os.path.join(root, file) 
                            img = cv2.imread(os.path.join(root, file))
                            print(img.shape)
                            # draw gray box around image to detect edge buildings
                            h,w = img.shape[:2]
                            cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)
                            print('Processing ' + tile_name)
                            cv2.imshow(tile_name, img) 
                            # convert image to HSV
                            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                            ranges_coi = utils.set_display_range(hsv, range_sets)
                            cv2.imshow('Display Ranges', ranges_coi)
                            # remove remain noise by applying dilation then erosion or vice versa 
                            walls = utils.remove_noise(ranges_coi, kernel)
                            cv2.imshow('Walls', walls)
                            # find contours and create respective polygons 
                            imgResult, r_polygons = utils.find_rasterpolygons(img, walls)
                            cv2.imshow('Buildings', imgResult)
#                             ds = gdal.Open(tile_name)
#                             for p in r_polygons:
#                                 print("Polygon:")
#                                 for j in p:
#                                     xp, yp = utils.pixel2coord(ds, int(j[0][0]), int(j[0][1]))
#                                     print(int(j[0][0]), int(j[0][1]), "World --->", xp, yp)
                            # Exiting the window if 'q' is pressed on the keyboard. 
                            if cv2.waitKey(0) & 0xFF == ord('q'): 
                                cv2.destroyAllWindows() 


styleBuildings = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
#full road is used for creating zones
styleZones = quote('feature:road|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

styleArterialRoad = quote('feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayRoad = quote('feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayControlledAccessRoad = quote('feature:road.highway.controlled_access|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleLocalRoad = quote('feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

#My Dinh
lat = 21.0312246
lon = 105.7646925
# next X
# lat = 21.0312246
# lon = 105.76812572753906

# lat = 21.0399554
# lon = 105.7920228

# lat = 21.028240
# lon = 105.771832

# Cau vuot Mai Dich
# lat = 21.035628
# lon = 105.781349

#test highway
# lat = 21.0813699
# lon = 105.7887625
# highway next Y + 1
# lat = 21.07816645652331
# lon = 105.7887625
# highway next X - 1, Y + 1
# lat = 21.07816645652331
# lon = 105.78532927246094
# highway next Y + 2
# lat = 21.074962944007055
# lon = 105.7887625
zoom = 18

style = styleLocalRoad

if style == styleBuildings:     
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Buildings.shp'
elif style == styleZones:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Zones.shp'
elif style == styleHighwayRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Highways.shp'
elif style == styleLocalRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Localroads.shp'    
    
maptype_satellite = 'satellite'
maptype_roadmap = 'roadmap'
maptype_terrain = 'terrain'
maptype_hybrid  = 'hybrid'

fullTerrain = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(18) + "&maptype=" + maptype_terrain + "&size=640x640&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullSatellite = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(18) + "&maptype=" + maptype_satellite + "&size=640x640&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullRoadMap = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(18) + "&maptype=" + maptype_roadmap + "&size=640x640&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullHybrid = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(18) + "&maptype=" + maptype_hybrid + "&size=640x640&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"

workingUrl = "http://maps.googleapis.com/maps/api/staticmap?center=" + str(lat) + "," + str(lon) + "&zoom=" + str(18) + "&sensor=false&size=640x640&maptype=roadmap&style=visibility:off&style=" + style + "&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
print(fullRoadMap)
print(workingUrl)


fullSatelliteImg = io.imread(fullSatellite)
fullSatelliteImg = cv2.cvtColor(fullSatelliteImg, cv2.COLOR_BGR2RGB)

fullRoadmapImg = io.imread(fullRoadMap)
fullRoadmapImg = cv2.cvtColor(fullRoadmapImg, cv2.COLOR_BGR2RGB)
    
def fetch_onlinebuildingsdata(url, dest_img):
    buildings = []
    img = io.imread(url)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #print(img.shape)
    h,w = img.shape[:2]
    cv2.rectangle(img,(0,0),(w-1,h-1), (0,0,255),1)
    #cv2.imshow('RECTANGLE', img) 
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow('HSV', img)
    
    low = (0,11,0)
    high = (179,255,255)
    # create masks
    mask = cv2.inRange(hsv, low, high)
    cv2.imshow("REMOVE GOOGLE TRADE MARK", mask)
    contours, hier = cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for x in range(len(contours)):
        print()
        # if a contour has not contours inside of it, draw the shape filled
        c = hier[0][x][2]
        if c == -1:
            #cv2.drawContours(fullSatelliteImg,[contours[x]],0,(0,0,255),-1)
            cnt = [contours[x]][0]
            if cv2.contourArea(cnt) > 80:
                cnt = [contours[x]][0]
                epsilon = 0.0001*cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
#                 cv2.drawContours(fullSatelliteImg, [approx], -1, (0,0,255), -1)
#                 cv2.drawContours(fullRoadmapImg, [approx], -1, (0,0,255), -1)
                buildings.append(approx)             
    # draw the outline of all contours
    for cnt in contours:
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
    return buildings


def fetch_onlineroaddata(url, dest_img):
    roads = []
    img = io.imread(url)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow('HSV', img)
    
    low = (0,11,0)
    high = (179,255,255)
    # create masks
    mask = cv2.inRange(hsv, low, high)
    cv2.imshow("REMOVE GOOGLE TRADE MARK", mask)
    
    # Create skeleton for lines to get more accurately
    thinned = cv2.ximgproc.thinning(mask)
    
    contours, hier = cv2.findContours(thinned,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # draw the outline of all contours
    for cnt in contours:
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
            roads.append(cnt)
    return roads
def convert_pixelarray2worldcoordinate(pointsarray, centerlat, centerlon, zoom = 18, tilezise = 640):
    
    gis_pointsarray = []
    
    mercator = gt.GlobalMercator(tilezise)
    mx, my = mercator.LatLonToMeters(centerlat,centerlon)
    print ("Mecator --> LatLonToMeters:  Google:900913 [%s , %s]" % (mx, my))

    px, py = mercator.MetersToPixels(mx, my, zoom)
    tx, ty = mercator.PixelsToTile(px, py)
    print ("Mecator --> MetersToPixels--> Tiles:  Pixel [%s , %s] at Tile [%s , %s]" % (px, py, tx, ty))
    
    # Calculate next tile from X
    
    newLatCenter, newLonCenter = utils.getPointLatLngFromPixel(320 - 640, 320, centerlat, centerlon, tilezise, zoom)
    
    print ("Center of next is [%s , %s]" % (newLatCenter, newLonCenter))
    
    for n, p in enumerate(pointsarray):
        #print('Polygon {}: {}'.format(n, p))
        points = []
        for j in p:
            lat, lon = utils.getPointLatLngFromPixel(int(j[0][0]),int(j[0][1]), centerlat, centerlon, tilezise, zoom)
            points.append([lon, lat])
        gis_pointsarray.append(points)
    return gis_pointsarray
    
def create_polygons_shapefile(polygons):    
    gis_polygons = convert_pixelarray2worldcoordinate(polygons, lat , lon, zoom)
    utils.write_polygons2shpfile(outputshpfile, gis_polygons)
    return outputshpfile
def create_polyline_shapefile(polylines):    
    gis_polylines = convert_pixelarray2worldcoordinate(polylines, lat , lon, zoom)
    utils.write_linestring2shpfile(outputshpfile, gis_polylines)
    return outputshpfile    

created_file = None
if (style == styleBuildings) or (style == styleZones):    
    # Create shape file for buildings and zones in polygons    
    building_polygons = fetch_onlinebuildingsdata(workingUrl, fullRoadmapImg)
    created_file = create_polygons_shapefile(building_polygons)
else:
    # Create shape file for roads in poly lines 
    roads = fetch_onlineroaddata(workingUrl,fullRoadmapImg)
    created_file = create_polyline_shapefile(roads)
    

# if created_file is not None:
#     utils.display_shpinfo(created_file)
    
#process_buildingsdata(tile_dir, level)

cv2.imshow('Satellite', fullSatelliteImg)
cv2.imshow('Roadmap', fullRoadmapImg)
if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows() 
    

