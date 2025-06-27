from interface import Interface, menu_handler, start_menu, esck, ItemError
from lcd import displayString, clearDisplay
from ujson import load, dump
from time import sleep

mes = Interface.Sensor.measure
EmptyListError = ItemError.EmptyListError

clearDisplay()

def read():
    with open("log.json") as file:
        return load(file)


def write(value):
    with open("log.json", "w") as file:
        dump(value, file)

def main():
    layer = 1
    while layer:
        if layer == 1:
            item = menu_handler(lambda: start_menu(["Logs", "New Log", "Delete"]), None)
            if item == "Logs":
                layer = 2
                continue
            if item == "New Log":
                layer = 3
                continue
            if item == "Delete":
                layer = 4
                continue
            else:
                layer = 0
                continue 
        if layer == 2:
            try:
                item = menu_handler(lambda: start_menu(list(read().keys())), None)
            except EmptyListError:
                clearDisplay() 
                displayString(2, 3, "No Items Found")
                sleep(2)
                layer = 1
                continue
            if item == None:
                layer = 1
                continue
            else:
                displayString(1, 0, "temp: "+str(read()[item][0])+"C")
                displayString(2, 0, "hum: "+str(read()[item][1])+"%")
                displayString(4, 0, "<ESC")
                while True:
                    if esck.value():
                        break
                continue
        if layer == 3:
            print(2)
            pass
            t, h = mes()
            r = read()
            lr = len(list(r.keys()))
            key = lr + 1
            r.update({f"Log{key}": [t, h]})
            write(r)
            displayString(1, 0, "New log has saved:")
            displayString(2, 0, f"Log{key}")
            displayString(3, 0, str(t)+"C")
            displayString(4, 0, str(h)+"%")
            sleep(2)
            layer = 1
            
    
if __name__ == "__main__":
    main()
