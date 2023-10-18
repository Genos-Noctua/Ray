import pygame
import numpy as np
import threading

class ray:
    def __init__(self, win_size=False, fps=False, bg_color = pygame.color.THECOLORS['black'], caption = False):
        self.fps = fps
        self.caption = caption
        self.win_size = win_size
        self.bg_color = bg_color
        self.running = True
        self.res = dict()
        self.loop = threading.Thread(target=self.mainloop, args=())
        self.loop.daemon = True
        self.loop.start()
        
    def mainloop(self):
        pygame.init()
        self.win_size = (1280,800) if not self.win_size else(int(pygame.display.Info().current_w*self.win_size), int(pygame.display.Info().current_h*self.win_size))
        self.fps = self.fps if self.fps else 60
        self.caption = self.caption if self.caption else 'Ray GUI'
        self.clock = pygame.time.Clock()
        self.MAXW = pygame.display.Info().current_w
        self.MAXH = pygame.display.Info().current_h
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.win_size, pygame.RESIZABLE, vsync=1)

        while self.running:
            self.events()
            self.render(self.res)
            pygame.display.flip()
            self.clock.tick(self.fps)
            self.add_text(str(int(self.clock.get_fps())), (0.02,0.05),  pygame.color.THECOLORS['yellow'], 50, 'fps')
            
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.win_size = list(event.size)
                self.win_size[1] = self.win_size[0]//16*9
                self.screen = pygame.display.set_mode(self.win_size, pygame.RESIZABLE, vsync=1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def add_text(self, text, pos, color, size, label):
        self.res[label] = {'type':'text', 'pos':pos, 'text':text, 'color':color, 'size': size}
    
    def add_image(self, image, pos, scale, label):
        self.res[label] = {'type':'image', 'image':image, 'pos':pos, 'scale':scale}

    def add_array(self, array, pos, scale, label):
        self.res[label] = {'type':'array', 'array':array, 'pos':pos, 'scale':scale}

    def add_color(self, color, pos, size, label):
        self.res[label] = {'type':'color', 'size':size, 'pos':pos, 'color':color}

    def set_text(self, object):
        font = pygame.font.SysFont('consola.ttf', int(object['size']*(self.win_size[0]/self.MAXW)))
        img = font.render(object['text'], True, object['color'])
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        self.screen.blit(img, rect)

    def set_image(self, object):
        img = pygame.image.load(object['image']).convert()
        img = pygame.transform.scale(img, (object['scale']*img.get_size()[0]*(self.win_size[0]/self.MAXW), object['scale']*img.get_size()[1]*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        self.screen.blit(img, rect)

    def set_array(self, object):
        array = object['array']
        if array.ndim == 2:
            array = np.repeat(array, 3).reshape(array.shape[0], array.shape[1], 3)
            img = pygame.surfarray.make_surface(array)
            img = pygame.transform.scale(img, (object['scale']*100*(self.win_size[0]/self.MAXW), object['scale']*100*(self.win_size[1]/self.MAXH)))
        elif array.ndim == 3:
            img = pygame.surfarray.make_surface(array)
            img = pygame.transform.scale(img, (object['scale']*100*(self.win_size[0]/self.MAXW), object['scale']*100*(self.win_size[1]/self.MAXH)))
        rect = img.get_rect()
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        self.screen.blit(img, rect)
    
    def set_color(self, object):
        rect = pygame.Surface((0, 0)).get_rect()
        rect.width, rect.height = int(object['size'][0]*self.win_size[0]), int(object['size'][1]*self.win_size[1])
        rect.center = int(object['pos'][0]*self.win_size[0]), int(object['pos'][1]*self.win_size[1])
        pygame.draw.rect(self.screen, object['color'], rect)

    def render(self, objects):
        self.screen.fill(self.bg_color)
        for key in objects.keys():
            if objects[key]['type'] == 'text':
                self.set_text(objects[key])
            elif objects[key]['type'] == 'image':
                self.set_image(objects[key])
            elif objects[key]['type'] == 'array':
                self.set_array(objects[key])
            elif objects[key]['type'] == 'color':
                self.set_color(objects[key])

'''
    display = ray(bg_color=pygame.color.THECOLORS['lightskyblue'], win_size=0.3)
    display.add_image('lol.jpg', (0.2,0.2), 2.0, 'image')
    display.add_array(array, (0.8,0.2), 2.0, 'array')
    display.add_color(color, (0.2,0.8), (0.1,0.1), 'color')
    display.add_text(str(x), (0.8,0.8),  color, 200, 'text')
    display.add_text('Changed', (0.8,0.8),  color, 200, 'text')
    display.add_text('Work hard', (0.5,0.5),  pygame.color.THECOLORS['white'], 500, 'header')
    display.res['text']['text'] = 'changed again'
'''