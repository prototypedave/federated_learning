#!/usr/bin/env python3

""" All functions that generate data in the entire system """

import random, csv
from typing import List

def calculate_rs(obs, wth, spd, dist, rdc, tm) -> int:
    risk_severity = obs + wth + spd + dist + rdc + tm
    
    if risk_severity >= 10:
        # Find the feature with the highest contribution to risk_severity and reduce it by the necessary amount
        max_contribution = max(obs, wth, spd, dist, rdc, tm)
        if max_contribution == obs:
            obs -= (risk_severity - 9)
        elif max_contribution == wth:
            wth -= (risk_severity - 9)
        elif max_contribution == spd:
            spd -= (risk_severity - 9)
        elif max_contribution == dist:
            dist -= (risk_severity - 9)
        elif max_contribution == rdc:
            rdc -= (risk_severity - 9)
        elif max_contribution == tm:
            tm -= (risk_severity - 9)

        risk_severity = obs + wth + spd + dist + rdc + tm
        
    return risk_severity


def obstacles_data(obstacles: str) -> int:
    obs: int = 0
    if obstacles == 'poor':
        obs = 2
    elif obstacles == 'fair':
        obs = 1
    elif obstacles == 'good':
        obs = 0
    else:
        raise ValueError(f'Obstacle is undefined')
    return obs


def weather_data(weather: str) -> int:
    wth: int = 0
    if weather == 'rainy':
        wth = 1
    elif weather == 'clear':
        wth = 0
    else:
        raise ValueError(f'Weather is undefined')
    return wth


def road_data(road: str) -> int:
    rd: int = 0
    if  road == 'potholes':
        rd = 2
    elif road == 'slippery':
        rd = 1
    elif road == 'clear':
        rd = 0
    else:
        raise ValueError(f'Road condition is undefined')
    return rd

def time_data(time: str) -> int:
    tm: int = 0
    if time == 'night':
        tm = 1
    elif time == 'day':
        tm = 0
    else:
        raise ValueError(f'Time is undefined')
    return tm

def distance_data(distance: int) -> int:
    dist: int = 0
    if distance > 600:
        dist = 2
    elif distance > 300:
        dist = 1
    elif distance > 0:
        dist = 0
    else:
        raise OverflowError(f'Out of bounds distance')
    return dist

def speed_data(speed: int) -> int:
    spd: int = 0
    if speed > 110:
        spd = 2
    elif speed > 80:
        spd = 1
    elif speed >= 50:
        spd = 0
    else:
        raise OverflowError(f'Speed out of bounds')
    return spd
    
def generate_data():
    # Generates random data for the features to be used as dataset 
    obstacles = random.randint(0, 2) 
    weather = random.randint(0, 1)
    speed = random.randint(0, 2) 
    distance = random.randint(0, 2)
    road_condition = random.randint(0, 2)
    time = random.randint(0, 1)
    risk_severity = obstacles + weather + speed + distance + road_condition + time
    
    if risk_severity >= 10:
        # Find the feature with the highest contribution to risk_severity and reduce it by the necessary amount
        max_contribution = max(obstacles, weather, speed, distance, road_condition, time)
        if max_contribution == obstacles:
            obstacles -= (risk_severity - 9)
        elif max_contribution == weather:
            weather -= (risk_severity - 9)
        elif max_contribution == speed:
            speed -= (risk_severity - 9)
        elif max_contribution == distance:
            distance -= (risk_severity - 9)
        elif max_contribution == road_condition:
            road_condition -= (risk_severity - 9)
        elif max_contribution == time:
            time -= (risk_severity - 9)
        risk_severity = risk_severity = obstacles + weather + speed + distance + road_condition + time
        
    return [obstacles, weather, speed, distance, road_condition, time, risk_severity]

def get_node_address(dist: List[int], pos: int) -> tuple:
    # Remove the pos value from dist if it exists in the list
    dist = [x for x in dist if x != pos]

    if not dist:
        # Handle the case where dist becomes empty after removing pos
        return None, None

    # Find the closest value to pos
    closest_value = min(dist, key=lambda x: abs(x - pos))

    # Find the index of the closest value in the original list
    closest_index = dist.index(closest_value)

    return closest_index, closest_value
        
def calculate_bandwidth(qos: float) -> int:
    # calculates bandwidth based on the value of qos
    bandwidth: int = 5
    # high
    if qos > 107: 
        bandwidth = random.randint(100, 200)
    elif qos > 54:
        bandwidth = random.randint(20, 100)
    else:
        bandwidth = random.randint(5, 20)
    return bandwidth

def calculate_bitrate(speed: int, distance: int) -> int:
    # assume 100mbs is to be contended for each switch
    bitrate: int = int(100 / distance)
    return bitrate

def calculate_num_antennas(dist: int) -> int:
    num: int = 0
    if dist > 50:
        num = 3
    elif dist > 25:
        num = 2
    else:
        num = 1
    return num

def write_to_csv(filepath, x, y):
    # Open the file in append mode
    with open(filepath, 'a', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the updated values to the CSV file
        writer.writerow([x, y])

def network_overhead(bandwidth: int, bitrate: int, antennas: int):
    # get the total required resources
    max_resources: int = 400 + 236 + 5
    total_resources_used = bandwidth + bitrate + antennas
    overhead = total_resources_used / max_resources * 100
    return overhead

def computational_complexity(processor: float, ram: float):
    # get the total required resources
    max_resources: int = 5 + 2048
    total_resources_used = processor + ram
    complexity = total_resources_used / max_resources * 100
    return complexity

def calculate_collision_risk(distance: int):
    dist = max(0, min(distance, 900))
    risk = 100 - ((distance - 0) / (900 - 0)) * 100
    return risk

def write_csv(filepath, x, y, z):
     with open(filepath, 'a', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the updated values to the CSV file
        writer.writerow([x, y, z])

def find_value_index(value_list, target_number):
    closest_index = None
    closest_difference = float('inf') 
    
    for index, value in enumerate(value_list):
        difference = target_number - value
        if difference >= 0 and difference < closest_difference:
            closest_difference = difference
            closest_index = index
    
    return closest_index