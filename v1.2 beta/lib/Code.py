from kernel import *
from kernel import _7s
from interface import *
import ujson
from lcd import *

clock = Interface.Clock()
mes = Interface.Sensor.measure

update_setting_metadata = True   
update_apps_metadata = False 
DEBUG = False       

backlight = Pin(20, Pin.OUT)
backlight.low()


run_layer = 0


def _read_():
    with open("/lib/alarm.json", "r") as file:
        return load(file)
    
    
def _write_(f):
    with open("/lib/alarm.json", "w") as file:
        dump(f, file)

def songs():
    with open("/songs.json") as file:
        return load(file)
    
def dht_messure(settings):
    try:
        if settings['Time']['Farenhite Temp']:d ='F'
        else: d = "C"
        if settings["Time"]["Watchface"][0] == "Character":
            if settings["Time"]["Show Temp & Hum"]:
                temp, hum = mes()
                if settings["Time"]["Farenhite Temp"]:
                    temp = round((temp * 1.8 + 32), 1)
                    
                lcd_show(3, 0, f"              {temp}{d}{chr(0b11011111)}")
                lcd_show(4, 0, f"hum: {round(hum)}%")
                lcd_show(2, 0, "                    ")
        if settings["Time"]["Watchface"][0] == "7 Seg.":
            if settings["Time"]["Show Temp & Hum"]:
                temp, hum = mes()
                if settings["Time"]["Farenhite Temp"]:
                    temp = round((temp * 1.8 + 32), 1)
                lcd_show(4, 15, f"{temp}{d}{chr(0b11011111)}")
    except OSError as e:
        if DEBUG == False :
            clearDisplay()
            lcd_show(1, 0, "Error in")
            lcd_show(2, 0, "Loading Temp")
        else:
            raise e


def show_clock():
    global run_layer
    global mapping
    with open("settings.json") as file:
        settings = file.read()
    settings = ujson.loads(settings)
    with open("/lib/alarm.json") as file:
        alarms = load(file)
    mapping = 0
    i = 0
    bs = settings["Battery Saving"]["B.S. Mode"][0]
    if bs == "Ultra B.S.":
        backlight.high()
    if bs == "Off":
        backlight.low()
    dht_messure(settings)
    before_time = time()
    while not okk.value():
        clk = clock.read_time()
        
        if bs == "Auto B.S.":
            if int(clk[3]) >= 16:
                backlight.low()
            else:
                backlight.high()
        
        for alarm in alarms.values():
            hf = alarm[0]
            hm = alarm[1]
            snt = alarm[3][1]
            hm += snt
            while True :
                if hm >= 60:
                    hm -= 60
                    hf += 1
                    print("hm mined")
                else:
                    break
            while True :
                if hf >= 24:
                    hf -= 24
                    print("hf mined")
                else:
                    break
            if hf == int(clk[3]) and hm == int(clk[4]) and not int(clk[5]):
                mapping = list(alarms.keys())[list(alarms.values()).index(alarm)]
        if mapping:
            val = alarms[mapping]
            clearDisplay()
            displayString(1, 0, f"Alarm{mapping}")
            h_ = '0' + str(val[0]) if len(str(val[0])) != 2 else val[0]
            m_ = '0' + str(val[1]) if len(str(val[1])) != 2 else val[1]
            displayString(2, 15, f"{h_}:{m_}")
            sleep(0.5)
            song = songs()[alarms[mapping][4]]
            l = len(song)
            i = 0
            while True:
                buzzer.duty_u16(32768)
                if song[i] > 49:
                    buzzer.freq(song[i])
                else:
                    buzzer.duty_u16(0)
                i += 1
                if i == l:
                    i = 0
                if okk.value():
                    if val[2] == "Once":
                        r = _read_()
                        del r[mapping]
                        _write_(r)
                    elif val[2] == "Everyday":
                        pass
                    mapping = 0
                    break
                if esck.value():
                    r = _read_()
                    r[mapping][3][1] += r[mapping][3][0]
                    _write_(r)
                    mapping = 0
                    break
                sleep(0.25)
            buzzer.duty_u16(0)   
            break
        if settings["Time"]["Watchface"][0] == "Character":
            lcd_show(1, 0, f"            {clk[3]}:{clk[4]}:{clk[5]}")
            if settings["Time"]["Show Date"]:
                if settings["Time"]["Persian Calender"]:
                    converted_date = convert_date((int(clk[0]), int(clk[1]), int(clk[2])))
                    lcd_show(2, 0, f"{converted_date[0]}/{converted_date[1]}/{converted_date[2]}")
                else:
                    lcd_show(2, 0, f"{clk[0]}/{clk[1]}/{clk[2]}")
            
        if settings["Time"]["Watchface"][0] == "7 Seg.(with secs)":
            _7s(f"{clk[3]}:{clk[4]}:{clk[5]}")
        if settings["Time"]["Watchface"][0] == "7 Seg.":
            _7s(f"{clk[3]}:{clk[4]}")
            if settings["Time"]["Show Date"]:
                if settings["Time"]["Persian Calender"]:
                    converted_date = convert_date((int(clk[0]), int(clk[1]), int(clk[2])))
                    lcd_show(1, 15, f"{converted_date[0]}")
                    lcd_show(2, 15, f"{converted_date[1]}/{converted_date[2]}")
                else:
                    lcd_show(1, 15, f"{clk[0]}")
                    lcd_show(2, 15, f"{clk[1]}/{clk[2]}")
        if i == 90:
            i = 0
            dht_messure(settings)
        
        i += 1
        sleep(0.15)
    
    clearDisplay()
    run_layer = 1
    

def load_menu():
    global run_layer
    with open("apps.json") as file:
        read = file.read()
    l = list(ujson.loads(read).keys())
    i = 0
    print(l)
    value = menu_handler(lambda: start_menu(l, True))
    value = value.replace(" ", "_")
    clearDisplay()
    if not value == "":
        print(f"openning {value}")
        try:
            operator = f"""from {value} import main
main()"""
            print(operator)
            exec(operator)
        except ImportError as e:
            if not DEBUG:
                if str(e)[0] == "n":
                    displayString(1, 0, "This app has error")
                    displayString(3, 0, "Errno 1")
                    displayString(4, 0, "not_installed")

                    sleep(5)
                elif str(e)[1] == "c":
                    displayString(1, 0, "This app has error")
                    displayString(3, 0, "Errno 2")
                    displayString(4, 0, "no_main_function")
                    sleep(5)
                else:
                    layer = 0
            else:
                raise e
        except Exception as e:
            if not DEBUG:
                displayString(1, 0, "This app has error")
                displayString(3, 0, repr(e).split("(")[0])
                displayString(4, 0, str(e))
                sleep(5)
            else:
                raise e
    else:
        print("escaped")
        run_layer = 0
        return
    run_layer = 1
    


def OS():
    if update_setting_metadata or not exists("settings.json"):
        with open("settings.json", "w") as file:
            ujson.dump({"Time": {"Watchface": ["7 Seg.", "Character", "7 Seg.", "7 Seg.(with secs)"], "Set Time": "(SetTimeSetting)", "Farenhite Temp": False, "Show Date": True, "Persian Calender": True, "Show Temp & Hum": True}, "Battery Saving": {"B.S. Mode": ["Off", "Off", "Ultra B.S.", "Auto B.S."]}}, file)
    if update_apps_metadata or not exists("apps.json"):
        with open("apps.json", "w") as file:
            ujson.dump({"Settings":[2, 6], "test":[2, 6]}, file)
    with open("main.json") as file:
        ms = ujson.load(file)
    if not DEBUG:
        displayString(1, 1, "Digital Table Clock", 100, True)
        displayString(4, 6, f"Ver: {ms['OS_version']}", 100, True)
        sleep(4)
        clearDisplay()
        displayString(1, 0, "By: S.M.H. Dastgheybi", 100, True)
        displayString(3, 0, f"Update: {ms['OS_last_update']}", 100, True)
        displayString(4, 2, "Enter to continue")
        funtill(okk.value)
        clearDisplay()
        
    while True:
        if run_layer == 0:
            try:
                show_clock()
            except Exception as e:
                if not DEBUG:
                    displayString(1, 0, "Error in main page")
                    displayString(3, 0, repr(e).split("(")[0])
                    displayString(4, 0, str(e))
                    sleep(5)
                else:
                    raise e
        if run_layer == 1:
            load_menu()


if __name__ == "__main__":
    os = OS()

