'''
Created on May 6, 2020

@author: thaih
'''
import cv2
import shapefile
import math
import requests

import pyproj
from skimage import io
import json
from shapely.geometry import Polygon, LineString
import shapely.ops as ops
import shapely.geometry as geometry
from functools import partial
from osgeo import osr


def set_display_range(inputimage, ranges):
    if ranges is None:
        return inputimage
    outputimage = cv2.inRange(inputimage, ranges[0][0], ranges[0][1])
    if len(ranges) > 1 :
        for x in ranges:
            o = cv2.inRange(inputimage, x[0], x[1])
            outputimage = cv2.bitwise_or(outputimage, o)     
    return outputimage

def erosionthendilation(inputimage, kernel):
    return cv2.morphologyEx(inputimage,cv2.MORPH_CLOSE,kernel, iterations = 1)
def dilationthenerosion(inputimage, kernel):    
    return cv2.morphologyEx(inputimage,cv2.MORPH_OPEN,kernel, iterations = 1)
def remove_noise(inputimage, kernel):    
    return dilationthenerosion(inputimage, kernel)
def find_rasterpolygons(dest_img, features_img):
    contours, hier = cv2.findContours(features_img,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    # find and draw buildings
    for x in range(len(contours)):
            # if a contour has not contours inside of it, draw the shape filled
            c = hier[0][x][2]
            if c == -1:
                    #cv2.drawContours(dest_img,[contours[x]],0,(0,0,255),-1)
                    cnt = [contours[x]][0]
                    if cv2.contourArea(cnt) > 80:
                        cnt = [contours[x]][0]
                        epsilon = 0.0001*cv2.arcLength(cnt, True)
                        approx = cv2.approxPolyDP(cnt, epsilon, True)
                        cv2.drawContours(dest_img, [approx], -1, (0,0,255), -1)
                        polygons.append(approx)
    # draw the outline of all contours
    for cnt in contours:
            cv2.drawContours(dest_img,[cnt],0,(0,255,0),1)
    return dest_img, polygons
def fetch_buildings_or_zonesdata(filename):
    buildings = []
    img = io.imread(filename)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #print(img.shape)
    h,w = img.shape[:2]
    cv2.rectangle(img,(0,0),(w-1,h-1), (0,0,255),1)

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
                epsilon = 0.0001*cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
#                 cv2.drawContours(fullSatelliteImg, [approx], -1, (0,0,255), -1)
#                 cv2.drawContours(fullRoadmapImg, [approx], -1, (0,0,255), -1)
                buildings.append(approx)
                #buildings.append(cnt)             
    return buildings
def fetch_roadsdata(url):
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
            roads.append(cnt)
    return roads
def display_shpinfo(inputfile):
    with shapefile.Reader(inputfile) as shp:
        # read information from 1 object
        print("The 1st Object:")
        for name in dir(shp.shape(0)):
            if not name.startswith('_'):
                print (name)
        print('Bbox: ', shp.shape(0).bbox)
        print('Parts: ', shp.shape(0).parts)
        print('Type name: ', shp.shape(0).shapeTypeName)
        print('Type number: ', shp.shape(0).shapeType)
        print('Point list: ', shp.shape(0).points)
        # representation on Geojson format
#         geoj = shp.shape(0).__geo_interface__
#         geoj["type"]
#         print('GEOJSON', geoj)
        
        # Operations on file
        print("Operations on file:")
        print('Basic info:',shp)
        print('Bbox:', shp.bbox)
        print('Fields:', shp.fields)
        
        print("Operations on record:")
        records = shp.records()
        print('Numbers of Record:', len(records))
        # Reading records 
        rec = records[0]
        dct = rec.as_dict()
        print('Attributes of record with oid ',rec.oid)
        print(sorted(dct.items()))
        # Reading Geometry and Records Simultaneously
#         shapeRecs = shp.shapeRecords()
#         shpRec = shapeRecs[0]
#         print('Attributes: ', shpRec.record[1:3])
#         geoj = shpRec.__geo_interface__
#         geoj["type"]
#         print('All in GEOJSON', geoj)


def calculate_polygon_area_in_m2(geom ):
    geom_area = ops.transform(partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(proj='aea', lat1=geom.bounds[1], lat2=geom.bounds[3])), geom)
    return geom_area.area


def write_points2shpfile(outputfile, points):
    with shapefile.Writer(outputfile, shapeType=shapefile.POINT, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        for n, p in enumerate(points):
            #print(p)
            if (n == 72) or (n == 73) or (n == 74):
                print("Here " + str(n) + " :", p)
            shp.point(p[0], p[1])
            shp.record("point " + str(n))
            
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)
        
def write_polygons2shpfile(outputfile, polygons):
    # Calculate BBOX
    multipolygon = []
    for n, p in enumerate(polygons):
        gpoly = Polygon(p)
        multipolygon.append(gpoly)
    polygon_collection = geometry.MultiPolygon(multipolygon)
    bbox = polygon_collection.bounds
    # Case bbox not a polygon because collection is a line (we were not check it), try catch 
    try:
        bbpoly = Polygon([(bbox[0],bbox[1]), (bbox[0],bbox[3]), (bbox[2],bbox[3]), (bbox[2],bbox[1]), (bbox[0],bbox[1])])
    except:
        return
    
    boundarylines = LineString(bbpoly.exterior.coords)
#     bbpoly = Polygon([(bbox[0],bbox[1]), (bbox[0],bbox[3]), (bbox[2],bbox[3]), (bbox[2],bbox[1]), (bbox[0],bbox[1])])
#     boundarylines = LineString(bbpoly.exterior.coords)
    
    centerpoints = []
    with shapefile.Writer(outputfile, shapeType=shapefile.POLYGON, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        shp.field('CalcArea', 'N', decimal=6)
        shp.field('Jointly', 'L')
        shp.field('Address', 'C', size=250)
        
        # first one, add bbox to shape file
        coords = bbpoly.exterior.coords
        outpoly = []
        for pp in list(coords):
            outpoly.append([pp[0],pp[1]])
        shp.poly([outpoly])
        area = calculate_polygon_area_in_m2(bbpoly)
        shp.record("polygon 0", area, 0, 'Boundary')
        # second one, add other polygons to shape file
        for n, p in enumerate(polygons):
            #print(p)
#             outpoly = []
#             outpoly.append(p)
#             shp.poly(outpoly)
#             
            gpoly = Polygon(p)          
            # Identify jointly polygon
            bJointly = 0
            if boundarylines.touches(gpoly):
                bJointly = 1  
            #Simplify and create centroid
            gpoly = gpoly.simplify(0.000005)
            #centerpoints.append((gpoly.centroid._get_coords()[0][0], gpoly.centroid._get_coords()[0][1]))             
            coords = gpoly.exterior.coords
            outpoly = []
            for pp in list(coords):
                outpoly.append([pp[0],pp[1]])
            shp.poly([outpoly])

            # Area
            area = calculate_polygon_area_in_m2(gpoly)
            # Center point info
#             results = getlocationinformation(gpoly.centroid._get_coords()[0][1], gpoly.centroid._get_coords()[0][0])
#             r = results['results'][0]['formatted_address']
#             # Name
#             strJson = json.dumps(r).encode("utf-8")
            
            #print(strJson)
            shp.record("polygon " + str(n + 1), area, bJointly, "Info")
            print("...", end = '')
            
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)
    #write_points2shpfile("%s_centroids.shp" % outputfile[:-4], centerpoints)

def write_linestring2shpfile(outputfile, lines):
    with shapefile.Writer(outputfile, shapeType=shapefile.POLYLINE, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        for n, l in enumerate(lines):
            print(l)
            outlines = []
            outlines.append(l)
            shp.line(outlines)
            shp.record('linestring ' + str(n))
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)
# From: https://stackoverflow.com/questions/47106276/converting-pixels-to-latlng-coordinates-from-google-static-image
def getPointLatLngFromPixel(x, y, centerlat, centerlon, imagesize= 640, zoom = 18):
    parallelMultiplier = math.cos(centerlat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = centerlat - degreesPerPixelY * ( y - imagesize / 2)
    pointLng = centerlon + degreesPerPixelX * ( x  - imagesize / 2)
    return (pointLat, pointLng)

def getlocationinformation(latitude, longitude, googleApiKey = 'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU'):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    #params = {'key':'AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU','sensor': 'false', 'address': 'Mountain View, CA'}
    params = {'key':googleApiKey,'sensor': 'false', 'latlng': '{},{}'.format(latitude,longitude)}
    r = requests.get(url, params=params)
    return r.json()
    
def neighbours(x,y,image):
    """Return 8-neighbours of image point P1(x,y), in a clockwise order"""
    img = image
    x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1;
    return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1], img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ] 
def getSkeletonIntersection(skeleton):
    """ Given a skeletonised image, it will give the coordinates of the intersections of the skeleton.

    Keyword arguments:
    skeleton -- the skeletonised image to detect the intersections of

    Returns: 
    List of 2-tuples (x,y) containing the intersection coordinates
    """
    # A biiiiiig list of valid intersections             2 3 4
    # These are in the format shown to the right         1 C 5
    #                                                    8 7 6 
    validIntersection = [[0,1,0,1,0,0,1,0],[0,0,1,0,1,0,0,1],[1,0,0,1,0,1,0,0],
                         [0,1,0,0,1,0,1,0],[0,0,1,0,0,1,0,1],[1,0,0,1,0,0,1,0],
                         [0,1,0,0,1,0,0,1],[1,0,1,0,0,1,0,0],[0,1,0,0,0,1,0,1],
                         [0,1,0,1,0,0,0,1],[0,1,0,1,0,1,0,0],[0,0,0,1,0,1,0,1],
                         [1,0,1,0,0,0,1,0],[1,0,1,0,1,0,0,0],[0,0,1,0,1,0,1,0],
                         [1,0,0,0,1,0,1,0],[1,0,0,1,1,1,0,0],[0,0,1,0,0,1,1,1],
                         [1,1,0,0,1,0,0,1],[0,1,1,1,0,0,1,0],[1,0,1,1,0,0,1,0],
                         [1,0,1,0,0,1,1,0],[1,0,1,1,0,1,1,0],[0,1,1,0,1,0,1,1],
                         [1,1,0,1,1,0,1,0],[1,1,0,0,1,0,1,0],[0,1,1,0,1,0,1,0],
                         [0,0,1,0,1,0,1,1],[1,0,0,1,1,0,1,0],[1,0,1,0,1,1,0,1],
                         [1,0,1,0,1,1,0,0],[1,0,1,0,1,0,0,1],[0,1,0,0,1,0,1,1],
                         [0,1,1,0,1,0,0,1],[1,1,0,1,0,0,1,0],[0,1,0,1,1,0,1,0],
                         [0,0,1,0,1,1,0,1],[1,0,1,0,0,1,0,1],[1,0,0,1,0,1,1,0],
                         [1,0,1,1,0,1,0,0]];
    image = skeleton.copy();
    image = image/255;
    intersections = list();
    for x in range(1,len(image)-1):
        for y in range(1,len(image[x])-1):
            # If we have a white pixel
            if image[x][y] == 1:
                nbs = neighbours(x,y,image);
                valid = True;
                if nbs in validIntersection:
                    intersections.append((y,x));
    # Filter intersections to make sure we don't count them twice or ones that are very close together
    for point1 in intersections:
        for point2 in intersections:
            if (((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) < 10**2) and (point1 != point2):
                intersections.remove(point2);
    # Remove duplicates
    intersections = list(set(intersections));
    return intersections;
    