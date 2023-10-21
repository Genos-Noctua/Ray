#Ray GUI v1.5
import pygame, time, threading
import numpy as np

class ray:
    # constructor
    def __init__(self, win_scale=0.5, fps=60, fps_style = 0, bg_color = pygame.color.THECOLORS['black'], caption = 'Ray GUI'):
        self.colors = pygame.color.THECOLORS
        self.fps = fps
        self.fps_style = fps_style
        self.caption = caption
        self.win_scale = win_scale
        self.bg_color = bg_color
        self.edited = True
        self.locked = False
        self.running = True
        self.res = dict()
        self.loop = threading.Thread(target=self.mainloop, args=())
        self.loop.daemon = True
        self.loop.start()

    # preparations before loop
    def prepare(self):
        pygame.init()
        self.win_size = (int(pygame.display.Info().current_w*self.win_scale), int(pygame.display.Info().current_h*self.win_scale))
        del self.win_scale
        self.clock = pygame.time.Clock()
        self.MAXW = pygame.display.Info().current_w
        self.MAXH = pygame.display.Info().current_h
        if self.fps_style == 0: pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.win_size, pygame.RESIZABLE, vsync=1)

    # main loop
    def mainloop(self):
        self.prepare()
        while self.running:
            self.events()
            if self.fps_style == 2: self.add_text(str(int(self.clock.get_fps())), (0.02,0.05),  pygame.color.THECOLORS['yellow'], 50, 'fps')
            if self.fps_style == 1: pygame.display.set_caption(f'FPS: {int(self.clock.get_fps())}')
            if not self.locked or not self.hidden: 
                self.render(self.res)
                pygame.display.flip()
            self.clock.tick(self.fps)

    # event handler
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.win_size = list(event.size)
                self.win_size[1] = self.win_size[0]//16*9
                self.screen = pygame.display.set_mode(self.win_size, pygame.RESIZABLE, vsync=1)
                try:
                    for key in self.res.keys():
                        if 'cache' in self.res[key].keys(): del self.res[key]['cache']
                except: pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        if pygame.display.get_active():
            self.hidden = False
        else:
            self.hidden = True
            time.sleep(1)

    # render all elements
    def render(self, objects):
        done = not self.edited
        while not done:
            try:
                self.screen.fill(self.bg_color)
                for key in set(objects.keys()) - set(['fps']):
                    if objects[key]['type'] == 'text':
                        self.render_text(objects[key])
                    elif objects[key]['type'] == 'image':
                        self.render_image(objects[key])
                    elif objects[key]['type'] == 'array':
                        self.render_array(objects[key])
                    elif objects[key]['type'] == 'color':
                        self.render_color(objects[key])
                if 'fps' in set(objects.keys()): self.render_text(objects['fps'])
                done = True
            except: pass
        self.edited = False

    # deleting elements from the resource bank
    def delete(self, label):
        self.edited = True
        del self.res[label]

    # <adding a new element to the resource bank>
    def add_text(self, text, pos, color, size, label):
        self.edited = True
        self.res[label] = {'type':'text', 'pos':pos, 'text':text, 'color':color, 'size': size}

    def add_image(self, image, pos, scale, label):
        self.edited = True
        self.res[label] = {'type':'image', 'image':image, 'pos':pos, 'scale':scale}

    def add_array(self, array, pos, scale, label):
        self.edited = True
        self.res[label] = {'type':'array', 'array':array, 'pos':pos, 'scale':scale}

    def add_color(self, color, pos, size, label):
        self.edited = True
        self.res[label] = {'type':'color', 'size':size, 'pos':pos, 'color':color}
    # </>

    # <updating the parameters of an existing element>
    def set_text(self, text, label):
        self.edited = True
        if label in self.res.keys(): 
            if 'cache' in self.res[label].keys(): del self.res[label]['cache']
            self.res[label]['text'] = text

    def set_image(self, image, label):
        self.edited = True
        if label in self.res.keys():
            if 'cache' in self.res[label].keys(): del self.res[label]['cache']
            self.res[label]['image'] = image

    def set_array(self, array, label):
        self.edited = True
        if label in self.res.keys():
            if 'cache' in self.res[label].keys(): del self.res[label]['cache']
            self.res[label]['array'] = array

    def set_color(self, color, label):
        self.edited = True
        if label in self.res.keys(): 
            if 'cache' in self.res[label].keys(): del self.res[label]['cache']
            self.res[label]['color'] = color

    # </>

    # <putting an existing element on the screen>
    def render_text(self, object):
        if 'cache' in list(object.keys()):
            self.screen.blit(*object['cache'])
            return
        font = pygame.font.SysFont('consola.ttf', int(object['size']*(self.win_size[0]/self.MAXW)))
        img = font.render(object['text'], True, object['color'])
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (img, rect)
        self.screen.blit(img, rect)

    def render_image(self, object):
        if 'cache' in list(object.keys()):
            self.screen.blit(*object['cache'])
            return
        img = pygame.image.load(object['image']).convert()
        img = pygame.transform.scale(img, (object['scale']*img.get_size()[0]*(self.win_size[0]/self.MAXW), object['scale']*img.get_size()[1]*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (img, rect)
        self.screen.blit(img, rect)

    def render_array(self, object):
        if 'cache' in list(object.keys()):
            self.screen.blit(*object['cache'])
            return
        array = object['array']
        if array.ndim == 2:
            array = np.repeat(array, 3).reshape(array.shape[0], array.shape[1], 3)
        img = pygame.surfarray.make_surface(array)
        img = pygame.transform.scale(img, (object['scale']*array.shape[0]*(self.win_size[0]/self.MAXW), object['scale']*array.shape[1]*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (img, rect)
        self.screen.blit(img, rect)

    def render_color(self, object):
        if 'cache' in list(object.keys()):
            pygame.draw.rect(*object['cache'])
            return
        rect = pygame.Surface((0, 0)).get_rect()
        rect.width, rect.height = int(object['size'][0]*self.win_size[0]), int(object['size'][1]*self.win_size[1])
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (self.screen, object['color'], rect)
        pygame.draw.rect(self.screen, object['color'], rect)
    # </>
