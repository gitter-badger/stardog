#dialogs.py
from collections import deque

from utils import *
from menuElements import *
from spaceship import Ship
from planet import *


class Messenger(Drawable):
	queue = deque() #not capitalized in stand lib
	speed = 40 #characters per second
	messageDelay = 9 #seconds after each message
	maxChars = 250 #line width
	font = FONT
	topleft = 2,2
	maxMessages = 8
	def __init__(self, game, font = FONT, dir = 1):
		Drawable.__init__(self, game)
		self.dir = dir# -1 means the messages stack upward.
		# self.game = game
		self.image = pygame.Surface((game.width - 202, self.font.get_linesize()))
		self.image.set_alpha(200)
	
	def message(self, text, color = (250,250,250)):
		"""message(text,color) -> add a message to the Messenger."""
		text = '   ' + text
		if len(text) > self.maxChars: #line length limit
			self.message(text[:maxChars], color)
			self.message(text[maxChars:], color)
			return
		self.queue.append((self.font.render(text, True, color),
				self.game.timer + 1. * len(text) / self.speed + self.messageDelay))
		if soundModule:
			messageSound.play()
		
	def update(self):
		if self.queue and self.game.timer > self.queue[0][1] \
		or len(self.queue) > self.maxMessages:
			self.queue.popleft()
		
	def draw(self, surface):
		y = self.topleft[1]
		for message in self.queue:
			self.image.fill((0, 0, 80))
			self.image.blit(message[0], (0,0))
			surface.blit(self.image, (self.topleft[0], y))
			y += self.font.get_linesize() * self.dir
			
	def empty(self):
		self.queue = deque()
		
class Trigger(object):
	def __init__(self, game, conditions, actions, repeat = False):
		self.repeat = repeat
		if type(conditions) != type([]):
			conditions = [conditions]
		self. conditions = conditions
		if type(actions) != type([]):
			actions = [actions]
		self.actions = actions
		self.game = game
		
	def update(self):
		for condition in self.conditions:
			if not condition():
				return
		for action in self.actions:
			action()
		if not self.repeat:
			self.game.triggers.remove(self)
		
def timerCondition(game, time, relative = True):
	if relative:
		time = game.timer + time
	return lambda: game.timer >= time
	
def levelCondition(game, level):
	return lambda: game.player.level >= level
	
def planetCondition(game, planet):
	return lambda: game.player.landed == planet
	
def solarSystemCondition(game, solarSystem):
	return lambda: game.curSystem.name == solarSystem

def seePlanetCondition(game):
	def see():
		for radar in game.player.radars:
			for floater in radar.detected:
				if isinstance(floater,Planet) and not isinstance(floater,Sun):
					return True
		return False
	return see

def seeShipCondition(game):
	def see():
		for radar in game.player.radars:
			for floater in radar.detected:
				if isinstance(floater,Ship):
					return True
		return False
	return see

	
def messageAction(game, text, color = (200,200,100)):
	return lambda: game.messenger.message(text, color)

	

		
