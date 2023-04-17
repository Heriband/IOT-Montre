import machine
import ssd1306
from pyb import ADC, Pin, Timer
import framebuf
from machine import Pin
import time 
from time import time, sleep_ms
import Game as game

#buttons
sw1 =  Pin ('SW1', Pin.IN) #validate button
sw1.init (Pin.IN, Pin.PULL_UP, af = -1)

sw2 = Pin ('SW2', Pin.IN)
sw2.init (Pin.IN, Pin.PULL_UP, af = -1)

sw3 = Pin ('SW3', Pin.IN)
sw3.init (Pin.IN, Pin.PULL_UP, af = -1)

#Sensor
# machine.Pin('A0', machine.Pin.OUT).low()
# machine.Pin('C3', machine.Pin.OUT).high()
# Pin(Pin.cpu.C2, mode=Pin.IN)


i2c = machine.SoftI2C(scl=machine.Pin('A15'), sda=machine.Pin('C10'))
machine.Pin('C13', machine.Pin.OUT).low()  # mettre courant entrant
machine.Pin('A8', machine.Pin.OUT).high()  # mettre courant sortant

MAX = 128
TOTAL_BEATS = 30

# RTC
rtc = machine.RTC()
rtc.datetime((2023, 2, 21, 3, 14, 25, 58, 0))
# screen
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
width = 0

#buttons

def printTime(oled, tuple):
    year = tuple[0]
    month = tuple[2]
    day = tuple[3]
    hour = tuple[4]
    minute = tuple[5]
    sec = tuple[6]
    oled.text(str(hour) + ":" + str(minute)+":"+str(sec), 65, 0)


def normalize_value(prevValN, prevVal, Val):
    return prevValN + (prevVal - Val)

def readSensor(prevVal):
    # machine.Pin('C2', machine.Pin.IN)
    val = ADC("C0").read()
    
    #print(val)
    return val


def BPM(historyVal):
    bpm = 0
    print(historyVal)
    minima, maxima = min(historyVal), max(historyVal)
    ecart = (minima + maxima * 3) // 4   
    for ind in range(len(historyVal) -1):
        if (historyVal[ind]  > ecart):
            bpm += 1

    return bpm * 6


def printBPM(oled, val): 
    oled.text(str(val), 10, 1)


def printheart(oled):
    HEART = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
    ]
    for y, row in enumerate(HEART):
        for x, c in enumerate(row):
            oled.pixel(x, y, c)




def hearth_line( history, bpm):
    global lastVal
    minima, maxima = min(history), max(history)
    oled.scroll(-1,0)
    for ind in range(len(history)):
        oled.fill_rect(0,0,126,20,0)
        printheart(oled)
        if bpm == 0:
            oled.text("Read",10,1)
        else: 
            printBPM(oled,bpm)
        printTime(oled, rtc.datetime())
        if minima - maxima != 0:
            val = 64 - int(21 * (history[ind] - minima) / (maxima - minima))
            print(lastVal, val)
            oled.line(124, lastVal, 125, val, 1)
            lastVal = val

def printSelecteur(selecteur):
    oled.text(">", 0, selecteur * 10 + 10)

def compute_bpm(beats, previous):
    if beats:
        beat_time = beats[-1] - beats[0]
        if beat_time:
            return (len(beats) / (beat_time)) * 60
    return previous 

def display_heart():
    HEART = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
    ]
    for y, row in enumerate(HEART):
        for x, c in enumerate(row):
            oled.pixel(x, y, c)

    oled.show()

# display heartbeat
def display( bpm, value, min_value, max_value):
    global last_y

    oled.scroll(-1,0) # Scroll left 1 pixel    
    if max_value - min_value > 0:
        # Draw beat line
        y = 64 - int(27 * (value - min_value) / (max_value - min_value))
        print(y)
        oled.line(125, last_y, 126, y, 1)
        last_y = y

    # Clear top text area
    oled.fill_rect(0,0,128,20,0)

    oled.text(str(int(bpm)) + " bpm", 12, 12)
    display_heart()
    
    oled.show()


def main():
    i = 0
    bpm = 0
    global lastVal
    lastVal = 0
    beats = []
    global last_y
    last_y = 0
    referenceval = ADC("C0").read()
    prevVal = ADC("C0").read()

    width = 0
    history = []
    historyVAL = []
    menuList = ["heart","game", "settings"]
    selecteur = 0
    menu = "menu"

    startMesure = rtc.datetime()
    isReading = False
    prevdif = -1
    delay = 0
    while True:
    
        if (menu == 'test'):
            continue

        if (menu == "game"):
            menu = game.Game(oled)

        if (menu == "heart"):
            if sw3.value() == 0:
                menu = "menu"
            if not isReading:
                oled.fill(0)
                printTime(oled, rtc.datetime())
                newVal = readSensor(prevVal)
                print(newVal, abs(newVal - referenceval), isReading)
                prevVal = newVal
                if abs(newVal - referenceval) > 30 :
                    isReading = True
                    startMesure = rtc.datetime()
                    oled.fill(0)
                    delay = 0
                    continue
                oled.text('Put Your Finger',5,35)
                oled.show()
                continue

            if isReading :
                value = ADC('C0').read()
                history.append(value)

                history = history[-MAX:]
                min_value, max_value = min(history), max(history)
                index = (3 * len(history)) // 4
                threshold_on = history[index]

                if value > threshold_on and history[-1] > history[-2]:
                    print('beat  ' + str(value))
                    beats.append(time())
                    # Truncate beats queue to max
                    beats = beats[-TOTAL_BEATS:]
                    bpm = compute_bpm(beats, bpm)

                display( bpm, value, min_value, max_value)
    
            oled.show()
        if menu == "menu":
            oled.fill(0)
            if i == 45:
                i = 0
            oled.text("Go ",i,0)
            if i < 20:
                oled.text("Run",i + 20,0)
            i +=1
            oled.hline(0, 9, 140, 1)
            oled.vline(60,0,9,1)
            oled.vline(61,0,9,1)

            printTime(oled, rtc.datetime())
            sw1Value = sw1.value()
            sw2Value = sw2.value()
            for ind in range(len(menuList)):
                oled.text(menuList[ind], 8, ind * 10 + 10)
            print(menu , sw1Value, selecteur)
            printSelecteur(selecteur)

            if(sw1Value == 0 ): #press button
                menu = menuList[selecteur]
            if (sw2Value == 0): #switch
                selecteur =( selecteur + 1 )% len(menuList)
                sleep_ms(300)
            oled.show()
        if menu == "settings":
            hour = rtc.datetime()[4]
            minute = rtc.datetime()[5]
            sec = rtc.datetime()[6]
            selecteurTime = 0

            while True:
                sw1Value = sw1.value()
                sw2Value = sw2.value()
                sw3Value = sw3.value()
                oled.fill(0)
                oled.text("Set Time",0,0)

                oled.text(str(hour),10 ,35)
                oled.text(":",35,35)
                oled.text(str(minute),50 ,35)
                oled.text(":",75,35)
                oled.text(str(sec),90 ,35)

                oled.text("^",selecteurTime * 40 +10,45)
                print(hour, minute, sec, sw1Value)
                if(sw1Value == 0 ): #press button
                    if selecteurTime == 0:
                        hour = (hour + 1) % 24
                    if selecteurTime == 1:
                        minute = (minute + 1) % 60
                    if selecteurTime == 2:
                        sec = (sec + 1) % 60
                    sleep_ms (100)
                if (sw2Value == 0): #switch
                    selecteurTime =( selecteurTime + 1 )% 3
                    sleep_ms (300)
                if (sw3Value == 0): #switch
                    rtc.datetime((2023, 2, 21, 3, hour, minute, sec, 0))
                    menu = "menu"
                    break


                oled.show()
                continue



main()
