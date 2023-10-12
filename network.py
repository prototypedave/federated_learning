#!/usr/bin/env python3

"""
"""

from vehicle import Vehicle
from typing import List


class Network:
    def __init__(self, vehicles: int) -> None:
        # store the vehicles instances in a list
        self.vehicles: List[Vehicle] = []

        # add the vehicles to the list
        for idx in range(vehicles):
            vehicle = Vehicle(index=idx)
            self.vehicles.append(vehicle)
        
        # store the distance in a list
        self.vehicle_distance: List[int] = []

        for vehicle in self.vehicles:
            dist = vehicle.distance
            self.vehicle_distance.append(dist)

    def get_closest_vehicle(self) -> Vehicle:
        

        