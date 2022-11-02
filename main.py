# Code by Alex Stråe, Sweden, AKA Dr-Wojtek @ GitHub
# Very cool ASCII logo by http://patorjk.com

from supertech import Supertrip
import addresses
import orders
import operator
import random
import os
import sys
import time

def by_distance(order):
    return order.get('distance')

def by_direction(order):
    return order.get('address').direction

def clear_window():
    os.system('cls' if os.name == 'nt' else 'clear')

def dialogue_return(input1="", input2="", input3="", input4=""):
    print("-" + '{:-^100s}'.format("-") + "-")
    print("|" + '{:^100s}'.format(input1 + input2) + "|")
    print("|" + '{:^100s}'.format(input3 + input4) + "|")
    print("-" + '{:-^100s}'.format("-") + "-")
    choice = input("\n")
    return choice

def print_logo(current_user, office):
    clear_window()
    print(f' _________                                   ________            .__   .__                        .__\n'
        f'/   _____/ __ __  ______    ____  _______    \______ \    ____   |  |  |__|___  __  ____   _______ |__|  ____     ______\n'
        f'\_____  \ |  |  \ \____ \ _/ __ \ \_  __ \    |    |  \ _/ __ \  |  |  |  |\  \/ /_/ __ \  \_  __ \|  |_/ __ \   /  ___/\n'
        f'/        \|  |  / |  |_> > \  ___/ |  | \/    |    `   \ \  ___/ |  |__|  | \   /  \  ___/  |  | \/|  | \  ___/  \___ \ \n'
        f'/_______ /|____/  |   __/   \___  >|__|      /_______  /  \___  >|____/|__|  \_/    \___  > |__|   |__|  \___  > /____  >\n'
        f'       \/         |__|          \/                   \/       \/                        \/                   \/       \/\n')
    print(f'\033[94mSuper Deliveries\033[0m system version 1.0 @ \033[92m{office}\033[0m.')
    if addresses.database:
        print(f'Database online!')
    print(f'Super Deliveries utilizes the Dynamic Knapsack solution with custom mods and a fusion of the A* search algorithm and custom logic,\n'
          f'providing shortest possible route instantly. Addresses and orders are loaded from a SQLite database.')
    print(f'\nWelcome back {current_user}.\n\n')

def print_orderlist(orderlist):
    total_weight = 0
    total_value = 0
    locations = 0
    sys.stdout.write("" + '{:^33s}'.format("Item to deliver:"))
    sys.stdout.write("" + '{:^10s}'.format("Value:"))
    sys.stdout.write("" + '{:^10s}'.format("Weight:"))
    sys.stdout.write("" + '{:^14s}'.format("Address (resets on every start):"))
    print("")
    print("" + '{:-^89s}'.format(""))
    for order in orderlist:
        total_weight += order['weight']
        total_value += order['value']
        locations += 1
        sys.stdout.write("| " + '{:^30s}'.format(order['name']) + "")
        sys.stdout.write("| " + '{:^10s}'.format("$" + str(order['value'])) + "")
        sys.stdout.write("| " + '{:^5s}'.format(str(order['weight']) + " kg") + "")
        sys.stdout.write("| " + '{:^35s}'.format(order['address'].name) + "|")
        print("")
    print("" + '{:-^89s}'.format(""))
    sys.stdout.write("Total:" + '{:^26s}'.format(""))
    sys.stdout.write("| " + '{:^10s}'.format("$" + str(total_value)))
    sys.stdout.write("|" + '{:^6s}'.format(str(total_weight) + " kg"))
    sys.stdout.write("|" + '{:^36s}'.format("Locations: " + str(locations)) + "|")
    print("")
    print("" + '{:-^89s}'.format(""))

# METHODS ABOVE

current_user = os.getlogin()
all_delivery_orders = orders.all_delivery_orders
todays_locations = list(addresses.manhattan_graph.keys())
logistics_office = addresses.thirty_seventh_and_fifth
todays_locations.remove(logistics_office)
new_trip = Supertrip(logistics_office, addresses.manhattan_graph, all_delivery_orders)
for item in all_delivery_orders:
    dice = random.randint(0, len(todays_locations)-1)
    item['address'] = todays_locations.pop(dice)
new_york_city = addresses.TwoDimensionalMap(addresses.manhattan_graph)
print_logo(current_user, logistics_office.name)
time.sleep(2)
print(f'Todays orders:')
print_orderlist(all_delivery_orders)
time.sleep(2)
choice = dialogue_return("Are you restricted by weight today and would like to grab the highest valuable combination?", "",
                         "Enter max weight in numbers if you are restricted, or press Enter to deliver all orders.")
restricted = True
total_value_to_deliver = 0
chosen_delivery_orders = []
try:
    choice = int(choice)
except ValueError:
    restricted = False
    print("It's nice that you have a large truck today, " + current_user + "!\n")
    time.sleep(1)
if restricted:
    items_to_deliver = new_trip.drivers_dynamic_knapsack('weight', choice)
    total_value_to_deliver = items_to_deliver[0]
    for order in all_delivery_orders:
        if order['name'] in items_to_deliver:
         chosen_delivery_orders.append(order)
else:
    chosen_delivery_orders = all_delivery_orders.copy()

print("This is your chosen order list:")
print_orderlist(chosen_delivery_orders)

do_it = input("\n\n\nPress Enter to see your super fast route!")
print_logo(current_user, logistics_office.name)

# THIS CALCULATES ROUTE BY SHORTEST DISTANCE FROM OFFICE
# (OFTEN WEAKEST RESULTS. SOME CPU-USAGE SINCE A* HAVE RUN ONCE PER TARGET)
for order in chosen_delivery_orders:
    target, distance, path = new_trip.a_star(new_trip.map, logistics_office, order.get('address'))
    order['distance'] = distance
    order['path'] = path

chosen_delivery_orders.sort(key=by_distance)
chosen_delivery_orders.append({'name' : 'Return to Base', 'weight' : 0, 'value' : 0, 'address' :logistics_office, 'distance': chosen_delivery_orders[-1].get('distance'), 'path' : []})

total_distance_by_foot = 0
for order in chosen_delivery_orders:
    if order['name'] != 'Return to Base':
        total_distance_by_foot += order['distance'] * 2

total_distance_by_shortest = 0
starting_location = new_trip.start
for order in chosen_delivery_orders:
    target, distance, path = new_trip.a_star(new_trip.map, starting_location, order.get('address'))
    starting_location = order.get('address')
    total_distance_by_shortest += distance

# THIS CALCULATES ROUTE BY DIRECTION
# (OFTEN YIELDS BETTER DISTANCE THAN BY SHORTEST DISTANCE. A* IS NOT NEEDED)
chosen_delivery_orders.pop(-1)
optimized_route = chosen_delivery_orders.copy()
optimized_route.sort(key=by_direction)
optimized_route.append({'name' : 'Return to Base', 'weight' : 0, 'value' : 0, 'address' :logistics_office, 'distance': chosen_delivery_orders[-1].get('distance'), 'path' : []})

total_distance_by_direction = 0
starting_location = new_trip.start
for order in optimized_route:
    target, distance, path = new_trip.a_star(new_trip.map, starting_location, order.get('address'))
    starting_location = order.get('address')
    total_distance_by_direction += distance

# THIS CALCULATES WITH SUPER-DELIVERIES LOGIC AND A* SEARCH ALGO:
optimized_route.pop(-1)
super_optimized_route = []
# Getting all empty directions, if any:
number_per_direction = {'N)' : 0, 'NE' : 0, 'E)' : 0, 'SE' : 0, 'S)' : 0, 'SW' : 0, 'W)' : 0,'NW' : 0}
for order in optimized_route:
    for direction in number_per_direction:
        if direction == order['address'].direction[3:5]:
            number_per_direction[direction] += 1
            break
# Sorting clockwise, starting with first direction after empty one(s).
# If no empty ones it starts with direction with lowest deliveries:
directions_asc = sorted(number_per_direction.items(), key=operator.itemgetter(1))
first_direction = directions_asc[0][0]
compass = ['N)', 'NE', 'E)', 'SE', 'S)', 'SW', 'W)', 'NW']
index = compass.index(first_direction)
if optimized_route[0]['address'] == logistics_office:
    super_optimized_route.append(optimized_route.pop(0))
for i in range(index, len(compass)):
    for delivery_order in optimized_route:
        if delivery_order['address'].direction[3:5] == compass[i]:
            super_optimized_route.append(delivery_order)
for i in range(0, index):
    for delivery_order in optimized_route:
        if delivery_order['address'].direction[3:5] == compass[i]:
            super_optimized_route.append(delivery_order)
# Then it's time for A* to optimize within directions and then closest in next direction.
# Uncomment print statements for verbose A* sorting.
for i in range(len(super_optimized_route)-1):
    if super_optimized_route[i]['address'] == logistics_office:
        continue
    current_dir = super_optimized_route[i]['address'].direction[3:5]
    if super_optimized_route[i+1]['address'].direction[3:5] == current_dir:
        current_distance_next = new_trip.a_star(new_trip.map, super_optimized_route[i]['address'], super_optimized_route[i+1]['address'])[1]
        current_next_address = super_optimized_route[i+1]
        grab = None
        for delivery_order in super_optimized_route:
            if delivery_order['address'].direction[3:5] == current_dir:
                already_delivered_order = None
                if i > 0:
                    already_delivered_order = super_optimized_route[i-1]
                if delivery_order != super_optimized_route[i] and delivery_order != already_delivered_order and delivery_order != current_next_address:
                    other_target_distance = new_trip.a_star(new_trip.map, super_optimized_route[i]['address'], delivery_order['address'])[1]
                    if other_target_distance < current_distance_next:
                        current_distance_next = other_target_distance
                        grab = delivery_order
        if grab:
            #print("FOUND CLOSER TARGET WITHIN DIR")
            #print("PUTTING " + grab['name'] + " AFTER " + super_optimized_route[i]['name'] )
            super_optimized_route.remove(grab)
            super_optimized_route.insert(i+1, grab)

    elif super_optimized_route[i]['address'].direction[3:5] != super_optimized_route[i+1]['address'].direction[3:5]:
        next_dir = super_optimized_route[i+1]['address'].direction[3:5]
        current_distance_next = new_trip.a_star(new_trip.map, super_optimized_route[i]['address'], super_optimized_route[i+1]['address'])[1]
        grab = None
        for delivery_order in super_optimized_route:
            if delivery_order['address'].direction[3:5] == next_dir:
                other_target_distance = new_trip.a_star(new_trip.map, super_optimized_route[i]['address'], delivery_order['address'])[1]
                if other_target_distance < current_distance_next:
                    current_distance_next = other_target_distance
                    grab = delivery_order
        if grab:
            #print("FOUND CLOSER TARGET FOR NEXT DIR")
            #print("PUTTING " + grab['name'] + " AFTER " + super_optimized_route[i]['name'])
            super_optimized_route.remove(grab)
            super_optimized_route.insert(i + 1, grab)

# OPTIMIZING FINISHED. CALCULATING DISTANCE AND DISPLAYING FINAL ROUTE:
super_optimized_route.append({'name' : 'Return to Base', 'weight' : 0, 'value' : 0, 'address' :logistics_office, 'distance': chosen_delivery_orders[-1].get('distance'), 'path' : []})
total_distance_by_super = 0
starting_location = new_trip.start
counter = 1
total_path = []
for order in super_optimized_route:
    order.get('address').visit_number.append(counter)
    target, distance, path = new_trip.a_star(new_trip.map, starting_location, order.get('address'))
    for address in path:
        if path not in total_path:
            total_path.append(address)
    starting_location = order.get('address')
    total_distance_by_super += distance
    counter += 1
for address in addresses.manhattan_graph:
    for visited in total_path:
        if address.name == visited:
            address.visit_number.append("*")
            break

#UPDATE DB WITH RESULTS BEFORE DISPLAYING RESULTS:
addresses.cur.execute("UPDATE history SET program_runs = program_runs + 1")
addresses.database.commit()
if total_distance_by_super <= total_distance_by_direction and total_distance_by_super <= total_distance_by_shortest:
    addresses.cur.execute("UPDATE history SET counter_FTL_right = counter_FTL_right + 1")
    addresses.database.commit()
res = addresses.cur.execute("SELECT program_runs FROM history")
program_runs = res.fetchone()
res = addresses.cur.execute("SELECT counter_FTL_right FROM history")
counter_super_best = res.fetchone()
#

new_york_city.display_map()
print(f'\n\nThe \033[92mgreen\033[0m text is where the office is located. The \033[93myellow\033[0m number is the first delivery. Follow the \033[94mblue *\033[0m to see the path the program traveled from the office.\n'
      f'The distance between adjacent addresses can differ depending on address, even though it may appear to be the same between all addresses. The distance is provided by the graph the program use.\n'
      f'\nThe path shown above is the most optimized one the program use; First it chooses a direction proceeding a direction without deliveries (if any). Then it travels clockwise.\n'
      f'Secondly, it looks for the nearest target, as long as that target is in the current direction.\n'
      f'Third, after delivering the last order in the current direction, it visits the closest target in next clockwise direction, and then repeats the second stage. Unless there are no deliveries left.\n'
      f'Since the first direction was proceeding one without deliveries (if any such existed), the route will skip as many empty areas as possible.\n'
      f'The route finally returns to base. The distance is calculated below for this route, called the \033[94mSuper Deliveries\033[0m route, as well as for other routes. All routes returns to base in the end.\n'
      f'\nDistance for delivering orders one by one, going back and forth from office: {total_distance_by_foot} kilometers.\n'
      f'Distance for route sorted after shortest distance from office:               {total_distance_by_shortest} kilometers. Saved {total_distance_by_foot - total_distance_by_shortest} kilometers of traveling!\n'
      f'Distance for route sorted by direction:                                      {total_distance_by_direction} kilometers. Saved {total_distance_by_foot - total_distance_by_direction} kilometers of traveling!\n'
      f'Distance for route optimized by \033[94mSuper Deliveries:                            {total_distance_by_super}\033[0m kilometers. Saved \033[94m{total_distance_by_foot - total_distance_by_super}\033[0m kilometers of traveling!\n'
      f'\nThis copy of the program has run {str(program_runs[0])} times. Of the three methods, Super Deliveries has found the fastest route {str(counter_super_best[0])} times!')
addresses.database.close()
orders.database.close()
restart = dialogue_return("Press Enter to restart the program. Input anything else to exit.")
if restart == "":
    os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
