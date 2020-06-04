import os
import time

time.sleep(5)

with open('delete_items.txt') as file:
    a = file.read()
    os.remove(a)

with open('1.txt', 'w') as file:
    file.write('wegf')
