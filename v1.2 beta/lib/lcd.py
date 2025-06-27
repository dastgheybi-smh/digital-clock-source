import machine
import utime

rs = machine.Pin(0,machine.Pin.OUT)
machine.Pin(1, machine.Pin.OUT).low()
e = machine.Pin(2,machine.Pin.OUT)
d4 = machine.Pin(3,machine.Pin.OUT)
d5 = machine.Pin(4,machine.Pin.OUT)
d6 = machine.Pin(5,machine.Pin.OUT)
d7 = machine.Pin(6,machine.Pin.OUT)
refresh = 0
new_7s = False 
display = ["row spacer",
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]]
           ]

def pulseE():
    e.value(1)
    utime.sleep_us(40)
    e.value(0)
    utime.sleep_us(40)

def longDelay(t):
    utime.sleep_ms(t)

def shortDelay(t):
    utime.sleep_us(t)
    

def send2LCD4(BinNum):
    d4.value((BinNum & 0b00000001) >>0)
    d5.value((BinNum & 0b00000010) >>1)
    d6.value((BinNum & 0b00000100) >>2)
    d7.value((BinNum & 0b00001000) >>3)
    pulseE()
    
def send2LCD8(BinNum):
    d4.value((BinNum & 0b00010000) >>4)
    d5.value((BinNum & 0b00100000) >>5)
    d6.value((BinNum & 0b01000000) >>6)
    d7.value((BinNum & 0b10000000) >>7)
    pulseE()
    d4.value((BinNum & 0b00000001) >> 0)
    d5.value((BinNum & 0b00000010) >> 1)
    d6.value((BinNum & 0b00000100) >> 2)
    d7.value((BinNum & 0b00001000) >> 3)
    pulseE()
    
def setCursor(line, pos):
    b = 0
    if line==1:
        b=0
    elif line==3:
        b=20
    elif line==2:
        b=40
    elif line==4:
        b=60
    returnHome()
    for i in range(0, b+pos):
        moveCursorRight()
    
def returnHome():
    rs.value(0)
    send2LCD8(0b00000010)
    rs.value(1)
    longDelay(2)

def moveCursorRight():
    rs.value(0)
    send2LCD8(0b00010100)
    rs.value(1)
    
def setupLCD():
    rs.value(0)
    send2LCD4(0b0011)
    send2LCD4(0b0011)
    send2LCD4(0b0011)
    send2LCD4(0b0010)
    send2LCD8(0b00101000)
    send2LCD8(0b00001100)#lcd on, blink off, cursor off.
    send2LCD8(0b00000110)#increment cursor, no display shift
    send2LCD8(0b00000001)#clear screen
    longDelay(2)#clear screen needs a long delay
    rs.value(1)
 


def displayString(row, col, input_string, speed=100, s=False):
    setCursor(row,col)
    for x in str(input_string):
        send2LCD8(ord(x))
        if s:utime.sleep_ms(speed)
        
        
        
def lcd_show(row, col, input_string, speed=100, s=False, _7s=False ):
    global refresh
    global new_7s
    collector = []
    collector += input_string
    update = False
    r, c = row, col
    for char in collector:
        if display[r][c] != char:
            setCursor(r, c)
            display[r][c] = char
            send2LCD8(ord(char))
            if s:utime.sleep_ms(speed)
            update = True
        c += 1
        if c == 20:
            break
    if update == True:
        refresh += 1
        if _7s == False:
            print(f"Display Updated at [{row}, {col}] | code = ({refresh})") 
        else:
           new_7s = True 


def sevenSegmentRefresh(num):
    global new_7s
    if new_7s:
        new_7s = False 
        print(f"Display Updated by 7.S. Number [{num}] | code = ({refresh})")
    
        
def clearDisplay(t=0):
    global display
    global refresh
    display = ["row spacer",
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]],
           [[" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "], [" "]]
           ]
    refresh += 1
    print(f"Display Cleared | code = ({refresh})")
    rs.value(0)
    send2LCD8(0b00000001)#clear screen
    longDelay(2)
    rs.value(1)
    if t:
        longDelay(1000)

def customChar(code, char_array):
    location = code
    charmap = char_array
    location &= 0x7

    rs.low()
    send2LCD8(0x40 | (location << 3))
    shortDelay(5040)
    for i in range(8):
        rs.high()
        send2LCD8(charmap[i])
        shortDelay(50)

setupLCD()
