'''
Created on May 6, 2020

@author: thaih
'''
import cv2
import shapefile
import math
import requests

import pyproj
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
    bbpoly = Polygon([(bbox[0],bbox[1]), (bbox[0],bbox[3]), (bbox[2],bbox[3]), (bbox[2],bbox[1]), (bbox[0],bbox[1])])
    boundarylines = LineString(bbpoly.exterior.coords)
    
    centerpoints = []
    with shapefile.Writer(outputfile, shapeType=shapefile.POLYGON, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        shp.field('CalcArea', 'N', decimal=6)
        shp.field('Jointly', 'L')
        
        # first one, add bbox to shape file
        coords = bbpoly.exterior.coords
        outpoly = []
        for pp in list(coords):
            outpoly.append([pp[0],pp[1]])
        shp.poly([outpoly])
        area = calculate_polygon_area_in_m2(bbpoly)
        shp.record("polygon 0", area, 0)
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
            centerpoints.append((gpoly.centroid._get_coords()[0][0], gpoly.centroid._get_coords()[0][1]))             
            coords = gpoly.exterior.coords
            outpoly = []
            for pp in list(coords):
                outpoly.append([pp[0],pp[1]])
            shp.poly([outpoly])

            # Area
            area = calculate_polygon_area_in_m2(gpoly)
            # Center point info
#             results = getlocationinformation(gpoly.centroid._get_coords()[0][1], gpoly.centroid._get_coords()[0][0])
#             r = results['results'][0]['address_components'] [0]['long_name']
#             # Name
#             strJson = json.dumps(r).encode("utf-8")
            
            shp.record("polygon " + str(n + 1), area, bJointly)
            
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)
#    write_points2shpfile("%s_centroids.shp" % outputfile[:-4], centerpoints)

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
    

    