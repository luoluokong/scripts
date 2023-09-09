import os
import pyperclip as pc

path = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
assert os.path.isfile(path)

with open(path,'r') as config:
    lines = config.readlines()
    
target_text = 'Pie64.status.adb_port'
for num,line in enumerate(lines,1):
    if target_text in line:
        port = f'{line[-7:-2]}'
        # print(f'{num}行:{line}')
        pc.copy(f'127.0.0.1:{port}')