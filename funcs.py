#!/usr/bin/env python3

""" All functions that generate data in the entire system """

import random
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
    elif speed > 50:
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

def get_node_address(dist: List[int], pos: int):
    closest_value = min(dist, key=lambda x: abs(x - pos))
    for idx in dist:
        if idx == closest_value:
            return idx, closest_value
