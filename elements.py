#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyglet
from state import Idle, Moving, Attacking,Dying
import config
from math import cos 

from math import radians, atan2

class Element(object):
    """ Main class of elements on board """
    def __init__(self, game, x, y, w=1, h=1):
        super(Element, self).__init__()
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.game = game
        
        self._state = Idle(self)

        self.last_state = Idle(self)

        self.cur_image = self.images[Idle][0][0]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.last_state = self._state
        self._state = value

    def update(self, dt):
        self.state.update(dt)

    def center(self):
        center = (self.x + self.w*config.CELL_SIZE/2 , self.y + self.h*config.CELL_SIZE/2)
        return center

    def diff_angle(self, element):
        e_x, e_y = element.center()
        return atan2(e_y - self.y , e_x -self.x)

    def draw(self):
        sprite = pyglet.sprite.Sprite(self.cur_image, self.x, self.y)
        sprite.draw()

    def interact(self, character):
        pass

    def collision(self):
        self.state = Idle(self)

    def cells(self):
        cell_x = int(self.x // config.CELL_SIZE)
        cell_y = int(self.y // config.CELL_SIZE)

        return [(cell_x + i, cell_y + j) for i in xrange(self.w) for j in xrange(self.h)
                if 0 <= cell_x + i < self.game.grid.w and 0 <= cell_y + j < self.game.grid.h ]

    def is_collidable(self):
        return True

    def die(self):
        self.state = Dying(self)


#SubClass
class Creature(Element):

    def __init__(self, *args, **kwargs):
        super(Creature, self).__init__(*args, **kwargs)
        self.total_hp = self.hp = 10
        self.target = None
        self.angle = 0.0
        self.speed = 500

    def attack_finished(self):
        for n in self.game.grid.neighbours(self):
            if not self.attackable(n) or n.hp < 0:
                continue
            self.attack(n)

        self.state = Idle(self)

    def started_attack(self):
    	pass

    def attackable(self, e):
        return isinstance(e, Creature)

    def attack(self, element):
        element.hp -= self.att
        if element.hp <= 0:
            element.die()

    def draw(self):
        super(Creature, self).draw()
        if 0 <= self.hp < self.total_hp:
            hp_txt = '{}/{}'.format(self.hp, self.total_hp)
            hp_label = pyglet.text.Label(hp_txt, x=self.x + config.CELL_SIZE, y=self.y + 2 * config.CELL_SIZE,
                                         font_name="Ubuntu", bold=True)
            hp_label.color = (111, 80, 64, 255)
            hp_label.draw()


class StillObject(Element):
    def __init__(self, *args, **kwargs):
        super(StillObject, self).__init__(*args, **kwargs)

#SubSubClass
class Character(Creature):

    images = {
        Idle: [
        [pyglet.image.load('images/char/idle/0_{}.png'.format(pos)) for pos in ['right', 'top', 'left', 'bottom']]
        ],
        Moving : [
        [pyglet.image.load('images/char/moving/{}_{}.png'.format(f,p)) for p in ['right', 'top', 'left', 'bottom']] for f in range(4) 
        ],
        Dying : [
        [pyglet.image.load('images/char/dying/0_{}.png'.format(p)) for p in ['death']]
        ],
        Attacking : [
        [pyglet.image.load('images/char/attacking/{}_{}.png'.format(f,p)) for p in ['right', 'top', 'left', 'bottom']] for f in range(4) 
        ]
         }

    def __init__(self, *args, **kwargs):

        self.images = Character.images
        super(Character, self).__init__(*args, w=1, h=2, **kwargs)

        self.total_hp = self.hp = 20
        self.att = 5

        self.lvl = 1        
        self.xp = 0        

        self.soundAttack = pyglet.resource.media('sound/attack.mp3',streaming = False)


    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, value):
        self._xp = value

        if self.xp >= 100:
            self.lvl += 1
            self._xp = self.xp - 100

        
    @property
    def lvl(self):
        return self._lvl

    @lvl.setter
    def lvl(self, value):
        
        self.total_hp = int(self.total_hp * 1.2)
        self.hp = self.total_hp

        self.att = int(self.att * 1.3)

        if value == 2:
            if self.game.castle in self.game.elements:
                self.game.elements.remove(self.game.castle)
            self.game.castle = CastleLvl2(self.game,(self.game.width)/2-(1.5*config.CELL_SIZE), (self.game.height)/2, 2,2)
            self.game.elements.append(self.game.castle)
        elif value == 3:
            if self.game.castle in self.game.elements:
                self.game.elements.remove(self.game.castle)
            self.game.castle = CastleLvl3(self.game,(self.game.width)/2-(1.5*config.CELL_SIZE), (self.game.height)/2, 2,2)
            self.game.elements.append(self.game.castle)

        self._lvl=value

    def started_attack(self):
    	super(Character,self).started_attack()
    	self.soundAttack.play()


    def attackable(self, e):
        return isinstance(e, Monster)

    def die(self):
        super(Character, self).die()
        self.game.game_over = True

class Castle(Creature):

    def __init__(self, *args, **kwargs):
        self.att = 5
        self.total_hp = self.hp = 100
        super(Castle, self).__init__(*args, **kwargs)

    def interact(self, character):
        self.game.launch_crafting()

    def die(self):
        super(Castle, self).die()
        self.game.game_over = True

class CastleLvl1(Castle):
    images = {
        Idle: [
        [pyglet.image.load('images/castle/idle/etat0.png')]
        ],
        Dying : [
        [pyglet.image.load('images/castle/dying/château1_{}.png'.format(p))] for p in xrange(4)
        ],
     }

    def __init__(self, *args, **kwargs):
        self.images = CastleLvl1.images
        super(CastleLvl1, self).__init__(*args, **kwargs)
        self.total_hp = self.hp = 120

class CastleLvl2(Castle):
    images = {
            Idle: [
            [pyglet.image.load('images/castle/idle/etat1.png')]
            ],
            Dying : [
            [pyglet.image.load('images/castle/dying/château2_{}.png'.format(p))]  for p in xrange(4)
            ]
     }
    def __init__(self, *args, **kwargs):
        self.images = CastleLvl2.images
        super(CastleLvl2, self).__init__(*args, **kwargs)
        self.total_hp = self.hp = 250

class CastleLvl3(Castle):
    images = {
        Idle: [
        [pyglet.image.load('images/castle/idle/etat2.png')]
        ],
        Dying : [
        [pyglet.image.load('images/castle/dying/château3_{}.png'.format(p))] for p in xrange(4)
        ],
         }

    def __init__(self, *args, **kwargs):
        self.images = CastleLvl3.images
        self.total_hp = self.hp = 400
        super(CastleLvl3, self).__init__(*args, **kwargs)

class Monster(Creature):
    images = None

    def __init__(self, *args, **kwargs):
        
        self.hp = 30
        self.att = 2

        super(Monster, self).__init__(*args, **kwargs)
        self.speed = 50


    def attack_finished(self):
        super(Monster, self).attack_finished()

        for n in self.game.grid.neighbours(self):
            if issubclass(n.__class__, Creature):
                self.state = Attacking(self)
                return

        self.state = Moving(self, self.getAngle())

    def getAngle(self):
        c_x, c_y = self.game.castle.x, self.game.castle.y
        offset = atan2(c_y - self.y , c_x -self.x)
        return offset


    def attackable(self, e):
        return isinstance(e, Character) or isinstance(e, Castle)

    def collision(self):
        neighbours = self.game.grid.neighbours(self)
        for n in neighbours:
            if isinstance(n, Castle) or isinstance(n, Character):
                self.state = Attacking(self)
                return

class SeaMonster(Monster):
    images = {

            Idle: [
            [pyglet.image.load('images/monster/seamonster/idle/0_right.png')]
            ],
            Moving : [
            [pyglet.image.load('images/monster/seamonster/moving/{}_right.png'.format(f))] for f in range(4) 
            ],
            Attacking : [
            [pyglet.image.load('images/monster/seamonster/attacking/{}_{}.png'.format(f,p)) for p in ['right']] for f in range(4) 
            ],
            Dying : [
            [pyglet.image.load('images/monster/seamonster/dying/0_{}.png'.format(p)) for p in ['death']]
            ],
            
             }

    def __init__(self, *args, **kwargs):
        self.images = SeaMonster.images
        super(SeaMonster,self).__init__(*args,**kwargs)
       
        self.soundAttack = pyglet.resource.media('sound/shark_niak.mp3',streaming = False)
        self.soudPop = pyglet.resource.media('sound/shark_shout.mp3',streaming = False)
        self.soudPop.play()

    def started_attack(self):
    	super(SeaMonster,self).started_attack()
    	self.soundAttack.play()


    def die(self):
        super(SeaMonster, self).die()
        self.game.shark_teeth += 1
        self.game.score += 200
        self.game.character.xp+=10

class JungleMonster(Monster):
    images = {

            Idle: [
            [pyglet.image.load('images/monster/junglemonster/idle/0_left.png')]
            ],
            Moving : [
            [pyglet.image.load('images/monster/junglemonster/moving/{}_left.png'.format(f))] for f in range(4) 
            ],
            Attacking : [
            [pyglet.image.load('images/monster/junglemonster/attacking/{}_{}.png'.format(f,p)) for p in ['left']] for f in range(4) 
            ],
            Dying : [
            [pyglet.image.load('images/monster/junglemonster/dying/0_{}.png'.format(p)) for p in ['death']]
            ],
            
             }

    def __init__(self, *args, **kwargs):
        self.images = JungleMonster.images
        super(JungleMonster,self).__init__(*args,**kwargs)
    	self.soundAttack = pyglet.resource.media('sound/bear_chomp.mp3',streaming = False)
        self.soudPop = pyglet.resource.media('sound/bear_shout.mp3',streaming = False)
        self.soudPop.play()
    
    def started_attack(self):
    	super(JungleMonster,self).started_attack()
    	self.soundAttack.play()
    
    def die(self):
        super(JungleMonster, self).die()
        self.game.bear_pelt += 1
        self.game.score += 200
        self.game.character.xp+=10

class Chest(StillObject):
    images = {

            Idle: [
                [pyglet.image.load('images/chest/idle/chest_idle.png')]
            ],
            Dying: [
                [pyglet.image.load('images/chest/idle/chest_idle.png')]
            ]
            }

    def __init__(self, *args, **kwargs):
        self.images = Chest.images
        super(Chest, self).__init__(*args, **kwargs)
        self.angle = 0.0
    
    def interact(self, character):
        character.game.ruby += 1
        self.die()

class Projectile(Creature):
    images = {

            Idle: [
            [pyglet.image.load('images/projectile/idle/bomb.png')]
            ],
            Moving: [
            [pyglet.image.load('images/projectile/idle/bomb.png')]
            ],
            Dying: [
            [pyglet.image.load('images/projectile/explosion/explosion{}.png'.format(i))
             for i in xrange(1, 5)]
            ]
    }

    def __init__(self, *args, **kwargs):
        self.images = Projectile.images
        super(Projectile, self).__init__(*args, **kwargs)

        self.att = 5

    def shoot(self, target):
        angle = self.diff_angle(target)
        self.state = Moving(self, angle)

    def collision(self):
        for n in self.game.grid.neighbours(self):
            if isinstance(n, Monster):
                self.attack(n)
                self.state = Dying(self)
    
    def is_collidable(self):
        return False


class Foam(StillObject):
    images = {

            Idle: [
            [pyglet.image.load('images/foam/idle/idle.png')]
            ]
             }

    def __init__(self, *args, **kwargs):
        self.images = Foam.images
        super(Foam, self).__init__(*args, **kwargs)
        self.angle = 0.0
        self.x0 = self.x
        self.tick=0


    def update(self, dt):
        super(Foam,self).update(dt)
        self.tick += 1
        dx = (cos(self.tick/25.0)*config.CELL_SIZE/4-config.CELL_SIZE/4)*0.3
        self.x = self.x0 - dx
        
class Forest(StillObject):
    images = {

            Idle: [
            [pyglet.image.load('images/forest/idle/0_idle.png')]
            ]
             }

    def __init__(self, *args, **kwargs):
        self.images = Forest.images
        super(Forest, self).__init__(*args, **kwargs)
if __name__ == '__main__':
    pass
