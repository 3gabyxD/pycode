import pygame
import json
from os import listdir
from os.path import isfile, join
import time

from pygame.draw import lines

# Config
config_file = open('config/config.json', 'r')
config = json.load(config_file)
config_file.close()

# Lint
lints_dir = 'lints'
lints_files = [f for f in listdir(lints_dir) if isfile(join(lints_dir, f))]
lints = {}
for file in lints_files:
	lints[file[:-5]] = json.load(
		open(lints_dir + '/' + file)
	)

print(lints)
#-----------------------------#

# Init
width, height = 640, 480

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
clock = pygame.time.Clock()

#-----------------------------#

# Theme
class Theme:
	font_size = 20
	bg = pygame.Color(config["theme"]["bg"])
	fg = pygame.Color(config["theme"]["fg"])
	dm = pygame.Color(config["theme"]["dm"])
	hl = pygame.Color(config["theme"]["hl"])

	scroll_speed = config["anim"]["scroll"]
	pointer_speed = config["anim"]["pointer"]

# Font
class Font:
	# sans_config = config["font"]["sans"]
	regular = pygame.font.Font(
		"fonts/FiraCode-Regular.ttf",
		Theme.font_size # sans_config[0], sans_config[1]
	)

class Lint:
	pass

#-----------------------------#

# UI Elements
class Button:
	"""Button Class"""
	def __init__(self, pos, size, text="button", padding=[0, 0, 0, 0], border=[0, 0, 0, 0]):
		"""
		### Parameters
		- pos : tuple, list
		- size : tuple, list
		- padding : tuple, list, optional
		- border : tuple, list, optional
		- text: str, optional
		"""
		self.pos = pos
		self.size = size
		self.padding = padding
		self.border = border

	def draw(self, surface):
		surface.fill(
			Theme.fg, pygame.Rect(
				self.pos[0], self.pos[1],
				self.size[0], self.size[1]))

class Taskbar:
	def __init__(self, buttons):
		self.width = width
		self.height = Theme.font_size * 1.5
		self.buttons = buttons

	def draw(self, surface):
		surface.fill(
			Theme.bg, pygame.Rect(0, 0, self.width, self.height))

		for button in self.buttons:
			button.draw(surface)

class Editor:

	bar_width = 30
	def __init__(self, lint, text=""):
		self.text = text
		self.pointer = len(text)
		self.x = 0

		self.scroll_from = 0
		self.scroll_start = 0

		self.pointer_from = self.pointer
		self.pointer_start = 0

		self.lines = self.text.split('\n')

		self.lint = lint
		self.t = 0

	def move_to(self, dest):
		pointer_t = max(0, min((time.time() - self.pointer_start) / Theme.pointer_speed, 1))
		# if pointer_t >= 1:
		self.pointer_from = self.pointer
		self.pointer_start = time.time()
		self.pointer = max(0, min(dest, len(self.text)))

	def go_up(self):

		i = 0
		t = 0
		for line in self.lines:
			current_len = len(line)
			print((t <= self.pointer) and (self.pointer <= t + current_len))
			if (t <= self.pointer) and (self.pointer <= t + current_len):
				print("FOUND LINE")
				if 0 < i:
					print("LINE VISIBLE")
					dist_in_line = self.pointer - t
					last = self.lines[i - 1]
					self.move_to(
						self.pointer - dist_in_line
					)
				break
			t += current_len
			i += 1


	def go_down(self):
		pass

	def move(self, delta):
		self.move_to(self.pointer + delta)

	def backspace(self, mod):
		if len(self.text) > 0:
			first = self.text[0:self.pointer]
			last = self.text[self.pointer:len(self.text)]
			self.text = first[0:-1] + last
			self.move(-1)
			self.lines = self.text.split('\n')

	def type(self, unicode):
		first = self.text[0:self.pointer]
		last = self.text[self.pointer:len(self.text)]
		self.text = first + unicode + last
		self.move(len(unicode))
		self.lines = self.text.split('\n')

	def scroll_to(self, dest):
		scroll_t = max(0, min((time.time() - self.scroll_start) / Theme.scroll_speed, 1))

		self.scroll_start = time.time()
		scroll = self.scroll_from + (self.x - self.scroll_from) * scroll_t
		self.scroll_from = scroll
		
		self.x = max(-len(self.lines), min(dest, 0))

	def scroll(self, delta):
		self.scroll_to(self.x + delta)

	def draw(self, surface):

		scroll_t = max(0, min((time.time() - self.scroll_start) / Theme.scroll_speed, 1))
		scroll = self.scroll_from + (self.x - self.scroll_from) * scroll_t

		pointer_t = max(0, min((time.time() - self.pointer_start) / Theme.pointer_speed, 1))

		space_width = Font.regular.size(" ")[0]

		# Line numbers
		i = 1
		l = 1
		for line in self.lines:
			line_number = Font.regular.render(
				str(i),
				True,
				Theme.dm
			)
			line_number_width = line_number.get_width()
			surface.blit(
				line_number,
				[self.bar_width - line_number_width, Theme.font_size * 1.5 + (i + scroll) * Theme.font_size]
			)

			current_x = 0
			for word in line.split(' '):
				for tab in word:
					if tab == '\t':
						text_render = Font.regular.render(
							'|   ',
							True,
							Theme.dm
						)
						text_pos = [current_x + Theme.font_size * .3 + self.bar_width, Theme.font_size * 1.5 + (i + scroll) * Theme.font_size]
						surface.blit(
							text_render,
							text_pos
						)
						current_x += text_render.get_width()

				word = word.replace('\t', '')
				try:
					col = self.lint[word]
				except:
					col = Theme.fg
				text_render = Font.regular.render(
					word,
					True,
					col
				)
				text_pos = [current_x + Theme.font_size * .3 + self.bar_width, Theme.font_size * 1.5 + (i + scroll) * Theme.font_size]
				surface.blit(
					text_render,
					text_pos
				)
				current_x += text_render.get_width() + space_width

			i += 1

		t = 0
		x = 0
		y = 1
		word_start = ''

		

		for w in self.text:
			if w == '\t':
				x += 4
				word_start = word_start + '|   '
			elif w == '\n':
				x = 0
				word_start = ''
				y += 1
			else:
				word_start = word_start + w
				x += 1
			if t == self.pointer_from - 1:
				p_from = pygame.Rect(
					Theme.font_size * .3 + self.bar_width + Font.regular.size(word_start)[0],
					(y + scroll) * Theme.font_size + Theme.font_size * 1.5, 1, Theme.font_size
				)
			if t == self.pointer - 1:
				p_to = pygame.Rect(
					Theme.font_size * .3 + self.bar_width + Font.regular.size(word_start)[0],
					(y + scroll) * Theme.font_size + Theme.font_size * 1.5, 1, Theme.font_size
				)
			t += 1
		
		if pointer_t >= 1:
			surface.fill(
				Theme.fg,
				p_to
			)
		elif pointer_t <= 0:
			try:
				surface.fill(
					Theme.fg,
					p_from
				)
			except:
				pass
		else:
			try:
				from_x = p_from.x
				from_y = p_from.y

				to_x = p_to.x
				to_y = p_to.y

				p_rect = pygame.Rect(
					from_x + (to_x - from_x) * pointer_t,
					from_y + (to_y - from_y) * pointer_t,
					1, Theme.font_size
				)
				surface.fill(
					Theme.fg, p_rect
				)
			except:
				from_x = p_to.x + space_width
				from_y = p_to.y

				to_x = p_to.x
				to_y = p_to.y

				p_rect = pygame.Rect(
					from_x + (to_x - from_x) * pointer_t,
					from_y + (to_y - from_y) * pointer_t,
					1, Theme.font_size
				)
				surface.fill(
					Theme.fg, p_rect
				)
		
#-----------------------------#

# Main loop

taskbar = Taskbar([
	Button(
		pos=[0, 0],
		size=[70, Theme.font_size * 1.5],
		text="File",
		padding=[2, 2, 2, 2],
		border=[0, 0, 0, 0])
])

file_name = "amongus.lua"
file_r = open(file_name, "r")
editor = Editor(
	lint=lints['lua'],
	text=file_r.read()
)
file_r.close()

running = True
while running:

	delta = clock.tick()
	
	# Poll Events
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				file = open(file_name, "w")
				file.write(editor.text)
				file.close()
				running = False
			elif event.key == pygame.K_BACKSPACE:
				if len(editor.text)>0:
					if pygame.key.get_mods() & pygame.KMOD_CTRL:
						editor.text = editor.text.rsplit(None, 1)[0]
					else:
						editor.backspace(False)
			elif event.key == pygame.K_RETURN:
				try:
					tabs = editor.text.rsplit('\n', 1)[1].count('\t')
				except:
					tabs = 0
				editor.type("\n" + ('\t' * tabs))
			elif event.key == pygame.K_s:
				if pygame.key.get_mods() & pygame.KMOD_CTRL:
					file = open(file_name, "w")
					file.write(editor.text)
					file.close()
				else:
					editor.type(event.unicode)

			elif event.key == pygame.K_LEFT:
				editor.move(-1)

			elif event.key == pygame.K_RIGHT:
				editor.move(1)

			elif event.key == pygame.K_UP:
				editor.go_up()

			else:
				editor.type(event.unicode)

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 4:
				editor.scroll(7 * delta*.1)
			elif event.button == 5:
				editor.scroll(-7 * delta*.1)
		elif event.type == pygame.QUIT:
			file = open(file_name, "w")
			file.write(editor.text)
			file.close()
			running = False

	# Drawing
	screen.fill(Theme.bg)
	# taskbar.draw(screen)
	editor.draw(screen)

	pygame.display.update()

#-----------------------------#