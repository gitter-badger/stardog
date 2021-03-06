#gui.py
#
from pygame.locals import *
from utils import *
from spaceship import Ship
from planet import Planet
from parts import *
from cargo import *
from vec2d import *
from collections import deque
import pygame


class Drawable(object):

    def __init__(self, universe):
        self.universe = universe
        self.player = universe.player

        self.rect = Rect(0, 0, self.universe.game.width,
                         self.universe.game.height)

    def setRect(self, rect):
        self.rect = rect

    def setCamera(self, camera):
        self.camera = camera

    def setPlayer(self, player):
        self.player = player

    def update(self):
        pass

    def draw(self):
        pass

class Messenger(Drawable):
    # not capitalized in stand lib
    
    # font = FONT

    def __init__(self, universe, font, dir=1):
        Drawable.__init__(self, universe)
        queue = deque()
        # -1 means the messages stack upward.
        self.font = FONT
        self.dir = dir
        self.rect = col12row9(universe.game, 0, 0, 9, 1)
        self.image = pygame.Surface((self.rect.width,self.font.get_linesize()))
        # characters per second
        self.speed = 40
        self.image.set_alpha(200)
        # self.topleft = 0, 0
        self.maxMessages = 100
        # seconds after each message
        self.messageDelay = 9
        # line width
        self.maxChars = 200
        self.universe = universe
        self.game = universe.game
        self.soundsys = self.universe.game.soundSystem
        self.popupsound = 'message pip.ogg'
        self.soundsys.register(self.popupsound)

    def chunks(self, the_list, length):
        """ Yield successive n-size chucks from the_list.
        """
        for i in xrange(0, len(the_list), length):
            yield the_list[i:i+length]

    def message(self, text, color=SUPER_WHITE):
        """message(text,color) -> add a message to the Messenger."""
        text = '   ' + text
        # line length limit
        if len(text) > self.maxChars:
            for sentence in self.chunks(text, self.maxChars):
                linger = (self.game.timer+1.*len(sentence)/self.speed
                          + self.messageDelay)
                queueItem = (self.font.render(sentence, True, color), linger)
                self.queue.append(queueItem)
            return
        linger = (self.game.timer + 1. * len(text) / self.speed
                  + self.messageDelay)
        queueItem = (self.font.render(text, True, color), linger)
        self.queue.append(queueItem)
        self.soundsys.play(self.popupsound)

    def update(self):
        if self.queue and self.game.timer > self.queue[0][1] \
           or len(self.queue) > self.maxMessages:
            self.queue.popleft()

    def draw(self, surface):
        y = self.rect.y
        for message in self.queue:
            self.image.fill((0, 0, 80))
            self.image.blit(message[0], (0, 0))
            surface.blit(self.image, (self.rect.x, y))
            y += self.font.get_linesize() * self.dir

    def empty(self):
        self.queue = deque()

class HUD(Drawable):
    def __init__(self, universe):
        Drawable.__init__(self, universe)
        self.player = universe.game.player
        self.arect = col12row9(universe.game, 10, 8, 2, 3)


        self.image = pygame.Surface((self.arect.width, self.arect.height), flags=(SRCALPHA))
        
        self.bar1 = LifeBar( universe, 130, False, 10, (255,0,0))
        self.bar2 = LifeBar( universe, 130, False, 10, (0,255,0))
        self.bar3 = LifeBar( universe, 130, False, 10, (0,0,255))

    def draw(self, surface):
        """updates the HUD and draws it."""
       
        self.image.fill((SHIPDAMAGE))
        if self.player:
            self.bar1.updateset(0,self.player.energy, self.player.maxEnergy)
            self.bar2.updateset(0, self.player.xp, 100)
            if self.player.maxhp:
                self.bar3.updateset(0, self.player.hp, self.player.maxhp)

            self.bar1.draw(self.image,(20, 50))
            self.bar2.draw(self.image, (50, 50))
            if self.player.maxhp:
                self.bar3.draw(self.image, (80, 50))

            # empty bar
            pygame.draw.rect(self.image, HUD1, self.arect, 1)
            self.image.blit(FONT.render("E", False, (255,0,0)), (20, 10))
            self.image.blit(FONT.render("XP", False, (0,255,0)), (50, 10))
            if self.player.maxhp:
                self.image.blit(FONT.render("S", False, (0,0,255)), (80, 10))

            hudpos = self.arect.x, self.arect.y
            surface.blit(self.image, (hudpos))


class RadarField(Drawable):
    def __init__(self, universe):
        Drawable.__init__(self, universe)
        self.rect = col12row9(universe.game, 9, 0, 1, 2)
        self.rect.width += 43
        self.radarRadius = self.rect.width
        self.center = (self.radarRadius, self.radarRadius)
        self.image = pygame.Surface((self.radarRadius*2, self.radarRadius*2))
        self.image.set_alpha(200)
        self.zoomModifier = 1
        maskimagesize = (self.radarRadius*2, self.radarRadius*2)
        self.maskimage = pygame.Surface(maskimagesize)
        self.maskimage.fill(SHIPDAMAGE)
        pygame.draw.circle(self.maskimage, BLACK,
                           self.center, self.radarRadius)
        self.maskimage.set_colorkey(BLACK)
        self.targimage = pygame.Surface((8, 8))
        self.targimage.set_colorkey(BLACK)

    def draw(self, surface):
        radius = self.radarRadius
        center = self.center
        # self.image.fill((255, 0, 0))
        scale = self.radarRadius * self.zoomModifier
        pygame.draw.circle(self.image, SHIPDAMAGE2,
                           self.center, self.radarRadius)
        # draw floating part dots:
        if self.player:
            if (self.player.radars[-1].disk and self.player.radars[-1].enabled and int(self.player.radars[-1].disk.radius / scale + 2) < 100):
                pygame.draw.circle(self.image, HUD1, center, int(self.player.radars[-1].disk.radius / scale + 2), 1)
            if self.universe.curSystem in self.player.knownsystems:
                for planet in self.player.knownsystems[self.universe.game.universe.curSystem]:
                    result = planet.pos - self.player.pos
                    dotPos = int(center[0] + limit(-radius, result.x / scale, self.radarRadius)), int(center[1] + limit(-self.radarRadius, result.y / scale, self.radarRadius))
                    r = int(planet.radius / scale + 2)
                    if collisionTest(Floater(self.universe, Vec2d(dotPos), Vec2d(0, 0), 0, 0), Floater(self.universe, Vec2d(center), Vec2d(0, 0), 0, 100)):
                        color = planet.color
                        if self.player.curtarget == planet:
                            targetRect(self.image, MINI2, SHIPDAMAGE, dotPos, r, 2)
                        pygame.draw.circle(self.image, color, dotPos, r)
                    else:
                        color = (255, 250, 0)
                        modi = 5
                        if self.player.curtarget == planet:
                            color = (0, 255, 250)
                            modi = 10
                        normalised = result.normalized()
                        pos = []
                        pos.append(normalised * (self.radarRadius - modi) + center)
                        pos.append((normalised * self.radarRadius).rotated(2) + center)
                        pos.append((normalised * self.radarRadius).rotated(-2) + center)
                        pygame.draw.polygon(self.image, color, pos)

            for floater in self.player.radars[-1].detected:
                result = floater.pos - self.player.pos
                dotPos = int(center[0] + limit(-self.radarRadius,   result.x / scale, self.radarRadius)), \
                        int(center[1] + limit(-self.radarRadius, result.y / scale, self.radarRadius))
                if collisionTest(Floater(self.universe, Vec2d(dotPos), Vec2d(0, 0), 0, 0), Floater(self.universe, Vec2d(center), Vec2d(0,0), 0, 100)):
                    if isinstance(floater, Ship):
                        if self.player.curtarget == floater:
                            self.image.blit(self.targimage,
                                            (dotPos[0]-4, dotPos[1]-4))
                        pygame.draw.circle(self.image, (250, 250, 0), dotPos, 2)
                        color = floater.color
                        r = 1
                        pygame.draw.rect(self.image, color,
                                         (dotPos[0]-1, dotPos[1]-1, 2, 2))
                    elif not isinstance(floater, Planet):
                        if self.player.curtarget == floater:
                            self.image.blit(self.targimage,
                                            (dotPos[0]-4, dotPos[1]-4))
                        if isinstance(floater, Bullet):
                            pygame.draw.rect(self.image, (150, 40, 0),
                                             (dotPos[0]-1, dotPos[1]-1, 2, 2))
                        elif isinstance(floater, Part) or isinstance(floater, Cargo):
                            pygame.draw.rect(self.image, (200, 200, 0),
                                             (dotPos[0]-1, dotPos[1]-1, 2, 2))
                elif not isinstance(floater, Planet):
                    color = (255, 0, 0)
                    modi = 7
                    if self.player.curtarget == floater:
                        color = MINI2
                        modi = 10
                    normalised = result.normalized()
                    pos = []
                    pos.append(normalised * (self.radarRadius - modi) + center)
                    pos.append((normalised * self.radarRadius).rotated(2) + center)
                    pos.append((normalised * self.radarRadius).rotated(-2) + center)
                    pygame.draw.polygon(self.image, color, pos)

            psdffs = self.universe.game.universe.curSystem.getNeighborposdiff()
            for diff in psdffs:
                angle = diff[1].get_angle()-180
                ddiamond(self.image, (255, 255, 255),
                         Vec2d(center).rotatedd(angle, 97), 1)

            pygame.draw.line(self.image, SUPER_WHITE, (0, self.radarRadius),
                             (self.radarRadius*2, self.radarRadius), 1)

            pygame.draw.line(self.image, SUPER_WHITE, (self.radarRadius, 0),
                             (self.radarRadius, self.radarRadius*2), 1)

            self.image.blit(self.maskimage, (0, 0))

            pygame.draw.circle(self.image, SUPER_WHITE,
                               self.center, self.radarRadius, 1)

            surface.blit(self.image,
                         (self.rect.x, self.rect.y))

    def zoomInRadar(self):
        if self.zoomModifier <= 2.4:
            self.zoomModifier += 0.2

    def zoomOutRadar(self):
        if self.zoomModifier > 0.4:
            self.zoomModifier -= 0.2


class TargetingRect(Drawable):

    def __init__(self, universe):
        Drawable.__init__(self, universe)
        self.image = pygame.Surface((50, 50))

    def draw(self, surface):
        if self.player and self.player.curtarget and not isinstance(self.player.curtarget, Planet) and self.player.curtarget in self.universe.game.spaceview.onScreen:
            if self.image.get_width() != self.player.curtarget.radius:
                self.image = pygame.Surface((self.player.curtarget.radius*2+4, self.player.curtarget.radius*2+4))
                targetRect(self.image, MINI2, BLACK , (self.image.get_width()/2, self.image.get_height()/2), self.player.curtarget.radius, 2)
                self.image.set_colorkey(BLACK)

            result = (self.player.curtarget.pos - self.player.pos).inttup()
            result = result[0] + self.universe.game.width / 2 - self.image.get_width() / 2,  result[1] + self.universe.game.height / 2 - self.image.get_height() / 2,
            surface.blit(self.image,result)


class StarField(Drawable):
    def __init__(self, universe):
        Drawable.__init__(self, universe)
        self.numStars = 300
        self.stars = []
        for star in range(self.numStars):
            brightness = int(randint(100, 255))
            # a position, a color, and a depth.
            self.stars.append((
                randint(0, self.universe.game.width),
                randint(0, self.universe.game.height),
                randint(1, 20),
                (randint(brightness * 3 / 4, brightness),
                 randint(brightness * 3 / 4, brightness),
                 randint(brightness * 3 / 4, brightness))))
    """
        adjusting the max value (in this case 5000)
        makes the starlines bigger or smaller
    """
    def draw(self, surface):
        maxVal = 5000*2
        if self.player:
            xstarlen = (self.player.delta.x*100/(maxVal*2))
            ystarlen = (self.player.delta.y*100/(maxVal*2))
            for star in self.stars:
                x = int(star[0] - self.player.pos.x / star[2]) % (self.universe.game.width-1)
                y = int(star[1] - self.player.pos.y / star[2]) % (self.universe.game.height-1)
                """ drawing stars with set_at draws points. with draw.
                    line draws lines."""
                pygame.draw.line(surface, star[3], (x, y),
                                 (x+xstarlen, y+ystarlen), 1)

class LifeBar(object):

    def __init__(self, universe, length, hori, beginval, color):
        self.hori = hori
        if hori:
            self.rect = Rect(0, 0, length, 5)
        else:
            self.rect = Rect(0, 0, 5, length)
        self.dynamicrect = Rect(1, 1, self.rect.width-2, self.rect.height-2)
        self.game = universe.game
        self.length = length
        self.color = color
        self.beginvalue = beginval
        self.image = pygame.Surface((self.rect.width, self.rect.height))



    def updateset(self, mini ,value, maxi):
        
        ratio = (value / (maxi-mini))
        if self.hori and value < self.rect.width and value > 0:
            self.dynamicrect.width = (ratio * self.rect.width)
            self.dynamicrect.x = self.rect.width - (ratio * self.rect.width) 

        if not self.hori and value < self.rect.height and value > 0:
            self.dynamicrect.height = (ratio * self.rect.height)
            self.dynamicrect.y = self.rect.height - (ratio * self.rect.height) 


    def draw(self, surface, offset):
        if self.game.player:
            pygame.draw.rect(self.image, (0,0,0), self.rect)
            
            pygame.draw.rect(self.image, HUD2, self.rect, 1)
            
            pygame.draw.rect(self.image, self.color, self.dynamicrect) 
            
            surface.blit(self.image, offset)


class BGImage(Drawable):
    pic = None

    def __init__(self, universe):
        Drawable.__init__(self, universe)
        rect = (self.universe.game.width, self.universe.game.height)
        directory = 'res/Tarantula Nebula.jpg'
        self.pic = pygame.transform.scale(loadImage(directory), rect)

    def draw(self, surface):
        surface.blit(self.pic, (0, 0))


class MiniInfo(Drawable):
    color = (100, 100, 255)
    # line width
    maxChars = 50
    targimage = None
    mutatedimage = None
    texts = []

    def __init__(self, universe, font):
        Drawable.__init__(self, universe)
        self.font = font
        self.targ = None
        self.rect = col12row9(self.universe.game,0,9,2,3)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.set_alpha(200)
        self.palette = tuple([(i, i, i) for i in range(256)])

    def update(self):
        if self.player:
            self.targ = self.player.curtarget

    def draw(self, surface):
        self.image.fill((0, 0, 80))
        if self.targ:
            self.texts = []
            name = ""
            linedeltastart = Vec2d(10, 180)
            linedirstart = Vec2d(40, 180)
            pygame.draw.circle(self.image, MINI2, linedeltastart, 10, 1)
            pygame.draw.line(self.image, MINI2, linedeltastart,
                             self.targ.delta.normalized()*10+linedeltastart)
            distance = "Distance Km:" + makeKMdistance(self.player, self.targ)
            pygame.draw.circle(self.image, MINI2, linedirstart, 10, 1)
            pygame.draw.line(self.image, MINI2, linedirstart,
                             (self.targ.pos-self.player.pos).normalized()*10+linedirstart)

            if isinstance(self.targ, Ship):
                linedirstart = Vec2d(100, 180)
                pygame.draw.circle(self.image, SUPER_WHITE,
                                   linedirstart, 10, 1)
                pygame.draw.line(self.image, SUPER_WHITE, linedirstart, linedirstart.normalized().rotated(self.targ.dir)*10+linedirstart)
                name = self.targ.firstname + " " + self.targ.secondname
                if not self.targimage == self.targ.greyImage:
                    self.targimage = self.targ.greyImage
                    # we can realy us some way to make this surface in grayscale, but most solutions have serious drawbacks
                    self.mutatedimage = pygame.transform.rotozoom(self.targimage, 90,2)      
                offset = ((self.rect.width/2) - (self.mutatedimage.get_width()/2), (self.rect.height/2)-(self.mutatedimage.get_height()/2))
                self.image.blit(self.mutatedimage, offset)
            elif isinstance(self.targ, Planet):
                name = self.targ.firstname
                scale = self.universe.game.radarfield.radarRadius * self.universe.game.radarfield.zoomModifier
                if (self.targ.radius / scale) < self.rect.width/2:
                    r = int(self.targ.radius / scale)
                else:
                    r = self.rect.width / 2
                pygame.draw.circle(self.image, self.targ.color, ((self.rect.width/2,self.rect.height/2)), r)
            elif isinstance(self.targ, Part) or isinstance(self.targ, Cargo):
                name = self.targ.name
                if not self.targimage == self.targ.baseImage:
                    self.targimage = self.targ.baseImage
                     # we can realy us some way to make this surface in grayscale, but most solutions have serious drawbacks
                    self.mutatedimage = pygame.transform.scale(self.targimage, (self.targimage.get_width()*2,self.targimage.get_height()*2) )
                    self.mutatedimage = colorShift(self.mutatedimage , (100,100,100)) 
                self.image.blit(self.mutatedimage,(self.rect.width/2,self.height/2))
            
            self.texts.append(self.font.render(name , True, self.color))
            self.texts.append(self.font.render(distance , True, self.color))
            self.texts.append(self.font.render("speed: " + makeKMs(self.targ) + "Km/s" , True, self.color))
            for text in self.texts:
                self.image.blit(text, (0,self.texts.index(text)*15))
        surface.blit(self.image, (self.rect.x,self.rect.y))



class shipDamage(Drawable):

    def __init__(self, universe, font):
        Drawable.__init__(self, universe)
        # self.game = game
        self.player = self.universe.game.player
        self.totalhealth = 0
        self.font = font
        self.shownparts = []
        self.rect = col12row9(self.universe.game,9,4,3,3)
        # self.width = int(self.universe.game.width / 5)
        # self.height = int(self.universe.game.height/ 4 )
        self.image = pygame.Surface((self.rect.width,self.rect.height))
        self.image.set_alpha(200)
    
    def update(self):
        totalhealth = sum(c.hp for c in self.player.parts)
        if totalhealth != self.totalhealth:
            totalhealth = self.totalhealth
            self.active = True
            self.shownparts = sorted(self.player.parts, key=lambda part: part.hp / part.maxhp)
            self.shownparts = self.shownparts[:6]
        else:
            self.active = False


    def draw(self,surface):
        
        if self.active:
            self.startrect = Rect(10, 0, 150, 5)
            self.image.fill(SHIPDAMAGE)
            for part in self.shownparts:
                partfactor = part.hp / part.maxhp 
                
                if partfactor >= 0 and partfactor <= 1:
                    self.startrect[2] = partfactor * 150
                    self.startrect[1] += 30
                    color = (int((1-partfactor) * 255) , int(partfactor * 255), 50)
                    
                    pygame.draw.rect(self.image, color, self.startrect)
                    text = self.font.render(part.name + " " + str(round(part.hp,1)) + "/" + str(part.maxhp), False, HUD3)
                    self.image.blit(text, (10, self.startrect[1]-15))
            
            

        surface.blit(self.image, (self.rect.x, self.rect.y))
                

