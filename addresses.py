# Code by Alex Stråe, Sweden, AKA Dr-Wojtek @ GitHub

from math import inf
import sqlite3
import sys 
import os
from os import path

# TO FIX FILE PATH IN PYINSTALLER EXEC:
db_full_path = path.abspath(path.join(path.dirname(__file__), 'db/SuperDeliveries.db'))
#

class graph_vertex:
    def __init__(self, name, x, y, id):
        self.name = name
        self.pos = (x, y)
        self.direction = ""
        self.visit_number = []
        self.id = id

    # heappush needs to know which location is smaller, in order to store them according to heap rules.
    # locations have no specified size, therefore implement less-than method which says, current loc is smaller to whichever compared loc:
    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return self.name

database = sqlite3.connect(db_full_path)
cur = database.cursor()
manhattan_graph = {}
for id, name, x, y, adj1, adj1_distance, adj2, adj2_distance, adj3, adj3_distance, adj4, adj4_distance in cur.execute("SELECT * FROM addresses"):
    globals()[id] = graph_vertex(name, int(x), int(y), id)
    manhattan_graph.update({globals()[id] : None})

for key in manhattan_graph:
    for adj1, adj1_distance, adj2, adj2_distance, adj3, adj3_distance, adj4, adj4_distance \
        in cur.execute("SELECT adj1, adj1_distance, adj2, adj2_distance, adj3, adj3_distance, adj4, adj4_distance FROM addresses WHERE id = '" + key.id + "'"):
        if adj4 != "":
            manhattan_graph.update({key: {(eval(adj1), adj1_distance), (eval(adj2), adj2_distance), (eval(adj3), adj3_distance), (eval(adj4), adj4_distance)}})
        elif adj3 != "":
            manhattan_graph.update({key: {(eval(adj1), adj1_distance), (eval(adj2), adj2_distance),
                                          (eval(adj3), adj3_distance)}})
        else:
            manhattan_graph.update({key : {(eval(adj1), adj1_distance), (eval(adj2), adj2_distance)}})

class TwoDimensionalMap:
    def __init__(self, graph):
        leftover = []
        min_x = inf
        max_x = 0
        min_y = inf
        max_y = 0
        for address in graph:
            if address.pos[0] < min_x:
                min_x = address.pos[0]
            elif address.pos[0] > max_x:
                max_x = address.pos[0]
            if address.pos[1] < min_y:
                min_y = address.pos[1]
            elif address.pos[1] > max_y:
                max_y = address.pos[1]
            leftover.append(address)
        rows = abs(min_y-max_y) + 1
        cols = abs(min_x-max_x) + 1
        self.matrix = []
        for i in range(rows):
            col = []
            for j in range(cols):
                for address in leftover:
                    if address.pos[0] == j + min_x and address.pos[1] == i + min_y:
                        col.append(address)
                        leftover.remove(address)
            self.matrix.append(col)

    def display_map(self):
        print("________________________________________________________________________________________________________"
              "___________________________________________________________________________")
        for row in self.matrix:
            for address in row:
                sys.stdout.write(" " + '{:^15s}'.format("") + " |")
            print("")
            for address in row:
                if address.name == '37th Street and 5th Avenue':
                    sys.stdout.write(" " + '{:^15s}'.format("\033[92m" + address.name[:15] + "\033[0m") + " |")
                else:
                    sys.stdout.write(" " + '{:^15s}'.format(address.name[:15]) + " |")
            print("")
            for address in row:
                if address.name == '37th Street and 5th Avenue':
                    sys.stdout.write(" " + '{:^24s}'.format("\033[92m" + address.name[15:] + "\033[0m") + " |")
                else:
                    sys.stdout.write(" " + '{:^15s}'.format(address.name[15:]) + " |")
            print("")
            for address in row:
                if address.visit_number != []:
                    if address.visit_number[0] == "*":
                        sys.stdout.write(" " + '{:^24s}'.format("\033[94m" + "*" + "\033[0m") + " |")
                    else:
                        if address.visit_number[0] == 10:
                            sys.stdout.write(" " + '{:^24s}'.format("\033[94m* (" + str(address.visit_number[0]) + ") *\033[0m") + " |")
                        elif address.visit_number[0] == 1:
                            if address.name == '37th Street and 5th Avenue':
                                sys.stdout.write(" " + '{:^29s}'.format("\033[93m(1)\033[94m" + str(address.visit_number[1]) + "\033[0m") + " |")
                            else:
                                sys.stdout.write(" " + '{:^24s}'.format("\033[93m* (" + str(address.visit_number[0]) + ") *\033[0m") + " |")
                        else:
                            sys.stdout.write(" " + '{:^24s}'.format("\033[94m* (" + str(address.visit_number[0]) +") *\033[0m") + " |")
                else:
                    sys.stdout.write(" " + '{:^15s}'.format("") + " |")
            print("")
            for address in row:
                sys.stdout.write("_" + '{:_^15s}'.format("") + "_|")
            print("")