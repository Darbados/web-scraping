import math

def oddsFormat(value):
    if value not in ['',' ',None]:
        c_value = float(value)
        if c_value < 0:
            c_value = ((abs(c_value)+100) / abs(c_value))
            c_value = (c_value*100)/100
        else:
            c_value = (c_value+100)/100
            c_value = (c_value*100)/100
        return round(c_value,2)
    else:
        c_value = 0.00000
        return round(c_value,2)
