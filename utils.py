'''
Created on May 6, 2020

@author: thaih
'''
import cv2
import shapefile
import math
import requests

import psycopg2

import pyproj
from skimage import io, filters
from skimage.morphology import skeletonize
import numpy as np
from shapely.ops import split

import json
from shapely.geometry import Polygon, LineString, Point
import shapely.ops as ops
import shapely.geometry as geometry
from functools import partial
from osgeo import osr
import psycopg2.extras



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
    #cv2.imshow('HSV', img)
    
    low = (0,11,0)
    high = (179,255,255)
    # create masks
    mask = cv2.inRange(hsv, low, high)
    #cv2.imshow("REMOVE GOOGLE TRADE MARK", mask)
    contours, hier = cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for x in range(len(contours)):
        # if a contour has not contours inside of it, draw the shape filled
        c = hier[0][x][2]
        if c == -1:
            #cv2.drawContours(fullSatelliteImg,[contours[x]],0,(0,0,255),-1)
            cnt = [contours[x]][0]
            if (cv2.contourArea(cnt) > 20) and (cv2.contourArea(cnt) < 400000): # Max Area is boundary of 640 * 640 = 409600
#                 epsilon = 0.0001*cv2.arcLength(cnt, True)
#                 approx = cv2.approxPolyDP(cnt, epsilon, True)
#                 buildings.append(approx)
                buildings.append(cnt)             
    return buildings
def fetch_roadsdata(url):
    roads = []
    img = io.imread(url)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #cv2.imshow('HSV', img)
    
    low = (0,11,0)
    high = (179,255,255)
    # create masks
    mask = cv2.inRange(hsv, low, high)
    #cv2.imshow("REMOVE GOOGLE TRADE MARK", mask)
    
    # Create skeleton for lines to get more accurately
    try:
        thinned = mask > filters.threshold_otsu(mask)
    except:
        return roads, None

    #thinned, distance = medial_axis(thinned, return_distance=True)
    thinned = skeletonize(thinned, method='lee')
#     thinned = skeletonize(thinned)
#     thinned = thinned.astype(np.uint8)
    
    #intersections = getSkeletonIntersections(thinned)
    
    intersections, endpoints = getSkeletonIntersectionsAndEndPoints(thinned)
    
    intersections = intersections + endpoints
    
    contours, hier = cv2.findContours(thinned,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    
    
    # Get all segment contours
    for n, cnt in enumerate(contours):
            points = cnt.ravel()  
            i = 0
            n_points = len(points)
            segment = []
            
            for j in points:
                if(i % 2 == 0) and (i <= n_points):
                    x = points[i] 
                    y = points[i + 1] 
                    p = (x,y)
                    print(p)
                    segment.append(p)
                    for s in intersections: 
                        if p == s :
                            roads.append(segment)
                            segment = []
                            segment.append(p)
                           
                i = i + 1
    # Clean up, remove points and duplicate
    for s in roads:
        print (s)
        if len(s) == 1:
            roads.remove(s)
    roads = check_and_remove_lines_duplicate(roads)                         
    
    return roads, endpoints
def display_shpinfo(inputfile):
    with shapefile.Reader(inputfile, encoding = "utf-8") as shp:
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
        dct = {k: str(v).encode("utf-8") for k,v in dct.items()}
        print('Attributes of record with oid ',rec.oid)
        print(sorted(dct.items()))
        # Reading Geometry and Records Simultaneously
#         shapeRecs = shp.shapeRecords()
#         shpRec = shapeRecs[0]
#         print('Attributes: ', shpRec.record[1:3])
#         geoj = shpRec.__geo_interface__
#         geoj["type"]
#         print('All in GEOJSON', geoj)
def get_metadata_dowload_info(adm_id):
    lat = None
    lon = None
    tilenum = None
    inputfile = 'data\VNM_adm1.shp'
    areaTile640 = 126546.188215 # Area pre-calculated at tilezise = 640 and zoom = 18

    with shapefile.Reader(inputfile, encoding = "utf-8") as shp:
        print('Bbox From the whole:', shp.bbox)
        print('Fields:', shp.fields)
        records = shp.records()
        
        for i in range (len(records)):
            rec = records[i]
            rec = rec['ID_1']
            if rec == adm_id :
                bbox = shp.shape(i).bbox
                lon = (bbox[0] + bbox[2]) / 2
                lat = (bbox[1] + bbox[3]) / 2
                pbbox = Polygon([(bbox[0],bbox[1]), (bbox[0],bbox[3]), (bbox[2],bbox[3]), (bbox[2],bbox[1]), (bbox[0],bbox[1])])

                totalArea = calculate_polygon_area_in_m2(pbbox)
                tilenum = int(totalArea / areaTile640)
                tilenum = int(tilenum / 2)
                break;
        print ('Center Lat/lon of Province ID = % s is (%s,%s) and number of tile is %s' % (adm_id, lat, lon, tilenum))
    return lat, lon, tilenum

def calculate_polygon_area_in_m2(geom ):
    geom_area = ops.transform(partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(proj='aea', lat1=geom.bounds[1], lat2=geom.bounds[3])), geom)
    return geom_area.area

def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    # This is taken from shapely manual
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]

def split_line_with_points(line, points):
    """Splits a line string in several segments considering a list of points.

    The points used to cut the line are assumed to be in the line string 
    and given in the order of appearance they have in the line string.

    >>> line = LineString( [(1,2), (8,7), (4,5), (2,4), (4,7), (8,5), (9,18), 
    ...        (1,2),(12,7),(4,5),(6,5),(4,9)] )
    >>> points = [Point(2,4), Point(9,18), Point(6,5)]
    >>> [str(s) for s in split_line_with_points(line, points)]
    ['LINESTRING (1 2, 8 7, 4 5, 2 4)', 'LINESTRING (2 4, 4 7, 8 5, 9 18)', 'LINESTRING (9 18, 1 2, 12 7, 4 5, 6 5)', 'LINESTRING (6 5, 4 9)']

    """
    segments = []
    current_line = line
    for p in points:
        d = current_line.project(p)
        seg, current_line = cut(current_line, d)
        segments.append(seg)
    segments.append(current_line)
    return segments
def check_and_remove_lines_duplicate(allsegments):
    for s1 in allsegments:
        for s2 in allsegments:
            if (len(s1) == len(s2)) and (s1[0] == s2[0]) and (s1[len(s1) - 1] == s2[len(s2) - 1]) and (s1 != s2):
                allsegments.remove(s2);
            if (len(s1) == len(s2)) and (s1[0] == s2[len(s2) - 1]) and (s1[len(s1) - 1] == s2[0]) and (s1 != s2):
                allsegments.remove(s2);                
    return allsegments
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
        
def write_polygons2shpfile(outputfile, polygons, theorybbox):
    # Calculate BBOX
    multipolygon = []
    for n, p in enumerate(polygons):
        gpoly = Polygon(p)
        multipolygon.append(gpoly)
    polygon_collection = geometry.MultiPolygon(multipolygon)
    # BBox to calculate jointly parts
    realbbox = polygon_collection.bounds
    # Case realbbox not a polygon because collection is a line (we were not check it), try catch 
    try:
        bbpoly = Polygon([(realbbox[0],realbbox[1]), (realbbox[0],realbbox[3]), (realbbox[2],realbbox[3]), (realbbox[2],realbbox[1]), (realbbox[0],realbbox[1])])
    except:
        return
    
    if theorybbox is None:
        theorybbox = bbpoly
    else:
        print(bbpoly)
        print(theorybbox)
        
    boundarylines = LineString(bbpoly.exterior.coords)
    trueboundary = LineString(theorybbox.exterior.coords)
    
    centerpoints = []
    with shapefile.Writer(outputfile, shapeType=shapefile.POLYGON, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        shp.field('CalcArea', 'N', decimal=6)
        shp.field('Jointly', 'L')
        shp.field('Address', 'C', size=250)
        
        # first one, add realbbox to shape file
        coords = theorybbox.exterior.coords
        outpoly = []
        for pp in list(coords):
            outpoly.append([pp[0],pp[1]])
        shp.poly([outpoly])
        area = calculate_polygon_area_in_m2(theorybbox)
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


            if (bJointly ==1) and (gpoly.touches(trueboundary) == False):
                #gpoly = gpoly.buffer(0)
                print("polygon " + str(n + 1))                
            #Simplify and create centroid
            #gpoly = Polygon(gpoly.simplify(0.00001))
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
 
            
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)
    #write_points2shpfile("%s_centroids.shp" % outputfile[:-4], centerpoints)

def write_linestring2shpfile(outputfile, lines, endpoints):
    with shapefile.Writer(outputfile, shapeType=shapefile.POLYLINE, encoding="utf8") as shp:
        shp.field('Name', 'C', size=40)
        intersect_points = []
        
        if endpoints is not None:
            for p in endpoints:
                intersect_points.append(Point(p))
            for i, l in enumerate(lines):
                if (len(l) == 1):
                    continue
                glinestring = LineString(l)
                print (glinestring.is_ring)
                try:
                    segments = split_line_with_points(glinestring, intersect_points)
                    for n, s in enumerate(segments):
                        glinestring = s.simplify(0.000003)
                        #glinestring = s
                        outlines = []
                        for pp in glinestring.coords:
                            outlines.append([pp[0],pp[1]])
                        shp.line([outlines])
                        shp.record('linestring ' + str(i) + '_' + str(n))
                except:
                    glinestring = glinestring.simplify(0.000003)
                    #glinestring = s
                    outlines = []
                    for pp in glinestring.coords:
                        outlines.append([pp[0],pp[1]])
                    shp.line([outlines])
                    shp.record('linestring ' + str(i))

        else:
            for i, l in enumerate(lines):
                if (len(l) == 1):
                    continue                
                try:
                    glinestring = LineString(l)
                    glinestring = glinestring.simplify(0.00001)
                    outlines = []
                    for pp in glinestring.coords:
                        outlines.append([pp[0],pp[1]])
                    shp.line([outlines])
                    shp.record('linestring ' + str(i))
                except:
                    return

#             outlines = []
#             outlines.append(l)
#             shp.line(outlines)
#             shp.record('linestring ' + str(i))
            
    add_prj = open("%s.prj" % outputfile[:-4], "w")
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(4326)
    epsg = proj.ExportToWkt()
    add_prj.write(epsg)
    add_prj.close()
    print('Done! ', outputfile)

def create_layers_in_database():
    global connection
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "postgres",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "ras2vec")
            
        cursor = connection.cursor()
        # Tilegrid layers
        cursor.execute("DROP TABLE IF EXISTS TileGrid;")
        query_createtable = '''CREATE TABLE TileGrid
              (ID SERIAL PRIMARY KEY     NOT NULL,
              X  INT     NOT NULL, 
              Y  INT     NOT NULL,             
              CalcArea         REAL,
              geom GEOMETRY DEFAULT NULL); '''
        cursor.execute(query_createtable)
        connection.commit()
        print("TileGrid Layer is created!")
        
        # Buildings layers
        cursor.execute("DROP TABLE IF EXISTS Buildings;")
        query_createtable = '''CREATE TABLE Buildings
              (ID SERIAL PRIMARY KEY     NOT NULL,
              X  INT     NOT NULL, 
              Y  INT     NOT NULL,             
              Name           TEXT,
              CalcArea         REAL,
              Jointly  BOOLEAN,
              Address TEXT,
              geom GEOMETRY DEFAULT NULL,
              j_point GEOMETRY DEFAULT NULL,
              cent_point GEOMETRY DEFAULT NULL); '''
        cursor.execute(query_createtable)
        connection.commit()
        print("Buildings Layer is created!")
        # Road layers
        cursor.execute("DROP TABLE IF EXISTS Roads;")
        query_createtable = '''CREATE TABLE Roads
              (ID SERIAL PRIMARY KEY     NOT NULL,
              X  INT     NOT NULL, 
              Y  INT     NOT NULL,              
              Name           TEXT,
              Type         TEXT,
              Jointly  BOOLEAN,
              Address TEXT,
              geom GEOMETRY DEFAULT NULL,
              j_point GEOMETRY DEFAULT NULL); '''
        cursor.execute(query_createtable)        
        
        #cursor.execute("CREATE EXTENSION postgis;")
        connection.commit()
        print("Road Layer is created!")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        #closing database connection if error.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    if(cursor):
        cursor.close()    
    return connection
def write_tilegrid2database(connection, tileX, tileY, theorybbox):
    try:
        cursor = connection.cursor()
        geom_boundary = theorybbox.wkb
        area = calculate_polygon_area_in_m2(theorybbox)

        cursor.execute('INSERT INTO TileGrid(X, Y, CalcArea, geom)'
                       'VALUES (%(X)s, %(Y)s, %(area)s, ST_GeomFromWKB(%(geom)s::geometry, 4326))',
                       {'X': tileX,'Y': tileY, 'area': str(area), 'geom' : geom_boundary})

        connection.commit()
        print ("Inserted TileGrid for Tile ",tileX, "_",tileY )

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    if(cursor):
        cursor.close()             
    return connection       
                     
def write_buildings2database(connection, tileX, tileY, polygons, theorybbox):
    if len(polygons) == 0:
        return connection
    # Process insert polygons
    multipolygon = []
    for n, p in enumerate(polygons):
        gpoly = Polygon(p)
        multipolygon.append(gpoly)
    polygon_collection = geometry.MultiPolygon(multipolygon)
    # BBox to calculate jointly parts
    realbbox = polygon_collection.bounds
    # Case realbbox not a polygon because collection is a line (we were not check it), try catch 
    try:
        bbpoly = Polygon([(realbbox[0],realbbox[1]), (realbbox[0],realbbox[3]), (realbbox[2],realbbox[3]), (realbbox[2],realbbox[1]), (realbbox[0],realbbox[1])])
    except:
        return
    if theorybbox is None:
        theorybbox = bbpoly
        
    #boundarylines = LineString(theorybbox.exterior.coords)
    boundarylines = LineString(theorybbox.exterior.coords)
    
    values_list = []
    for n, p in enumerate(polygons):
        gpoly = Polygon(p)          
        # Identify jointly polygon
        bJointly = False
        j_point = None
        if boundarylines.touches(gpoly):
            bJointly = True
            intersection = gpoly.exterior.intersection(boundarylines)
            j_point = Point(intersection.centroid._get_coords()[0][0], intersection.centroid._get_coords()[0][1]) 
            j_point = j_point.wkb 
            print(intersection)          
        #gpoly = Polygon(gpoly.simplify(0.00001))
        #centerpoints.append((gpoly.centroid._get_coords()[0][0], gpoly.centroid._get_coords()[0][1]))
        area = calculate_polygon_area_in_m2(gpoly)
        name = 'polygon' + str(n+1)    
        address = 'Info'
        geom =  gpoly.wkb
        center_point = Point(gpoly.centroid._get_coords()[0][0], gpoly.centroid._get_coords()[0][1]) 
        center_point = center_point.wkb
           
        
#         results = getlocationinformation(gpoly.centroid._get_coords()[0][1], gpoly.centroid._get_coords()[0][0])
#         r = results['results'][0]['formatted_address']
#         if r is not None:
#             address = r
        value = (tileX, tileY, name, area, bJointly, address, geom, j_point, center_point)
        values_list.append(value)
        print ("Verified " + name)
    
    try:
        cursor = connection.cursor()
        sql = """
            INSERT INTO Buildings(X, Y, Name, CalcArea, Jointly, Address, geom, j_point, cent_point)
            VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromWKB(%s::geometry, 4326), ST_GeomFromWKB(%s::geometry, 4326), ST_GeomFromWKB(%s::geometry, 4326))
        """
        psycopg2.extras.execute_batch(cursor, sql, values_list)
        print ("Inserted all Buildings for Tile ",tileX, "_",tileY )
        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    if(cursor):
        cursor.close()             
    return connection                
def write_roads2database(connection, tileX, tileY, roadtype, lines, gis_endpoints):
    
    values_list = []
    if gis_endpoints is None:
        print ('No end points provided')
    else:
        print (gis_endpoints)
        
    for i, l in enumerate(lines):
        if (len(l) == 1):
            continue
        glinestring = LineString(l)
        j_point = None
        try:
            
            for pp in glinestring.coords:
                p = (pp[0],pp[1])
                for ep in gis_endpoints:
                    if p == ep:
                        j_point = Point(p)
                        j_point = j_point.wkb 
                        continue
                        
            geom = LineString(glinestring.simplify(0.00001))
            name = 'linestring ' + str(i)  
            address = 'Info'
            geom =  geom.wkb  
            
            value = (tileX, tileY, name, roadtype, False, address, geom, j_point)
            values_list.append(value)
            print ("Verified " + name)                    

        except:
            return  
    try:
        cursor = connection.cursor()
        sql = """
            INSERT INTO Roads(X, Y, Name, Type, Jointly, Address, geom, j_point)
            VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromWKB(%s::geometry, 4326), ST_GeomFromWKB(%s::geometry, 4326))
        """
        psycopg2.extras.execute_batch(cursor, sql, values_list)
        print ("Inserted all Roads (%s) for Tile" % roadtype, tileX, "_",tileY)
        connection.commit()
                
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    if(cursor):
        cursor.close()             
    return connection    
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
    size = len(image)
    if (x > 0) and (x < size - 1) and (y > 0) and (y < size - 1):
        return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1], img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]
    if x_1 < 0:
        n1 = 0.0
        n2 = 0.0
        n3 = img[x][y1]
        n4 = img[x1][y1]
        n5 = img[x1][y]
        n6 = img[x1][y_1]
        n7 = img[x][y_1]        
        n8 = 0.0
    if y_1 < 0:
        n1 = img[x_1][y]
        n2 = img[x_1][y1]
        n3 = img[x][y1]
        n4 = img[x1][y1]
        n5 = img[x1][y]        
        n6 = 0.0
        n7 = 0.0
        n8 = 0.0
    if x1 > len(image) - 1:
        n1 = img[x_1][y]
        n2 = img[x_1][y1]
        n3 = img[x][y1]        
        n4 = 0.0
        n5 = 0.0
        n6 = 0.0
        n7 = img[x][y_1]
        n8 = img[x_1][y_1]        
    if y1 > len(image) - 1:
        n1 = img[x_1][y] 
        n2 = 0.0
        n3 = 0.0
        n4 = 0.0
        n5 = img[x1][y]
        n6 = img[x1][y_1]
        n7 = img[x][y_1]
        n8 = img[x_1][y_1]        
    return [ n1, n2, n3, n4, n5, n6, n7, n8 ] 

def getSkeletonIntersectionsAndEndPoints(skeleton):
    """ Given a skeletonised image, it will give the coordinates of the intersections of the skeleton.

    Keyword arguments:
    skeleton -- the skeletonised image to detect the intersections of

    Returns: 
    List of 2-tuples (x,y) containing the intersection coordinates
    """
    # A big list of valid intersections                  2 3 4
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
                         
    validEndpoint = [[1,0,0,0,0,0,0,0],
                      [0,1,0,0,0,0,0,0],
                      [0,0,1,0,0,0,0,0],
                      [0,0,0,1,0,0,0,0],
                      [0,0,0,0,1,0,0,0],
                      [0,0,0,0,0,1,0,0],
                      [0,0,0,0,0,0,1,0],
                      [0,0,0,0,0,0,0,1]];
                      
    endpoints = list();
                             
    image = skeleton.copy();
    image = image/255;
    intersections = list();
    
    size = len(image)
    for x in range(0,len(image)):
        for y in range(0,len(image[x])):  
            if (x == 0) or (x == size -1) or (y == 0) or ( y == size -1):
                if image[x][y] == 1:
                    image[x][y] = 0    
    
#     for x in range(1,len(image)-1):
#         for y in range(1,len(image[x])-1):
    for x in range(0,len(image)):
        for y in range(0,len(image[x])): 
            # If we have a white pixel
            if image[x][y] == 1:
                nbs = neighbours(x,y,image);
                valid = True;
                if nbs in validIntersection:
                    intersections.append((y,x));
                if nbs in validEndpoint:
                    endpoints.append((y,x));    
    # Filter intersections to make sure we don't count them twice or ones that are very close together
    for point1 in intersections:
        for point2 in intersections:
            if (((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) < 10**2) and (point1 != point2):
                intersections.remove(point2);
    # Remove duplicates
    intersections = list(set(intersections));
    endpoints = list(set(endpoints));
    
    return intersections, endpoints;
def getSkeletonIntersections(skeleton):

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
                         [1,0,1,1,0,1,0,0],[1,0,0,0,0,0,0,0],[0,1,0,0,0,0,0,0],
                         [0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],
                         [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]];
                         
                             
    image = skeleton.copy();
    image = image/255;
    intersections = list();

    size = len(image)
    for x in range(0,len(image)):
        for y in range(0,len(image[x])):  
            if (x == 0) or (x == size -1) or (y == 0) or ( y == size -1):
                if image[x][y] == 1:
                    image[x][y] = 0

    for x in range(0,len(image)):
        for y in range(0,len(image[x])):                       
            # If we have a white pixel
            if image[x][y] == 1:
                nbs = neighbours(x,y,image);
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
    