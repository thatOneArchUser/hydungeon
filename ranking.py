# add this to dungeon cmd (when returning dungeon results)

import math

if mode.lower() == "normal: #100 is maximum
    s = math.floor(100 - int(random.randint(floor / 4, floor * 4)) * 3)
    if s < 17: return rank = "D"
    elif s >= 17 and s < 34: return rank = "C"
    elif s >= 34 and s < 51: return rank = "B"
    elif s >= 51 and s < 68: return rank = "A"
    elif s >= 69 and s < 85: return rank = "S"
    elif s >= 85: return rank = "S+"
    
elif mode.lower() == "master": #300 is maximum
    s = math.floor(300 - int(random.randint(floor / 14, floor * 14)) * 3)
    if s < 50: return rank = "D"
    elif s >= 50 and s < 100: return rank = "C"
    elif s >= 100 and s < 150: return rank = "B"
    elif s >= 150 and s < 200: return rank = "A"
    elif s >= 200 and s < 250: return rank = "S"
    elif s >= 250: return rank = "S+"
    
# remember to send the results too
