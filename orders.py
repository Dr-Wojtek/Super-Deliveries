# Code by Alex Stråe, Sweden, AKA Dr-Wojtek @ GitHub
import sqlite3
import sys
import os
from os import path

# TO FIX FILE PATH IN PYINSTALLER EXEC:
db_full_path = path.abspath(path.join(path.dirname(__file__), 'db/SuperDeliveries.db'))
#

database = sqlite3.connect(db_full_path)
cur = database.cursor()
all_delivery_orders = []
for name, weight, value in cur.execute("SELECT name, weight, value FROM orders"):
    all_delivery_orders.append({'name': name, 'weight':int(weight), 'value': int(value),'address' :None, 'distance': None, 'path' : None})
