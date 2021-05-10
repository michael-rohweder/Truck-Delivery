# WGU C950 TRUCK DELIVERY ROUTING PROGRAM
# Designed/Developed by Michael Rohweder
# Student ID: 000970364
# C950 Task 1

import csv
import datetime

packages = []
distances = []

truck1_delivery_time = datetime.time(8, 0, 0)
truck2_delivery_time = datetime.time(9, 5, 0)
truck3_delivery_time = datetime.time(9, 53, 0)

truck1_delivery_start = datetime.time(8, 0, 0)
truck2_delivery_start = datetime.time(9, 5, 0)
truck3_delivery_start = datetime.time(9, 53, 0)

user_entered_time = datetime.time(7, 0, 0)

truck1 = []
truck2 = []
truck3 = []

optimized_truck1 = []
optimized_truck2 = []
optimized_truck3 = []

current_stop = "4001 South 700 East"
next_stop = ""
total_miles = 0


class Colors:
    HEADER = '\033[95m'
    NORMAL = '\033[0m'


class Package:
    def __init__(self, id_num, address, city, state, zip_code, deadline, weight, notes, status,
                 miles_from_last_stop, delivery_time, truck_departure_time):
        self.id_num = id_num
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.miles_from_last_hub = miles_from_last_stop
        self.delivery_time = delivery_time
        self.truck_departure_time = truck_departure_time


def get_user_time():
    try:
        time = input("Enter time to check: (hh:mm:ss) ")
        time_split = time.split(':')
        global user_entered_time
        user_entered_time = datetime.time(int(time_split[0]), int(time_split[1]), int(time_split[2]))
        return user_entered_time
    except ValueError:
        print("\nInvalid time entered")
        main()
    except IndexError:
        print("\nInvalid time entered")
        main()


def load_files():
    with open("manifest.csv") as manifest:
        # manifest_reader = csv.reader(manifest, delimiter=',')

        for rows in manifest.readlines():
            test = rows.split(",")
            package = Package(test[0], test[1], test[2], test[3], test[4], test[5], test[6], test[7], "", "", "", "")
            packages.append(package)
    with open("distance_table.csv") as distance_table:
        distance_reader = csv.reader(distance_table, delimiter=',')
        for rows in distance_reader:
            distances.append(rows)
    load_trucks()


def load_trucks():
    for package in packages:
        if "Wrong address" in package.notes:
            package.address = "410 S State St"
            package.zip_code = "84111"

        if package.deadline != "EOD":
            if "truck 2" not in package.notes and "Delayed" not in package.notes:
                package.truck_departure_time = truck1_delivery_start
                truck1.append(package)
            elif "Delayed" in package.notes:
                package.truck_departure_time = truck2_delivery_start
                truck2.append(package)
        else:
            if "truck 2" in package.notes:
                package.truck_departure_time = truck2_delivery_start
                truck2.append(package)
            elif "Delayed" in package.notes:
                package.truck_departure_time = truck2_delivery_start
                truck2.append(package)
            elif "Must be" in package.notes:
                package.truck_departure_time = truck1_delivery_start
                truck1.append(package)
            else:
                if len(truck2) > len(truck3):
                    package.truck_departure_time = truck3_delivery_start
                    truck3.append(package)
                else:
                    package.truck_departure_time = truck2_delivery_start
                    truck2.append(package)
    optimize_trucks()


def main():
    print("\n\nHello and welcome to delivery manager\n")
    print("1) Check package status")
    print("2) Check all deliveries")
    print("3) Check truck status")
    print("4) Exit")

    command = input("\nEnter a command (1 - 4): ")

    try:
        if int(command) == 1:
            get_package_status()
        elif int(command) == 2:
            get_all_deliveries()
        elif int(command) == 3:
            truck = input("Enter truck number (1-3): ")
            get_truck_status(int(truck))
        elif int(command) == 4:
            quit()
        else:
            print("\nError, unrecognized command")
            main()
    except ValueError:
        print("\nError, unrecognized command")
        main()

def optimize_trucks():
    global current_stop
    global total_miles
    global truck1_delivery_time
    global truck2_delivery_time
    global truck3_delivery_time
    global user_entered_time
    next_distance = 100
    current_stop_row = -1
    current_stop_col = -1
    next_address = ""
    total_distance_truck1 = 0
    total_distance_truck2 = 0
    total_distance_truck3 = 0

    '''
    Optimization for truck 1
    While the original delivery list is not empty, loop through and find the next closest stop
    Load that stop onto the optimized list and remove it from the original list
    Update the total distance driven for truck 1
    '''

    while len(truck1) > 0:
        for distance in distances:
            if distance[1] == current_stop:
                current_stop_row = distance[0]
                current_stop_col = int(current_stop_row) + 2

        for row in range(int(current_stop_row), len(distances)):
            check_distance = distances[row][current_stop_col]
            if float(next_distance) > float(check_distance) > 0:
                for package in truck1:
                    if distances[row][1] == package.address:
                        next_distance = check_distance
                        next_address = distances[row][1]

        for col in range(int(current_stop_col), 2, -1):
            check_distance = float(distances[int(current_stop_row)][col])
            if float(check_distance) < float(next_distance):
                for package in truck1:
                    check_stop = distances[int(col) - 2][1]
                    if check_stop == package.address:
                        next_distance = check_distance
                        next_address = distances[int(col) - 2][1]

        for package in truck1[:]:
            if next_address == package.address:
                package.status = "Loaded onto delivery truck"
                package.miles_from_last_hub = next_distance

                delivery_hour = truck1_delivery_time.hour
                delivery_time_in_minutes = (float(next_distance) / 18) * 60
                delivery_time_in_seconds = (delivery_time_in_minutes % 1) * 60

                minute_add_time = int(delivery_time_in_minutes)
                truck_time_minute = truck1_delivery_time.minute
                total_minute_add = int(minute_add_time) + int(truck_time_minute)

                second_add_time = int(delivery_time_in_seconds)
                truck_time_seconds = truck1_delivery_time.second
                total_second_add = second_add_time + truck_time_seconds

                if int(total_minute_add) >= 60:
                    delivery_hour += 1
                    total_minute_add -= 60
                if int(total_second_add) >= 60:
                    total_minute_add += 1
                    total_second_add -= 60
                truck1_delivery_time = datetime.time(delivery_hour, total_minute_add, int(delivery_time_in_seconds))
                package.delivery_time = truck1_delivery_time
                current_stop = package.address
                optimized_truck1.append(package)
                truck1.remove(package)
                total_distance_truck1 += float(next_distance)
                next_distance = 100
                next_address = ""

    print("Total distance truck 1: " + str(total_distance_truck1))
    total_miles += total_distance_truck1

    '''
    Optimization for truck 2
    '''
    current_stop = "4001 South 700 East"

    while len(truck2) > 0:
        for distance in distances:
            if distance[1] == current_stop:
                current_stop_row = distance[0]
                current_stop_col = int(current_stop_row) + 2

        for row in range(int(current_stop_row), len(distances)):
            check_distance = distances[row][current_stop_col]
            if float(next_distance) >= float(check_distance) > 0:
                for package in truck2:
                    if distances[row][1] == package.address:
                        next_distance = check_distance
                        next_address = distances[row][1]

        for col in range(int(current_stop_col), 2, -1):
            check_distance = float(distances[int(current_stop_row)][col])
            if float(check_distance) < float(next_distance):
                for package in truck2:
                    check_stop = distances[int(col) - 2][1]
                    if check_stop == package.address:
                        next_distance = check_distance
                        next_address = distances[int(col) - 2][1]

        for package in truck2[:]:
            if next_address == package.address:
                package.status = "Loaded onto delivery truck"
                package.miles_from_last_hub = next_distance
                delivery_hour = truck2_delivery_time.hour

                delivery_time_in_minutes = (float(next_distance) / 18) * 60
                delivery_time_in_seconds = (delivery_time_in_minutes % 1) * 60

                minute_add_time = int(delivery_time_in_minutes)
                truck_time_minute = truck2_delivery_time.minute
                total_minute_add = int(minute_add_time) + int(truck_time_minute)

                second_add_time = int(delivery_time_in_seconds)
                truck_time_seconds = truck2_delivery_time.second
                total_second_add = second_add_time + truck_time_seconds
                if int(total_minute_add) >= 60:
                    delivery_hour += 1
                    total_minute_add -= 60
                if int(total_second_add) >= 60:
                    total_minute_add += 1
                    total_second_add -= 60
                truck2_delivery_time = datetime.time(delivery_hour, total_minute_add, int(delivery_time_in_seconds))
                package.delivery_time = truck2_delivery_time
                current_stop = package.address
                optimized_truck2.append(package)
                truck2.remove(package)
                total_distance_truck2 += float(next_distance)
                next_distance = 100
                next_address = ""

    print("Total distance truck 2: " + str(total_distance_truck2))
    total_miles += total_distance_truck2

    '''
        Optimization for truck 3
    '''
    current_stop = "4001 South 700 East"

    while len(truck3) > 0:
        for distance in distances:
            if distance[1] == current_stop:
                current_stop_row = distance[0]
                current_stop_col = int(current_stop_row) + 2

        for row in range(int(current_stop_row), len(distances)):
            check_distance = distances[row][current_stop_col]
            if float(next_distance) >= float(check_distance) > 0:
                for package in truck3:
                    if distances[row][1] == package.address:
                        next_distance = check_distance
                        next_address = distances[row][1]

        for col in range(int(current_stop_col), 2, -1):
            check_distance = float(distances[int(current_stop_row)][col])
            if float(check_distance) < float(next_distance):
                for package in truck3:
                    check_stop = distances[int(col) - 2][1]
                    if check_stop == package.address:
                        next_distance = check_distance
                        next_address = distances[int(col) - 2][1]

        for package in truck3[:]:
            if next_address == package.address:
                package.status = "Loaded onto delivery truck"
                package.miles_from_last_hub = next_distance
                delivery_hour = truck3_delivery_time.hour

                delivery_time_in_minutes = (float(next_distance) / 18) * 60
                delivery_time_in_seconds = (delivery_time_in_minutes % 1) * 60

                minute_add_time = int(delivery_time_in_minutes)
                truck_time_minute = truck3_delivery_time.minute
                total_minute_add = int(minute_add_time) + int(truck_time_minute)

                second_add_time = int(delivery_time_in_seconds)
                truck_time_seconds = truck3_delivery_time.second
                total_second_add = second_add_time + truck_time_seconds
                if int(total_minute_add) >= 60:
                    delivery_hour += 1
                    total_minute_add -= 60
                if int(total_second_add) >= 60:
                    total_minute_add += 1
                    total_second_add -= 60
                truck3_delivery_time = datetime.time(delivery_hour, total_minute_add, int(delivery_time_in_seconds))
                package.delivery_time = truck3_delivery_time
                current_stop = package.address
                optimized_truck3.append(package)
                truck3.remove(package)
                total_distance_truck3 += float(next_distance)
                next_distance = 100
                next_address = ""

    print("Total distance truck 3: " + str(total_distance_truck3))
    total_miles += total_distance_truck3
    print("Total miles driven: " + str(total_miles))

    main()


def get_package_status():
    package_id = input("Enter package ID: ")
    user_time = get_user_time()

    for package in packages:
        if package.id_num == package_id:
            if user_time > package.delivery_time:
                package.status = "Delivered at " + str(package.delivery_time)
            elif package.delivery_time > user_time > package.truck_departure_time:
                package.status = "Loaded on delivery truck"
            elif user_time < truck1_delivery_start:
                package.status = "At delivery hub"
            if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
                package.status = "DELAYED IN FLIGHT"
            print("\nID:            " + package.id_num)
            print("Address:       " + package.address)
            print("City:          " + package.city)
            print("State:         " + package.state)
            print("Zip:           " + package.zip_code)
            print("Deadline:      " + package.deadline)
            print("Weight:        " + package.weight)
            print("Notes:         " + package.notes)
            print("Status:        " + package.status)
    main()


def get_all_deliveries():
    user_time = get_user_time()
    print("All deliveries:\n")
    print(Colors.HEADER, '%-3s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
          '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
          '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)
    for package in packages:
        if user_time < package.truck_departure_time:
            package.status = "At hub"
        elif package.truck_departure_time <= user_time < package.delivery_time:
            package.status = "On delivery truck"
        elif user_time >= package.delivery_time:
            package.status = "Delivered at " + str(package.delivery_time)
        if "Delayed" in package.notes and user_time < datetime.time(9,5,0):
            package.status = "DELAYED IN FLIGHT"
        print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
              '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
              '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
    main()


def get_truck_status(truck):
    user_time = get_user_time()
    for package in packages:
        if user_time < package.truck_departure_time:
            package.status = "At hub"
        elif package.truck_departure_time <= user_time < package.delivery_time:
            package.status = "On delivery truck"
        elif user_time >= package.delivery_time:
            package.status = "Delivered at " + str(package.delivery_time)
        if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
            package.status = "DELAYED IN FLIGHT"
    if truck == 1:
        if len(optimized_truck1) != 0:
            print(Colors.HEADER, '%-3s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
                  '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
                  '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)
            for package in optimized_truck1:
                print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
                      '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
                      '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
            print("\nTotal Deliveries on truck: " + str(len(optimized_truck1)))
        else:
            print("\nThis truck is empty!")
    if truck == 2:
        if len(optimized_truck2) != 0:
            print(Colors.HEADER, '%-3s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
                  '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
                  '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)
            for package in optimized_truck2:
                print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
                      '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
                      '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
            print("\nTotal Deliveries on truck: " + str(len(optimized_truck2)))
        else:
            print("\nThis truck is empty!")
    if truck == 3:
        if len(optimized_truck3) != 0:
            print(Colors.HEADER, '%-3s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
                  '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
                  '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)
            for package in optimized_truck3:
                print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
                      '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
                      '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
            print("\nTotal Deliveries on truck: " + str(len(optimized_truck3)))
        else:
            print("\nThis truck is empty!")
    main()


load_files()
