# Designed/Developed by Michael Rohweder - Student ID: 000970364
# C950 Task 1

import csv
import datetime


'''
GLOBAL VARIABLES
'''
package_hash_table = ""
num_lines = 0

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


class PackageHashTable:
    def __init__(self, size):  # Size is passed in from load_files, which reads the csv file for the max lines
        self.size = size
        self.hash_map = []     # Initialize the hash map with an empty array
        for _ in range(size):  # Fill the hash map with the required size of empty arrays
            self.hash_map.append([])

    def insert(self, val):      # Insert a value into the hash map: val is passed as a Package object
        key = val.id_num        # hash key
        bucket = hash(int(key)) % self.size  # bucket number
        if self.hash_map[bucket] is not None:  # if this bucket is not empty
            for kv in self.hash_map[bucket]:   # loops the items in the bucket
                if kv.id_num == key:           # if this item is in the bucket
                    kv = val                   # set bucket item to this item
                    return True
            self.hash_map[bucket].append(val)  # otherwise, add this item to the bucket
            return True
        else:
            self.hash_map[bucket] = val         # if bucket is empty, add this item to bucket
            return True

    def get(self, key):
        bucket = hash(int(key)) % self.size     # bucket number
        if self.hash_map[bucket] is not None:   # bucket is not empty
            for kv in self.hash_map[bucket]:    # loop items in bucket
                if int(kv.id_num) == int(key):  # item is found
                    return kv                   # return item
        return None                             # otherwise return nothing


class Colors:                                   # class for formatting colors in the console
    HEADER = '\033[95m'
    NORMAL = '\033[0m'


class Package:                                  # class for creating the Package objects
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


def get_user_time():                            # function to convert the user entered time to datetime object
    try:
        global user_entered_time
        time = input("Enter time to check: (hh:mm:ss) ")
        time_split = time.split(':')
        user_entered_time = datetime.time(int(time_split[0]), int(time_split[1]), int(time_split[2]))
        return user_entered_time
    except ValueError:                          # user entered invalid data
        print("\nInvalid time entered")
        main()
    except IndexError:                          # user entered invalid data
        print("\nInvalid time entered")
        main()


def load_files():                               # Load the CSV files for processing
    global package_hash_table
    global num_lines
    num_lines = len(open("manifest.csv").readlines())   # number of lines in the csv file
    package_hash_table = PackageHashTable(num_lines)    # create the hash table with the required number of lines
    with open("manifest.csv") as manifest:              # open the manifest.csv file
        # Complexity O(N)
        for rows in manifest.readlines():               # loop the file and store the line in the rows variable
            line = rows.split(",")                      # split the values by ','

            # create a package object for this line
            package = Package(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], "", "", "", "")
            if package.notes == "\n":                   # if no package notes, append NONE
                package.notes = "NONE"
            package_hash_table.insert(package)          # insert the package into the hash table
    with open("distance_table.csv") as distance_table:  # open the distance table csv
        distance_reader = csv.reader(distance_table, delimiter=',')
        for rows in distance_reader:
            distances.append(rows)                      # append the distance date to the list
    load_trucks()


def load_trucks():
    global package_hash_table

    # Complexity = O(N)
    for index in range(1, num_lines + 1):               # loop the hash table
        package = package_hash_table.get(index)         # create a package object for each iteration of the loop
        if "Wrong address" in package.notes:            # update the incorrect address
            package.address = "410 S State St"
            package.zip_code = "84111"

        '''
        preliminary sorting of packages onto trucks
        '''
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

    '''
    main menu
    '''

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

    # truck optimization function

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

    while len(truck1) > 0:   # find the current stop on the distance table
        # O(N)
        for distance in distances:
            if distance[1] == current_stop:
                current_stop_row = distance[0]
                current_stop_col = int(current_stop_row) + 2
        # O(N^2)
        for row in range(int(current_stop_row), len(distances)):  # find the closest stop going down the distance table
            check_distance = distances[row][current_stop_col]
            if float(next_distance) > float(check_distance) > 0:
                for package in truck1:
                    if distances[row][1] == package.address:
                        next_distance = check_distance
                        next_address = distances[row][1]

        # O(N^2)
        for col in range(int(current_stop_col), 2, -1):  # find the closest stop going left on the table
            check_distance = float(distances[int(current_stop_row)][col])
            if float(check_distance) < float(next_distance):
                for package in truck1:
                    check_stop = distances[int(col) - 2][1]
                    if check_stop == package.address:
                        next_distance = check_distance
                        next_address = distances[int(col) - 2][1]

        '''
        absolute closest stop has been located
        '''
        # O(N)
        for package in truck1[:]:    # check if the closest stop on truck 1 (COPY THE LIST FOR CONCURRENT MODIFICATION)
            if next_address == package.address:
                package.status = "En Route"
                package.miles_from_last_hub = next_distance

                '''
                Figure out the delivery time of the package
                '''
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
                truck1.remove(package)   # Remove this stop from truck one and add it to optimized truck1
                total_distance_truck1 += float(next_distance)  # update truck 1 distance driven
                next_distance = 100
                next_address = ""

    print("Total distance truck 1: " + str(total_distance_truck1))
    total_miles += total_distance_truck1  # update total miles for all trucks

    '''
    Optimization for truck 2 - same as truck 1
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
                package.status = "En Route"
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
        Optimization for truck 3 same as truck 1 & 2
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
                package.status = "En Route"
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
    print("Total miles driven: " + str(total_miles))  # print total distance traveled for all trucks

    main()


def get_package_status():
    package_id = input("Enter package ID: ")
    user_time = get_user_time()

    # complexity = O(1)
    package = package_hash_table.get(package_id)   # get the package from the hash table

    '''
    update package status based on users time
    '''
    if package.id_num == package_id:
        if user_time > package.delivery_time:
            package.status = "Delivered at " + str(package.delivery_time)
        elif package.delivery_time > user_time > package.truck_departure_time:
            package.status = "En Route"
        elif user_time < truck1_delivery_start:
            package.status = "At delivery hub"
        if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
            package.status = "DELAYED IN FLIGHT"

        '''
        print package status to console
        '''
        print(Colors.HEADER, "\nID:            ", Colors.NORMAL, package.id_num)
        print(Colors.HEADER + "Address:       ", Colors.NORMAL, package.address)
        print(Colors.HEADER + "City:          ", Colors.NORMAL, package.city)
        print(Colors.HEADER + "State:         ", Colors.NORMAL, package.state)
        print(Colors.HEADER + "Zip:           ", Colors.NORMAL, package.zip_code)
        print(Colors.HEADER + "Deadline:      ", Colors.NORMAL, package.deadline)
        print(Colors.HEADER + "Weight:        ", Colors.NORMAL, package.weight)
        print(Colors.HEADER + "Notes:         ", Colors.NORMAL, package.notes)
        print(Colors.HEADER + "Status:        ", Colors.NORMAL, package.status)
    main()


def get_all_deliveries():
    user_time = get_user_time()
    print("\nAll deliveries:\n")
    print(Colors.HEADER, '%-3s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
          '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
          '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)

    # Complexity = O(N)
    for index in range(1, num_lines + 1):
        # O(1)
        package = package_hash_table.get(index)

        '''
        update package status based on users time        
        '''
        if user_time < package.truck_departure_time:
            package.status = "At hub"
        elif package.truck_departure_time <= user_time < package.delivery_time:
            package.status = "En Route"
        elif user_time >= package.delivery_time:
            package.status = "Delivered at " + str(package.delivery_time)
        if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
            package.status = "DELAYED IN FLIGHT"
        '''
        Print package information
        '''
        print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
              '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
              '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
    main()


def get_truck_status(truck):
    user_time = get_user_time()

    if truck == 1:
        if len(optimized_truck1) != 0:
            print(Colors.HEADER, '\n%-4s' % "ID", '%-20s' % "ADDRESS", '%-15s' % "CITY",
                  '%-7s' % "STATE", '%-6s' % "ZIP", '%-12s' % "DEADLINE",
                  '%-8s' % "WEIGHT", '%-17s' % "NOTES", '%-15s' % "STATUS", Colors.NORMAL)
            # O(N)
            for package in optimized_truck1:

                if user_time < package.truck_departure_time:
                    package.status = "At hub"
                elif package.truck_departure_time <= user_time < package.delivery_time:
                    package.status = "En Route"
                elif user_time >= package.delivery_time:
                    package.status = "Delivered at " + str(package.delivery_time)
                if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
                    package.status = "DELAYED IN FLIGHT"

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
            # O(N)
            for package in optimized_truck2:

                if user_time < package.truck_departure_time:
                    package.status = "At hub"
                elif package.truck_departure_time <= user_time < package.delivery_time:
                    package.status = "En Route"
                elif user_time >= package.delivery_time:
                    package.status = "Delivered at " + str(package.delivery_time)
                if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
                    package.status = "DELAYED IN FLIGHT"

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
            # O(N)
            for package in optimized_truck3:

                if user_time < package.truck_departure_time:
                    package.status = "At hub"
                elif package.truck_departure_time <= user_time < package.delivery_time:
                    package.status = "En Route"
                elif user_time >= package.delivery_time:
                    package.status = "Delivered at " + str(package.delivery_time)
                if "Delayed" in package.notes and user_time < datetime.time(9, 5, 0):
                    package.status = "DELAYED IN FLIGHT"

                print('%-4s' % package.id_num, '%-20s' % package.address[0:15], '%-15s' % package.city[0:15],
                      '%-7s' % package.state, '%-6s' % package.zip_code, '%-12s' % package.deadline,
                      '%-8s' % package.weight, '%-17s' % package.notes[0:15], '%-15s' % package.status)
            print("\nTotal Deliveries on truck: " + str(len(optimized_truck3)))
        else:
            print("\nThis truck is empty!")
    main()


load_files()
