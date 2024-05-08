import os

for root,_,file in os.walk('uploads'):
    for f in file:
     
        if f.endswith('.png'):
            print(f)