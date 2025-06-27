from interface import *
from lcd import *
from ujson import dump, load
from utime import sleep


def upload_tab():
    global is_data_bool, place
    items = list(place.keys())
    modified_items = []
    for item in items:
        if isinstance(place[item], bool):
            spaces = " " * (16 - len(item))
            modified_item = item + spaces + ("Y" if place[item] else "N")
            modified_items.append(modified_item)
        elif isinstance(place[item], list):
            modified_items.append(item)
        elif type(place[item]) == str:
            if place[item].startswith("(") and place[item].endswith(")"):
                modified_items.append(item)
            
            
    value = menu_handler(lambda: start_menu(modified_items))
    return value

def write():
    global settings
    with open("settings.json", "w") as file:
        dump(settings, file)

with open("settings.json", "r") as file:
    settings = load(file)
layer = 1
place = settings

def main():
    global place, layer
    layer = 1
    displayString(1, 0, "ss")
    print("ss")
    clearDisplay()
    while layer:
        if layer == 1:
            value = menu_handler(lambda: start_menu(list(place.keys()), True))
            if value == "":
                layer -= 1
                continue 
            else:
                layer += 1
                place = place[value]
                clearDisplay()
                displayString(1, 0, "Loading...")
                continue 
        if layer == 2:
            value = upload_tab()
            if value == "":
                layer -= 1
                place = settings
                continue
            elif isinstance(place.get(value), str):
                if place[value].startswith("(") and place[value].endswith(")"):
                    code = place[value][1:-1]
                    print(code)
                    exec(f"{code}.run()")
                continue 
            else:
                value = str(value)
                is_data_bool = [False if item == value else True for item in place]
                print(is_data_bool)
                is_data_bool = False if False in is_data_bool else True 
                if not is_data_bool:
                    placer = place[value]
                    layer += 1
                    clearDisplay()
                    displayString(1, 0, "Loading...")
                else:
                    value = value[:-1]
                    value = value.strip()
                    place[value] = not place[value]
                    write()
                continue
        if layer == 3:
            items = placer[1:]
            value = menu_handler(lambda: start_menu(items, True))
            if value:
                placer[0] = value
            layer -= 1
            write()
            
        sleep(0.2)

    clearDisplay()


if __name__ == "__main__":
    main()
