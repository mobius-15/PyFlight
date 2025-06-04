'''
Created on May 15, 2025

@author: redbu
'''
import random
                        #throttle=1.0, use_ab=True
def compute_climb_fuel(aircraft, dt_min, use_ab=True):
    if use_ab:
        ab_time = min(0.05, dt_min)  # 0.05時間 = 3分
        mil_time = max(dt_min - ab_time, 0)
        aircraft.afterburner = True
        ab_burn = aircraft.update_fuel(ab_time * 60, throttle=1.0)
        aircraft.afterburner = False
        mil_burn = aircraft.update_fuel(mil_time * 60, throttle=0.9)
        return ab_burn + mil_burn
    else:
        aircraft.afterburner = False
        return aircraft.update_fuel(dt_min * 60, throttle=0.9)
    
def compute_descent_fuel(aircraft, dt_min, throttle=0.3):
    aircraft.afterburner = False
    return aircraft.update_fuel(dt_min * 60, throttle)

def compute_acceleration_fuel(aircraft, dt_min, throttle=0.8):
    aircraft.afterburner = False
    return aircraft.update_fuel(dt_min * 60, throttle)

def compute_deceleration_fuel(aircraft, dt_min, throttle=0.5):
    aircraft.afterburner = False
    return aircraft.update_fuel(dt_min * 60, throttle)

def compute_cap_fuel(aircraft, duration_min = 15, throttle = 0.4, radius_nm = 10):
    """CAPフェーズ中の燃料消費を計算"""
    ab_flag = False  # 通常はA/Bなし
    aircraft.afterburner = ab_flag
    flow = aircraft.get_fuel_flow(throttle)
    burn = flow * (duration_min / 60)
    aircraft.remaining_fuel = max(aircraft.remaining_fuel - burn, 0)
    return burn


def compute_orbit_fuel(aircraft, duration_min = 10, throttle = 0.5, radius_nm = 20):
    """
    軍用の監視・旋回周回フェーズ
    """
    aircraft.afterburner = False
    flow = aircraft.get_fuel_flow(throttle)
    burn = flow * (duration_min / 60.0)
    aircraft.remaining_fuel = max(aircraft.remaining_fuel - burn, 0)
    return burn


def compute_refuel_gain(aircraft, available_fuel = 6000, max_refuel = 10000):
    """
    空中給油による補給量を算出（仮定）
    :param aircraft: 航空機
    :param available_fuel: 給油機の余剰燃料
    :param max_refuel: 機体が一度に受け取れる上限
    :return: 補給された燃料量
    """
    fuel_needed = aircraft.total_fuel - aircraft.remaining_fuel
    fuel_given = min(fuel_needed, available_fuel, max_refuel)
    aircraft.remaining_fuel += fuel_given
    return fuel_given

