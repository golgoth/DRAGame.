#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import cos, sin, ceil, pi

class State(object):
	"""docstring for State"""
	anim_delay = 0.1

	def __init__(self, element, anim_delay=anim_delay):
		self.t = 0
		self.element = element	
		self.anim_delay = anim_delay

	def update(self, dt):
		self.t += dt

		frame_id = int(self.t / self.anim_delay) % len(self.images)

		images_frame = self.images[frame_id]

		pos_angle = (self.element.angle + pi / 4 + 2 * pi) % (2 * pi)
		angle_fragment = int(len(images_frame) * (pos_angle / (2 * pi))) 

		self.element.cur_image = images_frame[angle_fragment]	

class Idle(State):
	"""docstring for Idle"""
	def __init__(self, element):
		super(Idle, self).__init__(element)
		self.images = self.element.images[Idle]


	def update(self, dt):
		super(Idle, self).update(dt)

class Moving(State):
	"""docstring for Moving"""

	def __init__(self, element, offset):
		super(Moving, self).__init__(element)
		self.offset = offset	
		self.images = self.element.images[Moving]

	def update(self, dt):
		super(Moving,self).update(dt)

		angle = self.offset
		distancePix = self.element.speed * dt

		l_x = self.element.x
		l_y = self.element.y

		self.element.x += distancePix * cos(angle)
		self.element.y += distancePix * sin(angle)

		# Checking if we got inside occupied cells
		game = self.element.game
		if any(game.grid.grid[y][x].element for x, y in self.element.cells()
			   if game.grid.grid[y][x].element and game.grid.grid[y][x].element != self.element):
			self.element.x, self.element.y = l_x, l_y
			self.element.collision()

	#def interact():
	#	print "interact"



	

class Attacking(State):
	"""docstring for Attacking"""
	def __init__(self, element,target,attack_speed=0.1):
		super(Attacking, self).__init__(element)
		self.attack_speed=attack_speed
		self.images = self.element.images[Attacking]
		self.target = target
		self.time_passed=0


	def update(self, dt):
		super(Attacking,self).update(dt)
		self.time_passed+=dt
		if self.t> self.attack_speed:
			self.element.attack(self.target)
			self.time_passed=0
		neighbours = self.element.game.grid.neighbours(self.element)

		if not self.target in neighbours:
			self.element.target_missed()



class Dying(State):
	"""docstring for Dying"""
	attack_speed=1
	def __init__(self, element, attack_speed=1):
		self.anim_delay=attack_speed
		super(Dying,self).__init__(element,attack_speed)
		self.images = self.element.images[Dying]


	def update(self,dt):
		super(Dying,self).update(dt)


#class Damaging(object):
#	"""docstring for Damaging"""
#	def __init__(self,element arg):
#		super(Damaging, self).__init__(element)
#		self.images = self.element.images[Damaging]
#
#	def update(self,dt):
#		super(Damaging,self).update(dt)

		