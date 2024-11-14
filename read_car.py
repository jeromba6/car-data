#!/usr/bin/env python3
"""
Script to read the data from the Hyundai / Kia API and store it in a json files.
"""
import hyundai_kia_connect_api
import json
import argparse
import copy
import os
from collections import defaultdict
from datetime import datetime


def main():
    """
    Main function to read the data from the Kia API and store it in a json file.
    """

    config = parse_args()

    # Create a VehicleManager object
    vm = hyundai_kia_connect_api.VehicleManager(
        region=config.get('region', 1),
        brand=config.get('brand', 1),
        username=config['username'],
        password=config['password'],
        pin=config.get('pin', '1234'))
    vm.check_and_refresh_token()
    vm.update_all_vehicles_with_cached_state()

    # Read the json file
    if 'fulljsonfile' in config.keys():
        json_file = config['fulljsonfile']
    elif 'relevantjsonfile' in config.keys():
        json_file = config['relevantjsonfile']
    else:
        raise ValueError('At least one of the following is required: fulljsonfile, relevantjsonfile')

    json_file_tmp = f'{json_file}.tmp'

    try:
        with open(json_file, 'r') as f:
            json_file_content = json.load(f)
    except:
        # print(e)
        json_file_content = {}

    # Read the data from the vehicles and loop over all vehicles
    data = vm.vehicles
    keys = data.keys()
    for car in keys:

        # Check if vehicle is in the json file and add it if it is not
        if car not in json_file_content.keys():
            json_file_content[car] = []

        # Alter the data collected so it can be stored in the json file
        car_data = str(data[car]).split('data=')[1].replace("'", '"').replace('True','true').replace('False','false')

        # Collect last stored data and compare it with the new data
        car_data_json = json.loads(car_data[:-1])
        if len(json_file_content[car]) < 3:
            json_file_content[car].append(car_data_json)
        else:
            # Store the data in the json file if there are changes in the data
            if changes_in_data(json_file_content[car], car_data_json):
                json_file_content[car].append(car_data_json)
            else:
                json_file_content[car][-1] = car_data_json

    if 'fulljsonfile' in config.keys():
        with open(json_file_tmp, "w") as f:
            json.dump(json_file_content, f)

    # Store only relevant data in a new json file
    if 'relevantjsonfile' in config.keys():
        useFullJsonFile = True
        if os.path.isfile(json_file):
            try:
                with open(json_file, 'r') as f:
                    relevantjsondata = json.load(f)
                    useFullJsonFile = False
            except ValueError:
                pass

        if useFullJsonFile:
            relevant_json_file_content = defaultdict(list)
            for index in range(len(keys)):
                car = list(keys)[index]
                for entry in json_file_content[car]:
                    relevant_entry = relevant_data(entry)
                    relevant_json_file_content[f'car{index}'].append(relevant_entry)
        else:
            relevant_json_file_content = relevantjsondata
            for index in range(len(keys)):
                car = list(keys)[index]
                entry = json_file_content[car][-1]
                relevant_entry = relevant_data(entry)
                if relevant_entry not in relevant_json_file_content[f'car{index}']:
                    relevant_json_file_content[f'car{index}'].append(relevant_entry)

        with open(json_file_tmp, "w") as f:
            json.dump(relevant_json_file_content, f)

    # Check if new json file is bigger than the old one and replace the old one
    if os.path.isfile(json_file):
        if os.path.getsize(json_file) < os.path.getsize(json_file_tmp):
            os.replace(json_file_tmp, json_file)
    else:
        os.replace(json_file_tmp, json_file)

    # Calculate km driven per time period
    if 'kmperperiodjsonfile' in config.keys() and 'relevantjsonfile' in config.keys():

        # Initalize the dictionary to store the km driven per period
        periods = ['day', 'week', 'month', 'year']
        km_per_period = {}
        for period in periods:
            km_per_period[period] = defaultdict(list)

        # Loop over all cars returned by the API
        for car in relevant_json_file_content.keys():
            start_period = {}
            for period in periods:
                start_period[period] = relevant_json_file_content[car][0]['odometer']

            # Loop over all entries for the car starting by the second entry
            for index in range(1, len(relevant_json_file_content[car])):

                # Loop over the periods and check if new period is reached and the odometer is higher than the start of the period
                for period in periods:
                    if determine_periode(relevant_json_file_content[car][index-1]['time'], period[0]) != determine_periode(relevant_json_file_content[car][index]['time'], period[0]) and relevant_json_file_content[car][index]['odometer'] > start_period[period]:

                        # Conditions are fulfilled, store the km driven in the period
                        km_per_period[period][car].append({
                            'time': determine_periode(relevant_json_file_content[car][index-1]['time'], period[0]),
                            'km': round(relevant_json_file_content[car][index]['odometer'] - start_period[period], 1)
                        })

                        # Update the start of the period
                        start_period[period] = relevant_json_file_content[car][index]['odometer']

                    # Check if the last entry is reached and the odometer is higher than the start of the period
                    elif relevant_json_file_content[car][index] is relevant_json_file_content[car][-1] and relevant_json_file_content[car][index]['odometer'] > start_period[period]:
                        km_per_period[period][car].append({
                            'time': determine_periode(relevant_json_file_content[car][index]['time'], period[0]),
                            'km': round(relevant_json_file_content[car][index]['odometer'] - start_period[period], 1)
                        })

        # Store km driven of all periods in the json file
        period_json_file_content = {}
        for period in periods:
            period_json_file_content[period] = km_per_period[period]

        with open(config['kmperperiodjsonfile'], "w") as f:
            json.dump(period_json_file_content, f)


def relevant_data(data: dict) -> dict:
    """
    Only return the relevant data
    """
    return {
        'time': convert_time(data['vehicleStatus']['time']),
        'range': data['vehicleStatus']['evStatus']['drvDistance'][0]['rangeByFuel']['totalAvailableRange']['value'],
        'soc': data['vehicleStatus']['evStatus']['batteryStatus'],
        'odometer': data['odometer']['value'],
    }


def parse_args():
    """
    Read the config file if aguments for configfile is given and return the config as a dictionary.
    Parse the arguments from the command line and override config dictionary from configfile
    """

    parser = argparse.ArgumentParser(description='Read data from the Kia API and store it in a json files.')
    parser.add_argument('-u', '--username',
                        dest='user',
                        type=str,
                        help='Username for the Kia API')
    parser.add_argument('-p', '--password',
                        dest='password',
                        type=str,
                        help='Password for the Kia API')
    parser.add_argument('-P', '--pin',
                        dest='pin',
                        type=str,
                        help='Pin for the Kia API')
    parser.add_argument('-R', '--region',
                        dest='region',
                        type=int,
                        help='Region for the Kia API')
    parser.add_argument('-b', '--brand',
                        dest='brand',
                        type=int,
                        help='Brand for the Kia API')
    parser.add_argument('-c', '--configfile',
                        dest='configfile',
                        type=str,
                        help='Config file settings')
    parser.add_argument('-f', '--fulljsonfile',
                        dest='fulljsonfile',
                        type=str,
                        help='Full json file')
    parser.add_argument('-r', '--relevantjsonfile',
                        dest='relevantjsonfile',
                        type=str,
                        help='Relevant json file')
    parser.add_argument('-k', '--kmperperiodjsonfile',
                        dest='kmperperiodjsonfile',
                        type=str,
                        help='Km per period (day/week/month/year) json file')
    args = parser.parse_args()

    # Read the config file
    if args.configfile:
        with open(args.configfile) as f:
            config = json.load(f)
    else:
        config = {}

    # Update the config with the command line arguments
    if args.user:
        config['username'] = args.user
    if args.password:
        config['password'] = args.password
    if args.pin:
        config['pin'] = args.pin
    if args.region:
        config['region'] = args.region
    if args.brand:
        config['brand'] = args.brand
    if args.fulljsonfile:
        config['fulljsonfile'] = args.fulljsonfile
    if args.relevantjsonfile:
        config['relevantjsonfile'] = args.relevantjsonfile
    if args.kmperperiodjsonfile:
        config['kmperperiodjsonfile'] = args.kmperperiodjsonfile

    # Check if all required arguments are present
    if 'username' not in config.keys():
        raise ValueError('Username is required')
    if 'password' not in config.keys():
        raise ValueError('Password is required')
    if 'fulljsonfile' not in config.keys() and 'relevantjsonfile' not in config.keys() and 'kmperdayjsonfile' not in config.keys():
        raise ValueError('At least one of the following is required: fulljsonfile, relevantjsonfile')

    # Return the config
    return dict(config)


def determine_periode(timestamp: int, period: str = 'd') -> str:
    """
    Determine the period of the timestamp
    """
    if period == 'd':
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    if period == 'w':
        return datetime.fromtimestamp(timestamp).strftime('%Y-%W')
    elif period == 'm':
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m')
    elif period == 'y':
        return datetime.fromtimestamp(timestamp).strftime('%Y')


def changes_in_data(curent_data: list, new_data: dict) -> bool:
    """
    Check if there are changes in the data compare new data with last 2 entries
    """
    if len(curent_data) < 3:
        return True
    first = copy.deepcopy(curent_data[-2])
    second = copy.deepcopy(curent_data[-1])
    last = copy.deepcopy(new_data)
    if 'time' in first['vehicleLocation'].keys():
        del first['vehicleLocation']['time']
    if 'time' in first['vehicleStatus']:
        del first['vehicleStatus']['time']
    if 'time' in second['vehicleLocation'].keys():
        del second['vehicleLocation']['time']
    if 'time' in second['vehicleStatus']:
        del second['vehicleStatus']['time']
    if 'time' in last['vehicleLocation'].keys():
        del last['vehicleLocation']['time']
    if 'time' in last['vehicleStatus']:
        del last['vehicleStatus']['time']
    return first != second or second != last


def convert_time(time: str, string_format: str = '%Y%m%d%H%M%S') -> int:
    """
    Convert timestring to timestamp
    """
    return int(datetime.strptime(time, string_format).timestamp())


if __name__ == '__main__':
    main()
