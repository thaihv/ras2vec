'''
Created on May 11, 2020

@author: thaih
'''
import cv2
import numpy as np     
from requests.utils import quote
from skimage import io, filters
from skimage.morphology import skeletonize, thin, medial_axis
from scipy import ndimage 
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import time
import os
import utils
from pathlib import Path
from skimage.util import invert


tile_dir = 'C:\Download\Data\CG'
level = 18

low_yellow = (0,9,0)
high_yellow = (23,18,255)

low_gray = (0,0,0)
high_gray = (100,5,250)

range_sets = ([low_yellow, high_yellow], [low_gray, high_gray])
kernel = np.ones((3,3),np.uint8)

def process_offlinedata(input_data_folder_path, output_data_folder_path, org_lat , org_lon, tilesize = 640, zoom = 18, tileformat = 'png'):
    # r=root, d=directories, f = files
    for r, d, f in os.walk(input_data_folder_path):
        for dir_name in d:
            level_dir = input_data_folder_path + "\\"+ dir_name
            for root, dirs, files in os.walk(level_dir):
                for file in files:
                    if file.endswith(tileformat):
                        tile_name = os.path.join(root, file) 
                        X = os.path.basename(os.path.dirname(tile_name))
                        Y = os.path.splitext(os.path.split(tile_name)[1])[0]
                        directory = output_data_folder_path + dir_name + "\\"
                        if not os.path.exists(directory):
                            os.makedirs(directory)  
                        outputshpfile = directory + X + '_' + Y + '_' + dir_name +'.shp'
                        print('Processing ' + tile_name + ": --> " + outputshpfile)
                        i = int(X)
                        j = int(Y)
                        lat, lon = utils.getPointLatLngFromPixel(int(tilesize /2) + (i * tilesize), int(tilesize /2) + (j * tilesize), org_lat, org_lon, tilesize, zoom)
                        if dir_name == str('Buildings') or dir_name == str('Zones'):                            
                            building_polygons = utils.fetch_buildings_or_zonesdata(tile_name)
                            gis_polygons = convert_pixelarrays2worldcoordinate(building_polygons, lat , lon, zoom)
                            
                            minx, miny, maxx, maxy = calculate_bbox_tiles(lat, lon, tilesize, zoom)
                            theorybbox = Polygon([(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx), (miny, minx)])
                            utils.write_polygons2shpfile(outputshpfile, gis_polygons, theorybbox)
                            
                        elif dir_name == str('Highways') or dir_name == str('LocalRoads') or dir_name == str('ArterialRoads') or dir_name == str('ControlledAccessRoads'):
                            roads, jointpoints = utils.fetch_roadsdata(tile_name)
                            
                            gis_polylines = convert_pixelarrays2worldcoordinate(roads, lat , lon, zoom)

                            utils.write_linestring2shpfile(outputshpfile, gis_polylines, None)

                        
                        #utils.display_shpinfo(outputshpfile)


                            
styleBuildings = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
#full road is used for creating zones
styleZones = quote('feature:road|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

styleArterialRoad = quote('feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayRoad = quote('feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayControlledAccessRoad = quote('feature:road.highway.controlled_access|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleLocalRoad = quote('feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

# Center My Dinh (X,Y)
# lat = 21.0312246
# lon = 105.7646925
# (X + 1, Y)
# lat = 21.0312246
# lon = 105.76812572753906
# (X + 1, Y + 1)
# lat = 21.028020076956896
# lon = 105.76812572753906
# (X, Y + 1)
# lat = 21.028020076956896
# lon = 105.7646925


# Cau vuot Mai Dich
# lat = 21.035628
# lon = 105.781349

#test highway
# lat = 21.0813699
# lon = 105.7887625

# Ha Noi Center
lat = 20.97503280639646
lon = 105.65287399291995


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
imagesize = 640

style = styleBuildings
tablename = 'Buildings'

if style == styleBuildings:     
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Buildings.shp'
    tablename = 'Buildings'
elif style == styleZones:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Zones.shp'
    tablename = 'Zones'
elif style == styleHighwayRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Highways.shp'
    tablename = 'Highways'
elif style == styleLocalRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Localroads.shp'
    tablename = 'Localroads'  
elif style == styleHighwayControlledAccessRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_HighwayControlledAccess.shp'
    tablename = 'HighwayControlled'
elif style == styleArterialRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Arterialroads.shp'
    tablename = 'Arterialroads'
    
maptype_satellite = 'satellite'
maptype_roadmap = 'roadmap'
maptype_terrain = 'terrain'
maptype_hybrid  = 'hybrid'

getpostition = "&center=" + str(lat) + "," + str(lon)
getzoom = "&zoom=" + str(zoom)
getsize = "&size=" + str(imagesize) + "x" + str(imagesize)


fullTerrain = "https://maps.googleapis.com/maps/api/staticmap?maptype=" + maptype_terrain + "&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullSatellite = "https://maps.googleapis.com/maps/api/staticmap?maptype=" + maptype_satellite + "&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullRoadMap = "https://maps.googleapis.com/maps/api/staticmap?maptype=" + maptype_roadmap + "&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
fullHybrid = "https://maps.googleapis.com/maps/api/staticmap?maptype=" + maptype_hybrid + "&style=feature:all&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"

downloadUrl = "http://maps.googleapis.com/maps/api/staticmap?sensor=false&maptype=roadmap&style=visibility:off&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
workingUrl = "http://maps.googleapis.com/maps/api/staticmap?sensor=false&maptype=roadmap&style=visibility:off&style=" + style + "&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
print(fullRoadMap)
print(workingUrl)


fullSatelliteImg = io.imread(fullSatellite + getpostition + getzoom + getsize)
fullSatelliteImg = cv2.cvtColor(fullSatelliteImg, cv2.COLOR_BGR2RGB)

fullRoadmapImg = io.imread(fullRoadMap + getpostition + getzoom + getsize)
fullRoadmapImg = cv2.cvtColor(fullRoadmapImg, cv2.COLOR_BGR2RGB)

def fetch_onlinebuildingsdata(url, dest_img):
    url = url + getpostition + getzoom + getsize
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
            if cv2.contourArea(cnt) > 20:
#                 epsilon = 0.0001*cv2.arcLength(cnt, True)
#                 approx = cv2.approxPolyDP(cnt, epsilon, True)
#                 cv2.drawContours(fullSatelliteImg, [approx], -1, (0,0,255), -1)
#                 cv2.drawContours(fullRoadmapImg, [approx], -1, (0,0,255), -1)
#                 buildings.append(approx)
                buildings.append(cnt)             
    # draw the outline of all contours
    for cnt in contours:
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
    return buildings

def fetch_onlineroaddata(url, dest_img):
    url = url + getpostition + getzoom + getsize
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
    #thinned = cv2.ximgproc.thinning(mask) # Not good
    
    thinned = mask > filters.threshold_otsu(mask)
    
    
    
    #thinned, distance = medial_axis(thinned, return_distance=True)
    #thinned = thin(thinned)
    #thinned = skeletonize(thinned)
    #thinned = thinned.astype(np.uint8)
    
    thinned = skeletonize(thinned, method='lee')
    
    # display results
#     fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4), sharex=True, sharey=True)
#      
#     ax = axes.ravel()
#     ax[0].imshow(mask)
#     ax[0].axis('off')
#     ax[0].set_title('original', fontsize=20)
#      
#     ax[1].imshow(thinned)
#     ax[1].axis('off')
#     ax[1].set_title('skeleton', fontsize=20)
#     
#     fig.tight_layout()
#     plt.show()

    intersections, endpoints = utils.getSkeletonIntersection(thinned)
    
    contours, hier = cv2.findContours(thinned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours, hier = cv2.findContours(thinned, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    

    font = cv2.FONT_HERSHEY_COMPLEX
    # Draw the outline of all contours
    for n, cnt in enumerate(contours):
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
            print('Contours--->' + str(n), cnt)
            roads.append(cnt)
            
            
            if n == 1:
                points = cnt.ravel()  
                i = 0
                max = 1800
                for j in points:
                    if(i % 50 == 0) and (i < max):
                        x = points[i] 
                        y = points[i + 1] 
                        # String containing the co-ordinates. 
                        string = str(x) + " " + str(y)  
                        if(i == 0): 
                            # text on topmost co-ordinate. 
                            cv2.putText(fullSatelliteImg, "Begin", (x, y),  font, 0.3, (255, 0, 0))
                        elif (i == (max - 50)):
                            cv2.putText(fullSatelliteImg, str(i), (x, y),  font, 0.3, (0, 0, 255))
                        else: 
                            # text on remaining co-ordinates. 
                            cv2.putText(fullSatelliteImg, str(i), (x, y),  font, 0.3, (0, 255, 0))
                              
                    i = i + 1
                    
                    if (i == len(points) - 2):
                        x = points[i] 
                        y = points[i + 1]
                        cv2.putText(fullSatelliteImg, "End", (x , y),  font, 0.5, (0, 0, 255))
#             epsilon = 0.001*cv2.arcLength(cnt, True)
#             approx = cv2.approxPolyDP(cnt, epsilon, False)
#             cv2.drawContours(fullSatelliteImg,[approx],0,(0,255,0),1)
#             cv2.drawContours(dest_img,[approx],0,(0,255,0),1)
#             roads.append(approx)
    # Draw interections and and points
    for n, section in enumerate(intersections):
        cv2.circle(fullSatelliteImg, section, 3, (0,0,255), 3 )
        cv2.circle(dest_img, section, 3, (0,0,255), 3 )
        cv2.putText(fullSatelliteImg, str(n), section,  font, 0.5, (0, 0, 255))
    for n, point in enumerate(endpoints):
        cv2.circle(fullSatelliteImg, point, 3, (225,0,255), 3 )
        cv2.circle(dest_img, point, 3, (225,0,255), 3 )

    return roads, intersections
def convert_pixelarrays2worldcoordinate(pointsarrays, centerlat, centerlon, zoom = 18, tilezise = 640):
    gis_pointsarray = []
    # Calculate next tile from X, Y = (320,320) as tile size = 640 
    newLatCenter, newLonCenter = utils.getPointLatLngFromPixel(320, 320 + 640, centerlat, centerlon, tilezise, zoom)
    print ("Center Info: Tile (X,Y) is centered at [%s , %s] AND (X, Y + 1) is centered at [%s , %s]" % (centerlat, centerlon, newLatCenter, newLonCenter))
    
    for n, p in enumerate(pointsarrays):
        points = []
        for j in p:
            lat, lon = utils.getPointLatLngFromPixel(int(j[0][0]),int(j[0][1]), centerlat, centerlon, tilezise, zoom)
            points.append([lon, lat])
        gis_pointsarray.append(points)
    return gis_pointsarray

def convert_a_pixel_list2worldcoordinate(pointlist, centerlat, centerlon, zoom = 18, tilezise = 640):
    pointsarray = []
    for n, p in enumerate(pointlist):
        print ("X:Y:=", p[0],p[1])
        lat, lon = utils.getPointLatLngFromPixel(p[0],p[1], centerlat, centerlon, tilezise, zoom)
        print ("[lon, lat]:=", lon, lat)
        pointsarray.append([lon, lat])
    return pointsarray

def calculate_bbox_tiles(lat, lon, tilesize, zoom):
    
    minx = 0
    miny = 0
    maxx = tilesize
    maxy = tilesize 
      
    minx, miny = utils.getPointLatLngFromPixel(minx, miny, lat, lon, tilesize, zoom)
    maxx, maxy = utils.getPointLatLngFromPixel(maxx, maxy, lat, lon, tilesize, zoom)
    
    print ('MinXY is (%s, %s)' % (minx, miny))
    print ('MaxXY is (%s, %s)' % (maxx, maxy))

    return minx, miny, maxx, maxy
def create_polygons_shapefile(polygons):
        
    gis_polygons = convert_pixelarrays2worldcoordinate(polygons, lat , lon, zoom)

    minx, miny, maxx, maxy = calculate_bbox_tiles(lat, lon, imagesize, zoom)
    theorybbox = Polygon([(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx), (miny, minx)])
    
    utils.write_polygons2shpfile(outputshpfile, gis_polygons,theorybbox)
    
    utils.create_buildingslayer_in_database()
    utils.write_buildings2database(gis_polygons,theorybbox)
    
    return outputshpfile
def create_polyline_shapefile(polylines, intersections):    
    gis_polylines = convert_pixelarrays2worldcoordinate(polylines, lat , lon, zoom)
    intersectpoints = convert_a_pixel_list2worldcoordinate(intersections, lat , lon, zoom)
    print ("INTER : " , intersectpoints)
    utils.write_linestring2shpfile(outputshpfile, gis_polylines, intersectpoints)
    return outputshpfile    
# Run test for get data online
created_file = None
if (style == styleBuildings) or (style == styleZones):    
    # Create shape file for buildings and zones in polygons    
    building_polygons = fetch_onlinebuildingsdata(workingUrl, fullRoadmapImg)
    created_file = create_polygons_shapefile(building_polygons)
else:
    # Create shape file for roads in poly lines 
    roads, intersections = fetch_onlineroaddata(workingUrl,fullRoadmapImg)
    created_file = create_polyline_shapefile(roads, intersections)
    
    
# if created_file is not None:
#     utils.display_shpinfo(created_file)


# Run test for get data offline
# input_data_folder_path = 'C:\Download\Data\Hanoi\\'
# output_data_folder_path= 'C:\Download\Data\Output\Hanoi\\'
# 
# start_time = time.time()
# process_offlinedata(input_data_folder_path, output_data_folder_path, lat , lon, imagesize, zoom, 'png')
# print("--- %s seconds ---" % (time.time() - start_time))

cv2.imshow('Satellite', fullSatelliteImg)
cv2.imshow('Roadmap', fullRoadmapImg)
if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows() 
    

