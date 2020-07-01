'''
Created on May 11, 2020

@author: thaih
'''
import cv2
import numpy as np     
from requests.utils import quote
from skimage import io, filters
from skimage.morphology import skeletonize, thin, medial_axis

from shapely.geometry import Polygon
import time
import datetime
import os
import utils
from pathlib import Path



# Center My Dinh (X,Y)
# lat = 21.0312246
# lon = 105.7646925

# Cau vuot Mai Dich
# lat = 21.035628
# lon = 105.781349

# #test highway
# lat = 21.0813699
# lon = 105.7887625

# Ha Noi Center
lat = 20.97503280639646
lon = 105.65287399291995


zoom = 18
imagesize = 640


styleBuildings = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
#full road is used for creating zones
styleZones = quote('feature:road|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

styleArterialRoad = quote('feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayRoad = quote('feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleHighwayControlledAccessRoad = quote('feature:road.highway.controlled_access|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
styleLocalRoad = quote('feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')

style = styleHighwayRoad
roadtype = 'Highways'

if style == styleBuildings:     
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Buildings.shp'
    roadtype = 'Buildings'
elif style == styleZones:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Zones.shp'
    roadtype = 'Zones'
elif style == styleHighwayRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Highways.shp'
    roadtype = 'Highways'
elif style == styleLocalRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Localroads.shp'
    roadtype = 'Localroads'  
elif style == styleHighwayControlledAccessRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_HighwayControlledAccess.shp'
    roadtype = 'HighwayControlled'
elif style == styleArterialRoad:
    outputshpfile = 'C:\Download\Data\Output\\' + str(lon) + '_' + str(lat) + '_'+ str(zoom) + '_Arterialroads.shp'
    roadtype = 'Arterialroads'
    
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
    contours, hier = cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    for x in range(len(contours)):
        print()
        # if a contour has not contours inside of it, draw the shape filled
        c = hier[0][x][2]
        if c == -1:
            #cv2.drawContours(fullSatelliteImg,[contours[x]],0,(0,0,255),-1)
            cnt = [contours[x]][0]
            if cv2.contourArea(cnt) > 10:
                #epsilon = 0.0001*cv2.arcLength(cnt, True)
#                 approx = cv2.approxPolyDP(cnt, epsilon, True)
#                 cv2.drawContours(fullSatelliteImg, [approx], -1, (0,0,255), -1)
#                 cv2.drawContours(fullRoadmapImg, [approx], -1, (0,0,255), -1)
#                 buildings.append(approx)
                buildings.append(cnt)             
    # draw the outline of all contours
    for cnt in contours:
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
            #buildings.append(cnt) 
    return buildings

def fetch_onlineroaddata(url, dest_img):
    
    url = url + getpostition + getzoom + getsize
    
    #url = 'C:/Download/Data/Hanoi/LocalRoads/-1/0.png'
    #url = 'C:/Download/Data/Hanoi/ControlledAccessRoads/1/-9.png' 
    #url = 'C:/Download/Data/Hanoi/Highways/-4/-9.png'
    
    roads = []
    img = io.imread(url)
    #cv2.imshow("Origin", img)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #cv2.imshow('HSV', img)
    
    low = (0,11,0)
    high = (179,255,255)
    # create masks
    mask = cv2.inRange(hsv, low, high)
    #cv2.imshow("REMOVE GOOGLE TRADE MARK", mask)
  
    # Create skeleton for lines to get more accurately
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

    cv2.imshow('THIN', thinned)
    
    #intersections = utils.getSkeletonIntersections(thinned)
    
    intersections_1, endpoints = utils.getSkeletonIntersectionsAndEndPoints(thinned)
     
    intersections = intersections_1 + endpoints
    
    #intersections, endps = utils.getSkeletonIntersectionsAndEndPoints(thinned)
    contours, hier = cv2.findContours(thinned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours, hier = cv2.findContours(thinned, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    

    font = cv2.FONT_HERSHEY_COMPLEX
    
    for n, section in enumerate(intersections):
        print(section)   
        
    allsegments = []    
    # Draw the outline of all contours
    for n, cnt in enumerate(contours):
            cv2.drawContours(fullSatelliteImg,[cnt],0,(0,255,0),1)
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
            #print('Contours--->' + str(n), cnt)
            #roads.append(cnt)
            points = cnt.ravel()  
            i = 0
            n_points = len(points)
            segment = []
            
            for j in points:
                if(i % 2 == 0) and (i <= n_points):
                    x = points[i] 
                    y = points[i + 1] 
                    p = (x,y)
                    segment.append(p)
                    for s in intersections: 
                        if p == s :
                            print ("Intersect at " + str(i) + " is (%s,%s)" % (p[0], p[1]) )
                            allsegments.append(segment)
                            segment = []
                            segment.append(p)
                           
                i = i + 1
    # Clean up, remove points and duplicate
    print('Number of segment : ', len(allsegments))
    for s in allsegments:
        print (s)
        if len(s) == 1:
            allsegments.remove(s)
    allsegments = utils.check_and_remove_lines_duplicate(allsegments) 
    print ('After clean up')   
    print('Number of segment : ', len(allsegments))                      
    for s in allsegments:
        print (s)    
    roads = allsegments

    # Draw interections and and points
    for n, section in enumerate(intersections_1):
        cv2.circle(fullSatelliteImg, section, 3, (0,0,255), 3 )
        p = (section[0] + 10,section[1] + 10)
        cv2.putText(dest_img, str(n), p,  font, 0.5, (255, 0, 255))
    for n, section in enumerate(endpoints):
        cv2.circle(fullSatelliteImg, section, 3, (255,0,0), 3 )
        p = (section[0] + 10,section[1] + 10)
        cv2.putText(dest_img, str(n), p,  font, 0.5, (255, 0, 255))
    return roads, endpoints
                
def convert_pixelarrays2worldcoordinate(pointsarrays, centerlat, centerlon, zoom = 18, tilezise = 640):
    gis_pointsarray = []
    # Calculate next tile from X, Y = (320,320) as tile size = 640 
    #newLatCenter, newLonCenter = utils.getPointLatLngFromPixel(320, 320 + 640, centerlat, centerlon, tilezise, zoom)
    #print ("Center Info: Tile (X,Y) is centered at [%s , %s] AND (X, Y + 1) is centered at [%s , %s]" % (centerlat, centerlon, newLatCenter, newLonCenter))
    for n, p in enumerate(pointsarrays):
        points = []
        for j in p:
            lat, lon = utils.getPointLatLngFromPixel(int(j[0][0]),int(j[0][1]), centerlat, centerlon, tilezise, zoom)
            points.append([lon, lat])
        gis_pointsarray.append(points)
    return gis_pointsarray
def convert_pixelarrays2worldcoordinate_v2(list_of_array, centerlat, centerlon, zoom = 18, tilezise = 640):
    gis_pointsarray = []
    for n, single_array in enumerate(list_of_array):
        points = []
        for eachpoint in single_array:
            lat, lon = utils.getPointLatLngFromPixel(eachpoint[0], eachpoint[1], centerlat, centerlon, tilezise, zoom)
            points.append([lon, lat])
        gis_pointsarray.append(points)
    return gis_pointsarray
def convert_a_pixel_list2worldcoordinate(pointlist, centerlat, centerlon, zoom = 18, tilezise = 640):
    pointsarray = []
    for n, p in enumerate(pointlist):
        lat, lon = utils.getPointLatLngFromPixel(p[0],p[1], centerlat, centerlon, tilezise, zoom)
        pointsarray.append([lon, lat])
    return pointsarray

def calculate_bbox_tiles(lat, lon, tilesize, zoom):
    minx = 0
    miny = 0
    maxx = tilesize - 1
    maxy = tilesize - 1
      
    minx, miny = utils.getPointLatLngFromPixel(minx, miny, lat, lon, tilesize, zoom)
    maxx, maxy = utils.getPointLatLngFromPixel(maxx, maxy, lat, lon, tilesize, zoom)
    return minx, miny, maxx, maxy
def create_polygons_shapefile(polygons):
        
    gis_polygons = convert_pixelarrays2worldcoordinate(polygons, lat , lon, zoom)

    minx, miny, maxx, maxy = calculate_bbox_tiles(lat, lon, imagesize, zoom)
    theorybbox = Polygon([(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx), (miny, minx)])
    
    utils.write_polygons2shpfile(outputshpfile, gis_polygons,theorybbox)
    
    return outputshpfile
def create_polyline_shapefile(polylines, intersections):   
    
    gis_polylines = convert_pixelarrays2worldcoordinate_v2(polylines, lat , lon, zoom)
    
    intersectpoints = convert_a_pixel_list2worldcoordinate(intersections, lat , lon, zoom)

    utils.write_linestring2shpfile(outputshpfile, gis_polylines, None)
    
    return outputshpfile

def process_all_layers_to_shapefile(input_data_folder_path, output_data_folder_path, org_lat , org_lon, tilesize = 640, zoom = 18, tileformat = 'png'):
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
                            gis_polylines = convert_pixelarrays2worldcoordinate_v2(roads, lat , lon, zoom)
                            utils.write_linestring2shpfile(outputshpfile, gis_polylines, None)
                        #utils.display_shpinfo(outputshpfile)
                        
def process_all_layers_into_database(input_data_folder_path, org_lat , org_lon, tilesize = 640, zoom = 18, tileformat = 'png'):
    
    connection = utils.create_layers_in_database()
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
                        i = int(X)
                        j = int(Y)
                        lat, lon = utils.getPointLatLngFromPixel(int(tilesize /2) + (i * tilesize), int(tilesize /2) + (j * tilesize), org_lat, org_lon, tilesize, zoom)
                        if dir_name == str('Buildings'):                      
                            building_polygons = utils.fetch_buildings_or_zonesdata(tile_name)
                            gis_polygons = convert_pixelarrays2worldcoordinate(building_polygons, lat , lon, zoom)
                            
                            # Insert data into TileGrid layers
                            minx, miny, maxx, maxy = calculate_bbox_tiles(lat, lon, tilesize, zoom)
                            theorybbox = Polygon([(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx), (miny, minx)])
                            utils.write_tilegrid2database(connection, i, j, theorybbox)
                            # Insert data into Buildings layers                           
                            utils.write_buildings2database(connection, i, j, gis_polygons,theorybbox)                          
                        elif dir_name == str('Highways') or dir_name == str('LocalRoads') or dir_name == str('ArterialRoads') or dir_name == str('ControlledAccessRoads'): 
                            roads, endpoints = utils.fetch_roadsdata(tile_name)
                            gis_polylines = convert_pixelarrays2worldcoordinate_v2(roads, lat , lon, zoom)
                            
                            gis_endpoints = None
                            if endpoints is not None:
                                gis_endpoints = []
                                for eachpoint in endpoints:
                                    lat, lon = utils.getPointLatLngFromPixel(eachpoint[0], eachpoint[1], lat , lon, tilesize, zoom)
                                    gis_endpoints.append((lon, lat))
                            # Insert data into Roads layers
                            utils.write_roads2database(connection, i, j, dir_name, gis_polylines, gis_endpoints)
 
                        
    if(connection):
        connection.close()                            
# Run test for get data online
# created_file = None
# if (style == styleBuildings) or (style == styleZones):    
#     # Create shape file for buildings and zones in polygons    
#     building_polygons = fetch_onlinebuildingsdata(workingUrl, fullRoadmapImg)
#     created_file = create_polygons_shapefile(building_polygons)
# else:
#     # Create shape file for roads in poly lines
#     roads, intersections = fetch_onlineroaddata(workingUrl,fullRoadmapImg)
#       
#     created_file = create_polyline_shapefile(roads, intersections)
# cv2.imshow('Satellite', fullSatelliteImg)
# cv2.imshow('Roadmap', fullRoadmapImg)
# if cv2.waitKey(0) & 0xFF == ord('q'): 
#     cv2.destroyAllWindows()     
    
# if created_file is not None:
#     utils.display_shpinfo(created_file)


    
# Run test for get data offline
input_data_folder_path = 'C:\Download\Data\Hanoi\\'
start_time = time.time()
print("--- Start %s ---" % start_time)
# Case of create shape file, need output directory 
# output_data_folder_path= 'C:\Download\Data\Output\Hanoi\\'
# process_all_layers_to_shapefile(input_data_folder_path, output_data_folder_path, lat , lon, imagesize, zoom, 'png')
process_all_layers_into_database(input_data_folder_path, lat , lon, imagesize, zoom, 'png')
seconds = time.time() - start_time
print("--- Total time taken: %s seconds ---" % time.strftime("%H:%M:%S",time.gmtime(seconds)))


    

