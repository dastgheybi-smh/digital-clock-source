import kernel
import ujson
import utime
import lcd

class ItemError:
    class ItemLengthError(Exception):
        pass
    class EmptyListError(Exception):
        pass


upk = kernel.Pin(10, kernel.Pin.IN, kernel.Pin.PULL_DOWN)
downk = kernel.Pin(11, kernel.Pin.IN, kernel.Pin.PULL_DOWN)
okk = kernel.Pin(15, kernel.Pin.IN, kernel.Pin.PULL_DOWN)
esck = kernel.esck

def menu_item_shorter(items_, num_lower=15):
    items = items_
    i = 0
    for item in items:
        if len(str(item)) > 18:
            items[i] = items[i][:num_lower]+"..."
        i += 1
    return items
def menu_handler(menu, ekpr=""):
    try:
        value = menu()
        return value
    except AssertionError:
        return ekpr
def start_menu(items, arrow_selection=False):
    menu = Interface.Software.Menu()
    return menu.start(items, arrow_selection)


class Interface:
    class Clock(kernel.ds3231):
        def __init__(self):
            super().__init__(0, 17, 16)
    class Sensor:
        def measure():
            dht22 = kernel.DHT22(kernel.Pin(12))
            dht22.measure()
            return dht22.temperature(), dht22.humidity()
    class Software:
        class BaseInput:
            
            def __init__(self,
                         context: list,
                         up,
                         down,
                         ok,
                         esc,
                         esc_output=None):
                self.context = context
                self.up = up
                self.down = down
                self.ok = ok
                self.esc = esc
                self.esc_output = esc_output

            def start(self):
                data = self.context
                send = []
                submitted_inputs = 0
                while submitted_inputs < len(data):
                    input_value = self.show_input(data[submitted_inputs])
                    if input_value is None:
                        submitted_inputs -= 1
                        try:
                            send.pop()
                        except IndexError:
                            return
                    else:
                        send.append(input_value)
                        submitted_inputs += 1
                    utime.sleep(.2)
                return send
                    
            
            def show_input(self, inp):
                x = 1
                lcd.clearDisplay()
                for msg in inp["msg"]:
                    lcd.displayString(x, 0, str(msg)[:20])
                    x += 1
                if inp.get("type") is None or inp.get("type") == "raw_input":
                    if inp.get("placeholder") is not None:
                        lcd.displayString(4, 1, str(inp.get("placeholder"))[1:])
                    if inp.get("max_length") is not None:
                        max_length = inp.get("max_length")
                    else:
                        max_length = 20
                    input_items = inp["input_items"]
                    lcd.displayString(4, 0, str(input_items[0]))
                    i = 0
                    index = 0
                    submitted_input = ""
                    while True:
                        if self.down.value():
                            i += 1
                            if i == len(input_items):
                                i = 0
                            lcd.displayString(4, index, input_items[i])
                        if self.up.value():
                            if i == 0:
                                i = len(input_items) - 1
                            else:
                                i -= 1
                            lcd.displayString(4, index, input_items[i])
                        if self.ok.value():
                            index += 1
                            submitted_input += str(input_items[i])
                            lcd.displayString(4, index, input_items[0])
                            if index == max_length:
                                return submitted_input
                        if self.esc.value():
                            index -= 1
                            if index <= 0:
                                return None
                            else:
                                if  inp.get("placeholder") is not None:
                                    lcd.displayString(4, index+1, inp.get("placeholder")[index])
                                else:
                                    lcd.displayString(4, index+1, " ")
                        utime.sleep(0.2)
                    
                elif inp.get("type") == "number_choice":
                    min_num = int(inp["min_number"])
                    max_num = int(inp["max_number"])
                    
                    output = min_num
                    
                    if inp.get("equal_len"):
                        target_len = len(str(max_num))
                        base_len = len(str(output))
                        zeros = ["0" for _ in range(target_len - base_len)]
                        zeros_ = ""
                        for zero in zeros:
                            zeros_ += zero
                    else:
                        zeros_ = ""

                    lcd.displayString(4, 0, zeros_+str(min_num))

                    while not self.esc.value():
                        if self.up.value():
                            output += 1
                            if output == max_num + 1:
                                output = min_num
                            lcd.clearDisplay()
                            x = 1
                            for msg in inp["msg"]:
                                lcd.displayString(x, 0, str(msg)[:20])
                                x += 1
                            if inp.get("equal_len"):
                                target_len = len(str(max_num))
                                base_len = len(str(output))
                                zeros = ["0" for _ in range(target_len - base_len)]
                                zeros_ = ""
                                for zero in zeros:
                                    zeros_ += zero
                            else:
                                zeros_ = ""
                            lcd.displayString(4, 0, f"{zeros_}{output}")
                        elif self.down.value():
                            output -= 1
                            if output == min_num -1:
                                output = max_num
                            lcd.clearDisplay()
                            x = 1
                            for msg in inp["msg"]:
                                lcd.displayString(x, 0, str(msg)[:20])
                                x += 1
                            if inp.get("equal_len"):
                                target_len = len(str(max_num))
                                base_len = len(str(output))
                                zeros = ["0" for _ in range(target_len - base_len)]
                                zeros_ = ""
                                for zero in zeros:
                                    zeros_ += zero
                            else:
                                zeros_ = ""
                            lcd.displayString(4, 0, f"{output}")
                        elif self.ok.value():
                            return output
                        utime.sleep(.2)
                    return None
                elif inp.get("type") == "list_choice":
                    input_items = inp["input_items"]

                    lcd.displayString(4, 0, str(input_items[0]))
                    output = 0
                    min_num = 0
                    max_num = len(input_items) - 1

                    while not self.esc.value():
                        if self.up.value():
                            output += 1
                            if output == max_num + 1:
                                output = min_num
                            lcd.clearDisplay()
                            x = 1
                            for msg in inp["msg"]:
                                lcd.displayString(x, 0, str(msg)[:20])
                                x += 1
                            lcd.displayString(4, 0, f"{input_items[output]}")
                        elif self.down.value():
                            output -= 1
                            if output == min_num -1:
                                output = max_num
                            lcd.clearDisplay()
                            x = 1
                            for msg in inp["msg"]:
                                lcd.displayString(x, 0, str(msg)[:20])
                                x += 1
                            lcd.displayString(4, 0, f"{input_items[output]}")
                        elif self.ok.value():
                            return input_items[output]
                        utime.sleep(.2)
                    return None
        class NumberInput(BaseInput):
            def __init__(self,
                         context: list,
                         up=upk,
                         down=downk,
                         ok=okk,
                         esc=esck):
                context_number = []
                for item in context:
                    data = item
                    if data.get("type") is None or data.get("type") == "raw_input":
                        if data.get("input_items") is None:
                            data["input_items"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                            context_number.append(data)
                        else:
                            context_number.append(data)
                    else:
                        context_number.append(data)
                super().__init__(context_number, up, down, ok, esc)
        class Menu:
            def start(self, items:list | tuple, arrow_selection=False):
                print("deds")
                lcd.clearDisplay()
                self.items = items
                self.ITEMS = items
                self.arrow = arrow_selection
                if len(items) == 0:
                    raise ItemError.EmptyListError("No Item In list")
                i = 0
                for item in items:
                    self.items[i] = str(item)
                    i += 1
                del i
                for item in items:
                        if len(item) > 19:
                            raise ItemError.ItemLengthError("to much long item")
                self.length = len(items)
                self.selection = 0
                if self.length > 4:
                    self.indention = 0
                    self.max = self.length - 4
                    self.display_list = self.items[self.indention:self.indention+4]
                self.select()
                utime.sleep(0.2)
                if self.length <= 4:
                    while True:
                        assert not esck.value()
                        if okk.value():
                            return self.ITEMS[self.selection]
                        if downk.value():
                            if self.selection + 1 == self.length:
                                self.selection = 0
                            else:
                                self.selection += 1
                            self.select()
                        if upk.value():
                            if self.selection - 1 == -1:
                                self.selection = self.length-1
                            else:
                                self.selection -= 1
                            self.select()
                        utime.sleep(0.15)
                else:
                    while True:
                        assert not esck.value()
                        if okk.value():
                            return self.ITEMS[self.selection]
                        if downk.value():
                            if self.selection + 1 == self.length:
                                self.selection = 0
                                self.indention = 0
                            elif self.selection + 1 > self.indention + 3:
                                self.indention += 1
                                self.selection += 1
                            else:
                                self.selection += 1
                            self.select()
                        if upk.value():
                            if self.selection - 1 == -1:
                                self.selection = self.length-1
                                self.indention = int(self.max)
                            elif self.selection - 1 < self.indention:
                                self.indention -= 1
                                self.selection -= 1
                            else:
                                self.selection -= 1
                            self.select()
                        utime.sleep(0.15)
                            
            def select(self):
                item = self.selection
                self.items = list(self.ITEMS)
                spaces = ""
                for x in range(18-len(self.items[item])):
                    spaces += " "
                if self.arrow:
                    spaces += " "
                    self.items[item] += f"{spaces}>"
                else:
                    self.items[item] = f"[{self.ITEMS[item]}{spaces}]"  
                if len(self.items) <= 4:
                    self.display(self.items)
                else:
                    self.display_list = self.items[self.indention:self.indention+4]
                    self.display(self.display_list)
            def display(self, _list):
                lcd.clearDisplay()
                l = 1
                for item in _list:
                    lcd.displayString(l, 0, item)
                    l += 1    

        class Settings:
            class FunctionBasedSetting:
                def run():
                    raise NotImplementedError
            def change_setting(new):
                with open("setting.json", "w") as file:
                    ujson.dump(new)
            
            def settings():
                with open("setting.json") as file:
                    return ujson.loads(file.read())
            

class SetTimeSetting(Interface.Software.Settings.FunctionBasedSetting):
    def run():
        value = Interface.Software.NumberInput(
           [
               {
                   "msg": ["Set year", "(in gregorian)"],
                   "type": "number_choice",
                   "min_number": 2000,
                   "max_number": 2099
               },
               {
                   "msg": ["Set month"],
                   "type": "number_choice",
                   "equal_len": True,
                   "min_number": 1,
                   "max_number": 12,
               },
               {
                   "msg": ["Set day"],
                   "type": "number_choice",
                   "equal_len": True,
                   "min_number": 1,
                   "max_number": 31,
               },
               {
                   "msg": ["Set hour"],
                   "type": "number_choice",
                   "equal_len": True,
                   "max_number": 23,
                   "min_number": 0,
               },
               {
                   "msg": ["Set minute"],
                   "type": "number_choice",
                   "equal_len": True,
                   "max_number": 59,
                   "min_number": 0,
               },
               {
                   "msg": ["Set second"],
                   "type": "number_choice",
                   "equal_len": True,
                   "max_number": 59,
                   "min_number": 0,
               },
               {
                   "msg": ["Set Weekday"],
                   "type": "list_choice",
                   "input_items": ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
               }
           ]
        )

        value = value.start()
        if value is not None:
            clock = Interface.Clock()
            if len(str(value[1])) == 1:
                value[1] = "0" + str(value[1])
            if len(str(value[2])) == 1:
                value[2] = "0" + str(value[2])
            if len(str(value[3])) == 1:
                value[3] = "0" + str(value[3])
            if len(str(value[4])) == 1:
                value[4] = "0" + str(value[4])
            if len(str(value[5])) == 1:
                value[5] = "0" + str(value[5])
            clock.set_time(f"{value[3]}:{value[4]}:{value[5]},{value[6]},{value[0]}/{value[1]}/{value[2]}")
