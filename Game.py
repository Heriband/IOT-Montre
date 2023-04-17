import machine
import ssd1306
from pyb import ADC, Pin, Timer
import framebuf
from machine import Pin
import time
from random import randrange
import Obstacle as ob

#buttons
sw1 =  Pin ('SW1', Pin.IN) #validate button
sw1.init (Pin.IN, Pin.PULL_UP, af = -1)

sw2 = Pin ('SW2', Pin.IN)
sw2.init (Pin.IN, Pin.PULL_UP, af = -1)

sw3 = Pin ('SW3', Pin.IN)
sw3.init (Pin.IN, Pin.PULL_UP, af = -1)


def initTerrain(oled):
    for i in range(129):
        oled.text(".",i,55)
        oled.text(".",i,10)

def displayPlayer(oled, niv):
    player = [
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 0, 0],
            ]
    for y, row in enumerate(player):
        for x, c in enumerate(row):
            oled.pixel(x, y + 15 * niv + 20, c)


def getNiveau(niv):
    sw1Value = sw1.value()
    sw2Value = sw2.value()
    if(sw1Value == 0 and niv != 2): #UP
        time.sleep_ms (300)
        niv +=1
    if (sw2Value == 0 and niv != 0): #DOWN
        time.sleep_ms (300)
        niv -=1
    return niv

def addObstacle():
    niv = randrange(3)
    return ob.Obstacle(niv)

def displayObastacle(oled,obs):
    oled.text('X', obs.getPosition(), obs.getNiv() * 15 + 20)
    obs.setPosition(obs.getPosition() - 2)

def timer(list):
    if len(list) == 0:
        return True
    last = list[-1]
    return last.getPosition() < 100


def Game(oled):
    GameOver = False
    niveau = 0 # 0 1 ou 2
    score = 0
    listObstacle = []
    while not GameOver:
        oled.fill(0)

        if len(listObstacle) < 5 and timer(listObstacle):
            listObstacle.append(addObstacle())
            

        for obstacle in listObstacle:
            # obstacle = listObstacle[ind]
            
            if obstacle.getPosition() < 5 and obstacle.getNiv() == niveau:
                GameOver = True
            if obstacle.getPosition() < 0:
                listObstacle.remove(obstacle)
                score += 1
            displayObastacle(oled, obstacle)

        print(len(listObstacle))
        initTerrain(oled)
        displayPlayer(oled,niveau)
        niveau = getNiveau(niveau)
        oled.text("score : " + str(score), 0,0 )
        oled.show()
    oled.fill(0)
    oled.text("GAME OVER", 30, 30)
    oled.show()
    time.sleep(3)
    return "menu"
