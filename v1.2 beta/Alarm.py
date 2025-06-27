from lcd import clearDisplay, displayString
from interface import upk, downk, esck, okk, kernel, menu_handler, start_menu
from interface import Interface
from utime import sleep
from ujson import load, dump
from kernel import buzzer

Clock = Interface.Clock()

clearDisplay()
displayString(2, 7, "Alarm")
kernel.sleep(1)

update_metadata = True

state = 1

global_ = ""
_ = hex(352323323)


def read():
    with open("/lib/alarm.json", "r") as file:
        return load(file)
    
def songs():
    with open("/songs.json") as file:
        return load(file)
    
    
def write(f):
    with open("/lib/alarm.json", "w") as file:
        dump(f, file)
    
    
def case(val):
    if val == _ or val == global_:
        return True
    else:
        return False 
    
    
def match(val):
    global global_
    global_ = val


def modify(index, new=False ):
    clearDisplay()
    layer = 1
    while layer:
        match(layer)
        if case(1):
            clearDisplay()
            displayString(1, 0, f"name: Alarm{index}")
            displayString(4, 0, "<Esc          Enter>")
            sleep(0.1)
            while True:
                if esck.value():
                    layer -= 1
                    if new:
                        r = read()
                        del r[index]
                        write(r)
                    break  
                elif okk.value():
                    layer += 1
                    break
                sleep(0.1)
        if case(2):
            clearDisplay()
            hour = read()[index][0]
            displayString(1, 0, f"hour: {hour}")
            displayString(4, 0, "<Esc          Enter>")
            x_hour = hour
            sleep(0.1)
            while True:
                if esck.value():
                    layer -= 1
                    break  
                elif okk.value():
                    r = read()
                    r[index][0] = x_hour
                    write(r)
                    layer += 1
                    break
                if upk.value():
                    x_hour += 1
                    if x_hour == 24:
                        x_hour = 0
                    clearDisplay()
                    displayString(1, 0, f"hour: {x_hour}")
                    displayString(4, 0, "<Esc          Enter>")
                elif downk.value():
                    x_hour -= 1
                    if x_hour == -1:
                        x_hour = 23
                    clearDisplay()
                    displayString(1, 0, f"hour: {x_hour}")
                    displayString(4, 0, "<Esc          Enter>")
                sleep(0.1)
        if case(3):
            clearDisplay()
            x_min = read()[index][1]
            displayString(1, 0, f"minute: {x_min}")
            displayString(4, 0, "<Esc          Enter>")
            sleep(0.1)
            m = x_min 
            while True:
                if esck.value():
                    layer -= 1
                    break  
                elif okk.value():
                    r = read()
                    r[index][1] = m
                    write(r)
                    layer += 1
                    break
                
                if upk.value():
                    m += 1
                    if m == 60:
                        m = 0
                    clearDisplay()
                    displayString(1, 0, f"minute: {m}")
                    displayString(4, 0, "<Esc          Enter>")
                elif downk.value():
                    m -= 1
                    if m == -1:
                        m = 59
                    clearDisplay()
                    displayString(1, 0, f"minute: {m}")
                    displayString(4, 0, "<Esc          Enter>")
                sleep(0.1)
        if case(4):
            clearDisplay()
            x_type = read()[index][2]
            displayString(1, 0, f"type: {x_type}")
            displayString(4, 0, "<Esc          Enter>")
            t_list = ["Once", "Everyday"]
            sleep(0.1)
            t = t_list.index(x_type)
            while True:
                if esck.value():
                    layer -= 1
                    break  
                elif okk.value():
                    r = read()
                    r[index][2] = t_list[t]
                    write(r)
                    layer += 1
                    break
                
                if upk.value():
                    t += 1
                    if t == 2:
                        t = 0
                    clearDisplay()
                    displayString(1, 0, f"type: {t_list[t]}")
                    displayString(4, 0, "<Esc          Enter>")
                elif downk.value():
                    t -= 1
                    if t == -1:
                        t = 1
                    clearDisplay()
                    displayString(1, 0, f"minute: {t_list[t]}")
                    displayString(4, 0, "<Esc          Enter>")
                sleep(0.1)
        if case(5):
            clearDisplay()
            x_song = read()[index][4]
            t_list = ["Default", "Wake Up", "Happy Birthday", "Zing"]
            displayString(1, 0, f"song: {x_song}")
            displayString(4, 0, "<Esc   Play   Enter>")
            sleep(0.1)
            t = x_song
            while True:
                if esck.value():
                    layer -= 1
                    break  
                elif okk.value():
                    enter = 1
                    for i in range(100):
                        if not okk.value():
                            enter = 0
                            break
                        sleep(0.01)
                    if enter:
                        r = read()
                        r[index][4] = t
                        write(r)
                        layer += 1
                        break
                    else:
                        for i in songs()[t]:
                            buzzer.duty_u16(32768)
                            if i > 49:
                                buzzer.freq(i)
                            else:
                                buzzer.duty_u16(0)
                            sleep(0.25)
                        buzzer.duty_u16(0)
                
                if upk.value():
                    t += 1
                    if t == 4:
                        t = 0
                    clearDisplay()
                    displayString(1, 0, f"song: {t_list[t]}")
                    displayString(4, 0, "<Esc   Play   Enter>")
                elif downk.value():
                    t -= 1
                    if t == -1:
                        t = 1
                    clearDisplay()
                    displayString(1, 0, f"song: {t_list[t]}")
                    displayString(4, 0, "<Esc   Play   Enter>")
                sleep(0.1)
        if case(6):
            match(state)
            return
        sleep(0.15)
    match(state)
    
    


def main():
    state = 1
    while True :
        match(state)
        if case(1):
            value = menu_handler(lambda: start_menu(["Alarms", "Add new alarm", "Delete"], True))
            match( value)
            if case( ""):
                break
            if case( "Alarms"):
                state = 2
                continue 
            if case( "Add new alarm"):
                state = 3
                continue
            if case("Delete"):
                state = 4
                continue 
        elif case( 2):
            r = list(read().keys())
            if len(r) == 0:
                clearDisplay()
                displayString(2, 3, "No Items Found")
                while not esck.value():pass
                state = 1
            else:
                value = menu_handler(lambda: start_menu([f"Alarm{s}" for s in sorted([int(x) for x in r])], True))
                if value == "":
                    state = 1
                    continue
                else:
                    data = read()[value.replace("Alarm", "")]
                    if len(str(data[1])) == 1:
                        x = '0' + str(data[1])
                    else:
                        x = data[1]
                    clearDisplay()
                    displayString(1, 0, f"{value}")
                    displayString(3, 0, f"{data[0]}:{x}")
                    match(data[2])
                    if case("Once"):
                        displayString(3, 16, "Once")
                    if case("Everyday"):
                        displayString(3, 12, "Everyday")
                    if case("Custom"):
                        displayString(3, 14, "Custom")
                    sleep(0.5)
                    while True:
                        if esck.value():
                            break
                        elif okk.value():
                            modify(value.replace("Alarm", ""))
                            break
                        sleep(0.015)
        elif case(3):
            time = Clock.read_time()
            r = read()
            alarm_number = 1
            alarms = [int(alarm) for alarm in list(r.keys())]
            while True:
                if alarm_number in alarms:
                    print(alarm_number)
                    alarm_number += 1
                    continue
                else:
                    break 
            r.update({str(alarm_number): [int(time[3]), int(time[4]), "Once", [5, 0], 0]})
            write(r)
            modify(str(alarm_number), True)
            state = 1
        if case(4):
            value = menu_handler(lambda: start_menu(["Delete All", "Delete One"], True))
            match(value)
            if case("Delete All"):
                clearDisplay()
                displayString(1, 0, "Are you sure do you")
                displayString(2, 0, "want to delete all")
                displayString(3, 0, "your alarms?")
                displayString(4, 0, "<Esc             Up>")
                sleep(0.5)
                while True:
                    if esck.value():
                        state = 1
                        break 
                    elif upk.value():
                        r = {}
                        write(r)
                        break
                    sleep(0.15)
                continue 
            elif case("Delete One"):
                r = list(read().keys())
                if len(r) == 0:
                    clearDisplay()
                    displayString(2, 3, "No Items Found")
                    while not esck.value():pass
                    state = 1
                else:
                    value = menu_handler(lambda: start_menu([f"Alarm{s}" for s in sorted([int(x) for x in r])], True))
                    if value:
                        clearDisplay()
                        displayString(1, 0, "Are you sure do you")
                        displayString(2, 0, "want to delete")
                        displayString(3, 0, f"{value}")
                        displayString(4, 0, "<Esc             Up>")
                        while True:
                            if esck.value():
                                state = 1
                                break 
                            elif upk.value():
                                r = read()
                                del r[value.replace("Alarm", "")]
                                write(r)
                                break
                            sleep(0.15)
                        continue
                    else:
                        state = 1
            elif case(_):
                state = 1
                    

if __name__ == "__main__":
    if update_metadata:
        write({})
    main()
