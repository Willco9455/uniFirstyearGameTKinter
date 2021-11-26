# Screen Resolution on windows 1280x720

from random import randint
from tkinter import Entry, Image, PhotoImage, Tk, Canvas, Button
from time import sleep
from math import atan, degrees, cos, sin, radians, tan

# base object for all tanks 
class Tank:
    def __init__(self, colour, x=250, y=250, tankSpeed=3):
        self.fireCool = [0, 40]  #fire cooldown [frames to go before next bullet availavle, frame cooldown]
        self.faceUp = False      
        self.tankSpeed = tankSpeed    #defines how far the tank will move with each button press
        self.colour = colour    
        self.spawn(x, y)        
    
    #places the tank on the canvas at x and y coodinates
    def spawn(self, x, y):
        # adds the tank parts to the canvas
        self.body = canvas.create_rectangle(x-30, y+15, x+15, y-15, fill=self.colour)
        self.gun = canvas.create_image(x - 7, y - 0.75, image=gunImages['0'])
    
    # will move the rectangle body to the direction passed into the method
    def rotateBody(self, direction):
        # roates the body of the tank either up or down
        coords = canvas.coords(self.body)
        if direction == 'up' and self.faceUp == False:
            x0, y0 = (coords[0] +7.5), (coords[3] +7.5)
            x1, y1 = (coords[2] -7.5), (coords[1] -7.5)
            canvas.coords(self.body, x0, y0, x1, y1)
            self.faceUp = True
        elif direction == 'side' and self.faceUp == True:
            x0, y0 = (coords[0] -7.5), (coords[3] -7.5)
            x1, y1 = (coords[2] +7.5), (coords[1] +7.5)
            canvas.coords(self.body, x0, y0, x1, y1)
            self.faceUp = False

    # getter for the coordinate of the tank return just an one x and one y unlike the bbox function
    def getCoords(self):
        return (canvas.coords(self.gun))

    # returns the bbox for the body of the tank, similar to the getCoords but this format is used for collision detection
    def getBbox(self):
        return (canvas.bbox(self.body))

    # rounds the angle passed in to the nearest 45 degreese used for selecting the correct image for the tank gun
    def roundAngle(self, angle):
        # rounds the degree to the nereest 45
        noRem = (angle // 45) * 45
        rem = angle % 45
        if rem > 22.5:
            noRem += 45
        angle = noRem
        
        return angle
    

# the object for the players tank extends Tank object
class PlayerTank(Tank): 
    def __init__(self, colour, x, y):
        Tank.__init__(self, colour, x, y)
        self.fireSpeed = 3
    
    # runs on key inputs  
    def move(self, event):
        tankBbox = canvas.bbox(self.body)
        if event.char == 'w' and tankBbox[1] > 0:
            canvas.move(self.body, 0, -self.tankSpeed)
            canvas.move(self.gun, 0, -self.tankSpeed)
            self.rotateBody('up')
        elif event.char == 's' and tankBbox[3] < winHeight:
            canvas.move(self.body, 0, self.tankSpeed)
            canvas.move(self.gun, 0, self.tankSpeed)
            self.rotateBody('up')
        elif event.char == 'a'  and tankBbox[0] > 0:
            canvas.move(self.body, -self.tankSpeed, 0)
            canvas.move(self.gun, -self.tankSpeed, 0)
            self.rotateBody('side')
        elif event.char == 'd' and tankBbox[2] < winWidth:        
            canvas.move(self.body, self.tankSpeed, 0)
            canvas.move(self.gun, self.tankSpeed, 0)       
            self.rotateBody('side')
        
        self.checkGun(self.mouseRecord[0], self.mouseRecord[1])
        canvas.config(bg="grey")
        window.update() 

    # returns the angle that the mouse is from to the tank rounded to 45
    def mouseAngle(self, mousex, mousey):
        
        # gets the precise angle
        tankCoord = canvas.coords(self.gun)
        angle = findAngle(tankCoord[0], tankCoord[1], mousex, mousey)
        
        return self.roundAngle(angle)
     
    # moves the gun to the correct possition depending on the mouse input given     
    def mouseMove(self, mousex, mousey):
        self.mouseRecord = [mousex, mousey]
        angle = self.mouseAngle(mousex, mousey)
        canvas.itemconfig(self.gun, image=gunImages[str(angle)])

    # runs when space bar is pressed to fire the gun
    def fire(self, event):
        # will fire only if the colldown from the last shot is at 0
        if self.fireCool[0] == 0:
            coords = canvas.coords(self.gun)
            angle = findAngle(coords[0], coords[1], self.mouseRecord[0], self.mouseRecord[1])
            bulletFire(coords[0], coords[1], angle, False, self.fireSpeed)
            
            # resets the cooldown 
            self.fireCool[0] = self.fireCool[1]
        
    # this function will run every time there is a new frame
    def newFrame(self):
        # decreses the time since last shot by 1 every frame for the cooldown functionality of the gun  
        if self.fireCool[0] != 0:
            self.fireCool[0] -= 1    
            
    def teleport(self, x, y): 
        canvas.delete(self.body)
        canvas.delete(self.gun)
        self.faceUp = False
        self.spawn(x, y)
    
    def setSpeed(self, speed):
        self.tankSpeed = speed
        

class EnemyTank(Tank):
    def __init__(self, colour, x=250, y=250, fireSpeed=10):
        Tank.__init__(self, colour, x, y)
        self.fireCool = [randint(0,100), 100]
        self.fireSpeed = fireSpeed

    def fire(self):
        # will fire only if the colldown from the last shot is at 0
        coords = canvas.coords(self.gun)
        myCoords = self.getCoords()
        tnkCoords = playerTank.getCoords()
        angle = findAngle(myCoords[0], myCoords[1], tnkCoords[0], tnkCoords[1])
        bulletFire(coords[0], coords[1], angle, True, self.fireSpeed)
        
    def newFrame(self):
        myCoords = self.getCoords()
        tnkCoords = playerTank.getCoords()
        angle = findAngle(myCoords[0], myCoords[1], tnkCoords[0], tnkCoords[1])
        roundAngle = self.roundAngle(angle)
        canvas.itemconfig(self.gun, image=gunImages[str(roundAngle)])
        if self.fireCool[0] == 0:
            self.fire()
            # resets the fire cooldown
            self.fireCool[0] = self.fireCool[1]
        else:
            self.fireCool[0] -= 1
            
    def destroyTank(self):
        canvas.delete(self.body)
        canvas.delete(self.gun)

         
class bullet: 
    
    def __init__(self, x, y, angle, enemy, speed=2):
        self.tol = 400      #sets the time of life of the bullet
        self.angle = angle  #the angle of the bullet which is set when the bullet is initialized
        self.bulSpeed = speed #speed of the bullet which is by default 1.5
        self.enemy = enemy
        self.spawn(x, y)
        
    def spawn(self, x, y):
        if self.enemy == True:
            colour = 'maroon'
        else:
            colour = 'pink'

        self.body = canvas.create_oval(x+3, y+3, x-3, y-3, fill=colour)
        canvas.config(bg="grey")
    
    # this funtion will run every time there is a new frame
    def newFrame(self):
        xmove = cos(radians(self.angle)) * self.bulSpeed
        ymove = sin(radians(self.angle)) * self.bulSpeed
        if self.tol > 0:
            canvas.move(self.body, xmove, -ymove)
            self.tol -= 1
            return True
        else:
            self.delete()
            self.tol -= 1
            return False
    
    def delete(self):
        canvas.delete(self.body)
        
    def setAngle(self, angle):
        self.angle = angle
        
    def getCoords(self):
        return canvas.bbox(self.body)

# class for controlling the game logic such as loading levels, pausing, updateing leaderboard etc.
class game:
    def __init__(self):
        self.score = 0
        self.enTanks = []
        self.walls = []
        self.paused = False
        self.timer = 0
        self.level = 1
        self.scoreTxt = ''
        self.levelTxt = ''
        self.boss = False
        self.bossImage = ''
        self.home = True
    
    # handels what to do when p is pressed
    def pausePress(self, event):
        if self.paused == False:
            self.paused = True
            self.pauseOverlay = canvas.create_rectangle(0,0, winWidth, winHeight, fill='black')
            self.pauseText = canvas.create_text(winWidth/2, winHeight/2, text='PAUSED', font=('Helvetica', '30', 'bold'), fill='white')

        else:
            self.paused = False
            canvas.delete(self.pauseOverlay)
            canvas.delete(self.pauseText)
            
    def displayText(self):
        self.scoreTxt = canvas.create_text(winWidth - 70, 15, text=f'Score: {self.score}', font=('Helvetica', '16'))
        self.levelTxt = canvas.create_text(winWidth/2, 15, text=f'Level {self.level}', font=('Helvetica', '16'))
        
    def hideText(self):
        canvas.delete(self.scoreTxt)
        canvas.delete(self.levelTxt)
    
    # adds 1 to the current score, runs when a enemy tank is hit
    def addScore(self):
        self.score += 1
        self.hideText()
        self.displayText()
    
    def playerHit(self):
        for i in bullets:
            i.delete() 
        bullets.clear()
        self.paused = True
        self.overlay = canvas.create_rectangle(0,0, winWidth, winHeight, fill='black')
        self.text1 = canvas.create_text(winWidth/2, winHeight/2, text='GAME OVER :(', font=('Helvetica', '30', 'bold'), fill='white')
        self.text2 = canvas.create_text(winWidth/2, winHeight/2 + 60, text=f'Score: {self.score}', font=('Helvetica', '30', 'bold'), fill='white')
        window.update()
        sleep(3)
        
        canvas.delete(self.overlay)
        canvas.delete(self.text1)
        canvas.delete(self.text2)

        self.updateLeaderboard()
        
        self.paused = False
        self.level = 1
        self.score = 0

        for i in range(0, len(enTanks)):
            enTanks[i].destroyTank()
        enTanks.clear()
        
        screenMan.switchScreen()
        
    def updateLeaderboard(self):
        userData = [username.get(), str(self.score)]
        file = open('leaderboard.txt', 'r')
        data = file.read()
        file.close()
        data = data.split('\n')
        leaderboard = []
        inserted = False
        for i in data:
            playerData = i.split(':')
            if int(userData[1]) >= int(playerData[1]) and inserted == False:
                leaderboard.append(userData)
                inserted = True
            if len(leaderboard) < 10:
                leaderboard.append(playerData)
        if len(leaderboard) < 10 and inserted == False:
            leaderboard.append(userData)
        
        file = open('leaderboard.txt', 'w')
        for i in range(0, len(leaderboard)):
            if i == len(leaderboard) - 1:
                text = leaderboard[i][0] + ':' + leaderboard[i][1]
            else:
                text = leaderboard[i][0] + ':' + leaderboard[i][1] + '\n'
                
            file.writelines(text)
        file.close()
    
    # will run every time the user destroys all the tanks in a level 
    def levelComplete(self): 
        # removes all the bullets left on the screen and clears the bullet array
        for i in bullets:
            i.delete() 
        bullets.clear()

        text = canvas.create_text(winWidth/2, winHeight/2, text='LEVEL COMPLETE', font=('Helvetica', '30', 'bold'), fill='black')  
        window.update()
        sleep(1)
        playerTank.teleport(winWidth/2, winHeight/2 + 60)
        self.level += 1
        self.hideText()
        self.displayText()
        canvas.itemconfig(text, text=f'level {self.level}')
        window.update()
        self.loadLevel()
        sleep(1)
        canvas.delete(text)
        
    # goes through all the checks needed for a new frame
    def newFrame(self):
        if self.paused == True:
            return
        
        playerTank.newFrame()
        self.timer += 0.01
        if self.timer < 1:
            return
        
        for i in enTanks:
            i.newFrame()
        
        # if the user has destroyed all the tanks
        if len(enTanks) == 0:
            self.levelComplete()
            
        self.updateBullets()
        
                              
    # loops though every bullet and moves it or terminates it if it has reached the end of its life
    def updateBullets(self):
        if len(bullets) == 0:
            return
        
        for i in range(0, len(bullets)):
            # makes sure thhe list wont be out of range
            if i > len(bullets):
                return
            
            # checks if the bullet has reched the end of its time of life and if it has it will delete it 
            alive = bullets[i - 1].newFrame()
            if not alive:
                del bullets[i - 1]
                i = i - 1

            # if the last bullet was deleted then quit out of the loop
            if len(bullets) == 0:
                return
            
            # gets bbox of current bullet
            try:
                coords = bullets[i - 1].getCoords()
            except:
                return
            # runs if bullet is an enemy 
            if bullets[i - 1].enemy == True:
                playerCoords = playerTank.getBbox()
                
                # if the bullet has collided with the player then delete the bullet and ...
                if collisionCheck(playerCoords, coords):
                    bullets[i - 1].delete()
                    del bullets[i - 1]
                    
                    #PLAYER HIT
                    self.playerHit()
            else:
                for j in range(0, len(enTanks)):
                    enTankBbox = enTanks[j].getBbox()
                    if collisionCheck(enTankBbox, coords):
                        # delets bullet 
                        bullets[i - 1].delete()
                        del bullets[i - 1]
            
                        #TANK HIT
                        enTanks[j].destroyTank()
                        del enTanks[j]
                        control.addScore()
                        return
    
    # will return the x and y location of an available spawn location
    def findSpawn(self):
        x = 0
        y = 0
        while x == 0 and y == 0:
            # sets the area size from the centre where enemy tanks cant spawn
            spawnArea = 200
            x = randint(20, winWidth - 10)
            y = randint(20, winHeight -10)
            bbox = [x-30, y+15, x+15, y-15]
            x0 = winWidth/2 - spawnArea
            y0 = winHeight/2 -spawnArea
            x1 = winWidth/2 + spawnArea
            y1 = winHeight/2 + spawnArea
            avoidBbox = [x0, y0, x1, y1]
            if collisionCheck(avoidBbox, bbox):
                x, y = 0, 0
        return x, y 
    
    def loadLevel(self):
        
        print(f'level {self.level}')
        colours = ['green', 'orange', 'red']
        numTanks = self.level // 3
        tankLvl = self.level % 3
        tempTanks = []
        for i in range(0, numTanks):
            xpos, ypos = self.findSpawn()
            tempEnemy = EnemyTank(colours[2], xpos, ypos, 3)
            enTanks.append(tempEnemy)
            
        if tankLvl != 0:
            xpos, ypos = self.findSpawn()
            tempEnemy = EnemyTank(colours[tankLvl - 1], xpos, ypos, tankLvl)
            enTanks.append(tempEnemy)
        
         
        self.hideText()
        self.displayText()
        return tempTanks

    def bossScreen(self, event):
        self.boss = not self.boss
        if self.boss:
            self.bossImage = canvas.create_image(winWidth/2, winHeight/2 ,image=bossImage)
            self.paused = True
        else:
            self.paused = False
            canvas.delete(self.bossImage)

    def clearLvl(self):
        canvas.delete('all')

    def homeScreen(self):
        menu.append(canvas.create_rectangle(0, 0, winWidth, winHeight, fill='#228B22'))
        menu.append(canvas.create_text(winWidth/2, 50, text="TANK GAME", font=('Helvetica', '30')))
        
        menu.append(canvas.create_text(winWidth/2, 250, text="Name", font=('Helvetica', '14')))
        menu.append(canvas.create_window(winWidth/2,270, window=username))
        
        menu.append(canvas.create_text(winWidth/2, 290, text="CheatCode", font=('Helvetica', '14')))
        menu.append(canvas.create_window(winWidth/2,310, window=cheatCode))
        
        menu.insert(0, Button(window, text='Start', background='pink', width="10", height="2", command= lambda: self.startClicked()))
        menu[0].place(x=((winWidth/2) - 40), y=340)
        
        menu.append(canvas.create_text(winWidth/5, 50, text="How To Play", font=('Helvetica', '20')))
        howPlayTxt = """ The aim of the game is to destroy as many of the enemy\n tanks as possible You will get 1 point for each tank destroyed \n the tanks will get more powerful and there will be more tanks as\n you progress throug the levels there are 3 different types of tanks \n green, orange, red with red green being the weekest and red \n bieng the strongest."""
        menu.append(canvas.create_text(winWidth/5, 130, text=howPlayTxt, font=('Helvetica', '12')))
        
        menu.append(canvas.create_text(winWidth/5, 250, text="Controls", font=('Helvetica', '20')))
        controlsTxt = """Move Forward:          W\nMove Left:                  A\nMove Backwards:     S\nMove Right:                D\nAim Gun:            Mouse Move\nFire Gun:                Space\nPause Game:            P\nBoss Key:                  B\n\nCheatCode is 'redbull' gives speed boost"""
        menu.append(canvas.create_text(winWidth/5, 360, text=controlsTxt, font=('Helvetica', '12')))
        
        # displays the leaderboard 
        menu.append(canvas.create_text(winWidth * 0.80, 50, text="Leaderboard:", font=('Helvetica', '30')))
        file = open('leaderboard.txt', 'r')
        data = file.read()
        data = data.split('\n')
        yseperator = 100
        for i in range(0, len(data)):
            user = data[i].split(':')
            menu.append(canvas.create_text(winWidth * 0.80, yseperator, text=f"{i + 1}. {user[0]}:   {user[1]}", font=('Helvetica', '20')))
            yseperator += 35

        window.update()
        
    def startClicked(self):
        # this if statment will handel if a correct cheatcode has been entered 
        if cheatCode.get() == 'redbull':
            print('cheatcode used')
            playerTank.setSpeed(8)
        

        screenMan.startGame()
        canvas.focus_set()

    
class gameLoop:
    def __init__(self):
        self.screen = 'menu'
        self.gameLoaded = False
        self.menuLoaded = False
    
    def switchScreen(self):
        if self.screen == 'menu':
            self.screen = 'game'
            self.gameLoaded = False
        else: 
            self.screen = 'menu'
            self.menuLoaded = False
            
    def getScreen(self):
        return self.screen

    def loadGameScreen(self):
        
        for i in menu:
            try:
                canvas.delete(i)
            except:
                i.destroy()
        
        if self.gameLoaded == False:    
            control.loadLevel()
            self.gameLoaded = True
            self.menuLoaded = False
            
    def loadMenuScreen(self):
        for i in enTanks:
            i.destroyTank()
        enTanks.clear()
        
        if self.menuLoaded == False:    
            control.homeScreen()
            self.menuLoaded = True
            self.gameLoaded = False
    
    def startGame(self):
        if username.get() != '':
            self.screen = 'game'
        else:
            error = canvas.create_text(winWidth/2, 180, text="Need to enter a name", fill='red' , font=('Helvetica', '14'))
            window.update()
            sleep(2)
            canvas.delete(error)
            window.update()
            
def findAngle(x0, y0, x1, y1):
    # gets the precise angle between two coodinates treating x0,y0 as the origin
    x = x1 - x0
    y = y0 - y1
    # prevents not divisible by 0 error 
    if int(x) == 0:
        x = 1
    
    degree = degrees(atan(int(y) / int(x)))
        
    if x < 0 and y > 0:
        degree = 180 + degree
    elif x < 0 and y < 0:
        degree =  180 + degree 
    elif x > 0 and y < 0:
        degree = 360 + degree
    degree = int(degree)
    
    return degree

# mouse movement handeler
def mouseMove(event):
    x = event.x
    y = event.y
    playerTank.mouseMove(x, y)

# runs when a bullet is fired, creates bullet object and stores it in array 
def bulletFire(x, y, angle, enemy, speed=2):
    tempBul = bullet(x, y, angle, enemy, speed=speed)
    bullets.append(tempBul)
                             
# returns true when if the two bboxs of objects are overlapping 
# bbox 1 must be the bigger object
def collisionCheck(bbox1, bbox2):
    if  ((bbox1[3] > bbox2[3] > bbox1[1]) and (bbox1[0] < bbox2[0] < bbox1[2])) or ((bbox1[3] > bbox2[3] > bbox1[1]) and (bbox1[0] < bbox2[2] < bbox1[2])) or ((bbox1[3] > bbox2[1] > bbox1[3]) and (bbox1[0] < bbox2[0] < bbox1[2])) or ((bbox1[3] > bbox2[1] > bbox1[3]) and (bbox1[0] < bbox2[2] < bbox1[2])):
        return True
    else: 
        return False




# initiates the lists that will be filled with the canvas objects, declared in the main program so that can be accessed within objects
enTanks = []
bullets = []
menu = [None, None, None]

boss = False

window = Tk()

bossImage = PhotoImage(file='bossImg.png')
# dictionary with images for different roations of the tank  
gunImages = {
    '0': PhotoImage(file='tank_images/tank_gun_000.png'),
    '45': PhotoImage(file='tank_images/tank_gun_045.png'),
    '90': PhotoImage(file='tank_images/tank_gun_090.png'),
    '135': PhotoImage(file='tank_images/tank_gun_135.png'),
    '180': PhotoImage(file='tank_images/tank_gun_180.png'),
    '225': PhotoImage(file='tank_images/tank_gun_225.png'),
    '270': PhotoImage(file='tank_images/tank_gun_270.png'),
    '315': PhotoImage(file='tank_images/tank_gun_315.png'),
    '360': PhotoImage(file='tank_images/tank_gun_000.png'),
    }

# 1280x720
winWidth = 1280
winHeight = 650

print(winWidth, winHeight)
window.title('Tank Typhoon')
canvas = Canvas(window, width=winWidth, height=winHeight)
canvas.pack()

canvas.config(bg="grey")
canvas.focus_set()

# initiate the game object with will be used to control how the game works
username = Entry(canvas)
cheatCode = Entry(canvas)
control = game()    
screenMan = gameLoop()
# def startGame()

playerTank = PlayerTank('blue', winWidth/2, winHeight/2)


canvas.bind("<Motion>", mouseMove)
# player tank movement bindings 
canvas.bind('w', playerTank.move)
canvas.bind('s', playerTank.move)
canvas.bind('a', playerTank.move)
canvas.bind('d', playerTank.move)
canvas.bind('p', control.pausePress)
canvas.bind('<space>', playerTank.fire)
canvas.bind('b', control.bossScreen)


window.update()

while True:
    if screenMan.getScreen() == 'menu':
        # print('in menu loop')
        if screenMan.menuLoaded == False:
            screenMan.loadMenuScreen()
            print('loaded menu')
        else:
            window.update()
    else:
        # print('in Game loop')
        if screenMan.gameLoaded == False:
            screenMan.loadGameScreen()
        window.update()
        control.newFrame()
        sleep(0.001)

    
window.mainloop()
