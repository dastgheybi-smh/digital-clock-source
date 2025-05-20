from machine import *
from dht import DHT22, DHT11
import binascii
from uos import listdir
import lcd
from random import randint
from utime import *
from ujson import load, dump

                                          
def setup():
    clock = ds3231(0, 17, 16)
    return clock



buzzer = PWM(Pin(12))


class Codec7s:
    def __init__(self,
                 n0=[" ", " ", " ", " "],
                 n1=[" ", " ", " ", " "],
                 n2=[" ", " ", " ", " "],
                 n3=[" ", " ", " ", " "],
                 n4=[" ", " ", " ", " "],
                 n5=[" ", " ", " ", " "],
                 n6=[" ", " ", " ", " "],
                 n7=[" ", " ", " ", " "],
                 n8=[" ", " ", " ", " "],
                 n9=[" ", " ", " ", " "],
                 space=[" ", " ", " ", " "],
                 dd=[" ", " ", " ", " "]):
        self.items = [n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, space, dd]

DefaultCodec7s = Codec7s(["\2\3\0", "\2 \0", "\2 \0", "\2\1\0"],
                         ["  \0", "  \0", "  \0", "  \0"],
                         [" \3\0", " \1\0", "\2  ", "\2\1 "],
                         [" \3\0", " \1\0", "  \0", " \1\0"],
                         ["\2 \0", "\2\1\0", "  \0", "  \0"],
                         ["\2\3 ", "\2\1 ", "  \0", " \1\0"],
                         ["\2\3 ", "\2\1 ", "\2 \0", "\2\1\0"],
                         [" \3\0", "  \0", "  \0", "  \0"],
                         ["\2\3\0", "\2\1\0", "\2 \0", "\2\1\0"],
                         ["\2\3\0", "\2\1\0", "  \0", " \1\0"],
                         [" ", " ", " ", " "],
                         [" ", str(chr(0b10100101)), str(chr(0b00101110)), " "])

DefaultCodec7sv2 = Codec7s(["\2\3\0", "\2 \0", "\2 \0", "\2\1\0"],
                           ["  \0", "  \0", "  \0", "  \0"],
                           ["\7\3\0", " \1\0", "\2\3 ", "\2\1\5"],
                           ["\7\3\0", " \1\0", " \3\0", "\6\1\0"],
                           ["\2 \0", "\2\1\0", "  \0", "  \0"],
                           ["\2\3\4", "\2\1 ", " \3\0", "\6\1\0"],
                           ["\2\3\4", "\2\1 ", "\2 \0", "\2\1\0"],
                           ["\7\3\0", "  \0", "  \0", "  \0"],
                           ["\2\3\0", "\2\1\0", "\2\3\0", "\2\1\0"],
                           ["\2\3\0", "\2\1\0", " \3\0", "\6\1\0"],
                           dd=[" ", str(chr(0b10100101)), str(chr(0b00101110)), " "])
lcd.customChar(0, [0x1C,  0x1C,  0x1C,  0x1C,  0x1C,  0x1C,  0x1C,  0x1C])
lcd.customChar(1, [0x00,  0x00,  0x00,  0x00,  0x00,  0x00,  0x1F,  0x1F])
lcd.customChar(2, [0x07,  0x07,  0x07,  0x07,  0x07,  0x07,  0x07,  0x07])
lcd.customChar(3, [0x1F,  0x1F,  0x00,  0x00,  0x00,  0x00,  0x00,  0x00])
lcd.customChar(4, [0x1C,  0x1C,  0x00,  0x00,  0x00,  0x00,  0x00,  0x00])
lcd.customChar(5, [0x00,  0x00,  0x00,  0x00,  0x00,  0x00,  0x1C,  0x1C])
lcd.customChar(6, [0x00,  0x00,  0x00,  0x00,  0x00,  0x00,  0x07,  0x07])
lcd.customChar(7, [0x07,  0x07,  0x00,  0x00,  0x00,  0x00,  0x00,  0x00])


def _7s(number:int | str, x: int=0, codec: Codec7s=DefaultCodec7sv2):
    ln = str(number)
    got = 0
    prev_got = 0
    for i in range(len(ln)):
        prev_got = got
        num = ln[i]
        if type(num) == str:
            try:
                num = int(num)
            except ValueError:
                if num == " ":
                    charl = codec.items[10]
                    got += 1
                elif num == ":":
                    charl = codec.items[11]
                    got += 1
                else:
                    break
        if type(num) == int:
            n = abs(num)
            charl = codec.items[n]
            got += 3
        lcd.displayString(1, prev_got+x, f"{charl[0]}")
        lcd.displayString(2, prev_got+x, f"{charl[1]}")
        lcd.displayString(3, prev_got+x, f"{charl[2]}")
        lcd.displayString(4, prev_got+x, f"{charl[3]}")


def funtill(function, val:list=[True], while_value = True, freq = 50):
    while while_value:
        if function() in val:
            return
        sleep(1/freq)


class ESC():
    def __init__(self, *args):
        self.esc = Pin(14, Pin.IN, Pin.PULL_DOWN)
        self.soft_val = 0
    def value(self):
            if self.soft_val:
                self.soft_val -= 1
                return 1
            else:
                return self.esc.value()
    def soft_value(self, escs=1):
        self.soft_val += escs
    
    def no_soft_value(self):
        self.soft_val = 0


esck = ESC()





class ds3231(object):
    NowTime = b'\x00\x45\x13\x02\x24\x05\x21'
    w  = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    address = 0x68
    start_reg = 0x00
    alarm1_reg = 0x07
    control_reg = 0x0e
    status_reg = 0x0f
    
    def __init__(self,i2c_port,i2c_scl,i2c_sda):
        self.bus = I2C(i2c_port,scl=Pin(i2c_scl),sda=Pin(i2c_sda))

    def set_time(self,new_time):
        hour = new_time[0] + new_time[1]
        minute = new_time[3] + new_time[4]
        second = new_time[6] + new_time[7]
        week = "0" + str(self.w.index(new_time.split(",",2)[1])+1)
        year = new_time.split(",",2)[2][2] + new_time.split(",",2)[2][3]
        month = new_time.split(",",2)[2][5] + new_time.split(",",2)[2][6]
        day = new_time.split(",",2)[2][8] + new_time.split(",",2)[2][9]
        now_time = binascii.unhexlify((second + " " + minute + " " + hour + " " + week + " " + day + " " + month + " " + year).replace(' ',''))
        self.bus.writeto_mem(int(self.address),int(self.start_reg),now_time)
    
    def read_time(self):
        t = self.bus.readfrom_mem(int(self.address),int(self.start_reg),7)
        return ("20%x/%02x/%02x/%02x/%02x/%02x/%s" %(t[6],t[5],t[4],t[2],t[1],t[0],self.w[t[3]-1])).split("/")


def exists(filename):
    if filename in listdir():
        return True
    else:
        return False
    
def convert_date(date):
    [gy, gm, gd] = date
    gy, gm, gd = int(gy), int(gm), int(gd)
    gl = False
    if gy % 4 != 0:
        gl = True 
        gml = [31,28,31,30,31,30,31,31,30,31,30,31]
    else:
        gml = [31,29,31,30,31,30,31,31,30,31,30,31]
    
    y = gy - 621
    wgd = gd
    for day in range(gm-1):
        wgd += gml[day]
    wd = wgd - 78
    if wd < 0:
        y -= 1
        wd = 365 + wd
    if y % 33 in (1, 5, 9, 13, 17, 22, 26, 30):
        if gl:
            wd += 1
        ml = [31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336, 366]
    else:
        ml = [31, 62, 93, 124, 155, 186, 216, 246, 276, 306, 336, 365]
    m = 1
    for month in ml:
        if wd < month:
            m += ml.index(month)
            d = wd - ml[ml.index(month)-1]-1
            break
    return y, m, d
  