import random
import config
import pyglet

def random_bg():
	return random.choice([Sand, Jungle, Sea])

class Grid(object):
	def __init__(self, w, h):
		self.grid = [[ None for x in xrange(w)] for y in xrange(h)]
		self.random_populate()
		self.w=w
		self.h=h
		print self.h, self.w

	def random_populate(self):
		for y, row in enumerate(self.grid):
			for x, col in enumerate(row):
				r_x, r_y = x * config.CELL_SIZE, y * config.CELL_SIZE
				self.grid[y][x] =Sand(r_x, r_y)

	def draw_background(self):
		for row in self.grid:
			for cell in row:
				cell.background.draw()

	def close_elements_of_element(self, element):
		close_elements = []
		start_pos_x = element.x//config.CELL_SIZE - 1
		start_pos_y = element.y//config.CELL_SIZE - 1

		#bottom line
		if start_pos_y >= 0:
			for i in range (element.w + 1):
				if start_pos_x >= 0 and self.grid[start_pos_y][start_pos_x + i].element:
					close_elements.append(self.grid[start_pos_y][start_pos_x + i].element)

		#top line
		if start_pos_y >= 0:
			for i in range (element.w + 1):
				if self.grid[start_pos_y][start_pos_x + i].element:
					close_elements.append(self.grid[start_pos_y][start_pos_x + i].element)

	def draw_foreground(self):
		for row in self.grid:
			for cell in row:
				cell.foreground.draw()


class Cell(object):
	def __init__(self,x,y, element=None):
		self.element = element
		image_population = [image for (image, weight) in self.images for i in xrange(weight)]
		self.background = pyglet.sprite.Sprite(random.choice(image_population), x, y)
		self.foreground= None
		
	# def draw(self):
	# 	self.background.draw()
	# 	if self.element:
	# 		self.element.draw()
	# 	if self.foreground:
	# 		self.foreground.draw()

class Sand(Cell):

	images = [(pyglet.image.load('images/background/sand{}.png'.format(i)), weight)
	          for (i, weight) in [(1, 90), (2, 10), (3,10), (4, 2), (5,2), (6,2)] ]

	def __init__(self, *args, **kwargs):
		self.images = Sand.images
		super(Sand, self).__init__(*args, **kwargs)


class Jungle(Cell):

	images = [pyglet.image.load('images/background/{}.png'.format(pos)) for pos in ['jungle1', 'jungle2', 'jungle3']]

	def __init__(self, *args, **kwargs):
		self.images = Jungle.images
		super(Jungle, self).__init__(*args, **kwargs)

class Sea(Cell):
	
	images = [pyglet.image.load('images/background/{}.png'.format(pos)) for pos in ['sea1', 'sea2', 'sea3']]

	def __init__(self, *args, **kwargs):
		self.images = Sea.images
		super(Sea, self).__init__(*args, **kwargs)

if __name__ == '__main__':

	# drawing test
	window = pyglet.window.Window()
	@window.event
	def on_draw():
			window.clear()
			sandBack = Sand(x=window.width//4, y=window.height//4)
			# seaBack = Sea(x=window.width//4, y=window.height//4)
			# jungleBack = Jungle(x=window.width//4, y=window.height//4)

			sandBack.draw()
			# seaBack.draw()
			# jungleBack.draw()

	pyglet.app.run()
