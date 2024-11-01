#Ray GUI v1.991
import pygame, time, threading, matplotlib.pyplot as plt
from PIL import Image
import numpy as np

class ray:
    # constructor
    colors = pygame.color.THECOLORS
    def __init__(self, win_scale=0.9, fps=60, fps_style = 0, plot_smooth = 0, bg_color = pygame.color.THECOLORS['black'], caption = 'Ray GUI', optimisations = True):
        self.fps = fps
        self.fps_style = fps_style
        self.caption = caption
        self.win_scale = win_scale
        self.bg_color = bg_color
        self.plot_smooth = plot_smooth
        self.optimisations = optimisations
        self.fullscreen = False
        self.edited = True
        self.locked = False
        self.running = True
        self.res = dict()
        self.loop = threading.Thread(target=self.mainloop, args=())
        self.loop.daemon = True
        self.loop.start()

    def smooth_array(self, arr, window_size):
        return np.convolve(arr, np.ones(window_size) / window_size, mode='valid')

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
            if not pygame.display.get_active(): 
                time.sleep(1)
                continue
            if self.fps_style == 2: self.add_text(str(int(self.clock.get_fps())), (0.02,0.05),  pygame.color.THECOLORS['yellow'], 50, 'fps')
            if self.fps_style == 1: pygame.display.set_caption(f'FPS: {int(self.clock.get_fps())}')
            if not self.locked: 
                self.render(self.res)
                pygame.display.flip()
                self.clock.tick(self.fps)

    # event handler
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.edited = True
                self.win_size = list(event.size)
                try:
                    for key in self.res.keys():
                        if 'cache' in self.res[key].keys():
                            del self.res[key]['cache']
                except: pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(self.prev, pygame.RESIZABLE, vsync=1)
                        self.fullscreen = False
                    else:
                        my_event = pygame.event.EventType(pygame.VIDEORESIZE)
                        my_event.size = (self.MAXW, self.MAXH)
                        self.prev = self.win_size
                        self.screen = pygame.display.set_mode((self.MAXW, self.MAXH), pygame.FULLSCREEN, vsync=1)
                        pygame.event.post(my_event)
                        self.fullscreen = True

    def wait(self):
        while self.running:
            time.sleep(1)

    # render all elements
    def render(self, objects):
        def switch(objects, key):
            if objects[key]['type'] == 'text':
                self.render_text(objects[key])
            elif objects[key]['type'] == 'image':
                self.render_image(objects[key])
            elif objects[key]['type'] == 'array':
                self.render_array(objects[key])
            elif objects[key]['type'] == 'color':
                self.render_color(objects[key])
            elif objects[key]['type'] == 'plot':
                self.render_plot(objects[key])
        
        done = not self.edited if self.optimisations else False
        while not done:
            try:
                self.screen.fill(self.bg_color)
                for key in (set(objects.keys()) - set(['fps']) - set(map(str, list(range(1000))))):
                    switch(objects, key)
                if 'fps' in set(objects.keys()): self.render_text(objects['fps'])
                id = 1
                while str(id) in list(objects.keys()):
                    switch(objects, str(id))
                    id += 1
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

    def add_plot(self, plot, pos, scale, smooth, label):
        self.edited = True
        self.res[label] = {'type':'plot', 'plot':plot, 'pos':pos, 'smooth':smooth, 'scale':scale}
    # </>

    # updating the parameters of an existing element
    def put(self, element, label):
        self.edited = True
        if label in self.res.keys(): 
            if 'cache' in self.res[label].keys(): del self.res[label]['cache']
            self.res[label][self.res[label]['type']] = element

    # <putting an existing element on the screen>
    def render_text(self, object):
        if 'cache' in list(object.keys()) and self.optimisations:
            self.screen.blit(*object['cache'])
            return
        font = pygame.font.SysFont('consola.ttf', int(object['size']*(self.win_size[0]/self.MAXW)))
        img = font.render(object['text'], True, object['color'])
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (img, rect)
        self.screen.blit(img, rect)

    def render_image(self, object):
        if 'cache' in list(object.keys()) and self.optimisations:
            self.screen.blit(*object['cache'])
            return
        img = pygame.image.load(object['image']).convert()
        img = pygame.transform.scale(img, (object['scale']*img.get_size()[0]*(self.win_size[0]/self.MAXW), object['scale']*img.get_size()[1]*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (img, rect)
        self.screen.blit(img, rect)

    def render_array(self, object):
        if 'cache' in list(object.keys()) and self.optimisations:
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
        if 'cache' in list(object.keys()) and self.optimisations:
            pygame.draw.rect(*object['cache'])
            return
        rect = pygame.Surface((0, 0)).get_rect()
        rect.width, rect.height = int(object['size'][0]*self.win_size[0]), int(object['size'][1]*self.win_size[1])
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        object['cache'] = (self.screen, object['color'], rect)
        pygame.draw.rect(self.screen, object['color'], rect)
    
    def render_plot(self, object):
        if 'cache' in list(object.keys()) and self.optimisations:
            self.screen.blit(*object['cache'])
            return
        if 'plots' in list(object.keys()):
            fig, ax = object['plots']
        else: fig, ax = plt.subplots()
        fig.set_size_inches(16/2,9/2)
        if object['smooth'] != 0: 
            ax.plot(self.smooth_array(object['plot'], object['smooth']))
        else: ax.plot(object['plot'])
        fig.canvas.draw()
        width, height = fig.get_size_inches() * fig.get_dpi()
        array = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8').reshape(int(height), int(width), 3)
        array = np.array(Image.fromarray(array).transpose(5))
        img = pygame.surfarray.make_surface(array)
        img = pygame.transform.scale(img, (object['scale']/100*array.shape[0]*(self.win_size[0]/self.MAXW), object['scale']/100*array.shape[1]*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        ax.clear()
        object['cache'] = (img, rect)        
        object['plots'] = fig, ax
        self.screen.blit(img, rect)
    # </>
