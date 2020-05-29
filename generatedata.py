'''
Created on May 27, 2020

@author: thaih
'''
import random
import time

latitude = 12.9716
longitude = 77.5946
file_name = 'data.csv'

def generate_random_data(lat, lon, num_rows, file_name):
    with open(file_name,'a') as output:
        output.write('timestamp,latitude,longitude\n')
        for _ in range(num_rows):
            time_stamp = time.time()
            generated_lat = random.random()/100
            generated_lon = random.random()/100
            output.write("{},{},{}\n".format(time_stamp, lat+generated_lat, lon+generated_lon))

generate_random_data(latitude,longitude, 10, file_name)