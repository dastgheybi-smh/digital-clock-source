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
            dht22 = kernel.DHT22(kernel.Pin(13))
            dht22.measure()
            return dht22.temperature(), dht22.humidity()
    class Software:
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
            def change_setting(new):
                with open("setting.json", "w") as file:
                    ujson.dump(new)
            
            def settings():
                with open("setting.json") as file:
                    return ujson.loads(file.read())

