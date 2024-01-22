import pygame, sys, os, time, json, cProfile
from os import walk
from menus import PygameLogo
from settings import *

class Game:
    def __init__(self):
        pygame.init()
      
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((RES), pygame.FULLSCREEN|pygame.SCALED)
        self.font = pygame.font.Font(FONT, 9) #int(TILESIZE))
        self.ui_font = pygame.font.Font(FONT, 16) #int(TILESIZE)) 
        self.running = True
        
        # states
        self.stack = []
        self.load_states()

    def write_data(self):
        with open(f"save_file_{self.slot}", "w") as write_save_file:
            json.dump(COMMIT_SAVE_DATA, write_save_file)

    def read_data(self):
        with open(f"save_file_{self.slot}", 'r') as read_save_file:
            save_json = json.load(read_save_file)
            SAVE_DATA.update(save_json)

    def get_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ACTIONS['escape'] = True
                    self.running = False
                elif event.key == pygame.K_e:
                    ACTIONS['e'] = True
                elif event.key == pygame.K_z:
                    ACTIONS['z'] = True
                elif event.key == pygame.K_x:
                    ACTIONS['x'] = True
                elif event.key == pygame.K_c:
                    ACTIONS['c'] = True
                elif event.key == pygame.K_TAB:
                    ACTIONS['tab'] = True
                elif event.key == pygame.K_SPACE:
                    ACTIONS['space'] = True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    ACTIONS['left'] = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    ACTIONS['right'] = True
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    ACTIONS['up'] = True
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    ACTIONS['down'] = True

               
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    ACTIONS['e'] = False
                elif event.key == pygame.K_z:
                    ACTIONS['z'] = False
                elif event.key == pygame.K_x:
                    ACTIONS['x'] = False
                elif event.key == pygame.K_c:
                    ACTIONS['c'] = False
                elif event.key == pygame.K_TAB:
                    ACTIONS['tab'] = False
                elif event.key == pygame.K_SPACE:
                    ACTIONS['space'] = False 
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    ACTIONS['left'] = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    ACTIONS['right'] = False
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    ACTIONS['up'] = False
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    ACTIONS['down'] = False

            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:
                    ACTIONS['scroll_up'] = True
                elif event.y == -1:
                    ACTIONS['scroll_down'] = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ACTIONS['left_click'] = True
                elif event.button == 3:
                    ACTIONS['right_click'] = True
                elif event.button == 4:
                    ACTIONS['scroll_down'] = True
                elif event.button == 2:
                    ACTIONS['scroll_up'] = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    ACTIONS['left_click'] = False
                elif event.button == 3:
                    ACTIONS['right_click'] = False
                elif event.button == 4:
                    ACTIONS['scroll_down'] = False
                elif event.button == 2:
                    ACTIONS['scroll_up'] = False

    def reset_keys(self):
        for action in ACTIONS:
            ACTIONS[action] = False

    def load_states(self):
        self.pygame_logo = PygameLogo(self)
        self.stack.append(self.pygame_logo)

    def get_csv_layer(self, path):
        grid = []
        with open(path) as layout:
            layer = reader(layout, delimiter = ',')
            for row in layer:
                grid.append(list(row))
            return grid

    def get_folder_images(self, path):
        surf_list = []
        for _, __, img_files in walk(path):
            for img in img_files:
                full_path = path + '/' + img
                img_surf = pygame.image.load(full_path).convert_alpha()
                surf_list.append(img_surf)
        return surf_list
 
    def render_text(self, text, colour, font, pos, topleft=False):
        surf = font.render (str(text), False, colour)
        rect = surf.get_rect(topleft = pos) if topleft else surf.get_rect(center = pos)
        self.screen.blit(surf, rect)

    def custom_cursor(self, screen):
        #surf = pygame.image.load('assets/crosshair.png').convert_alpha()
        surf = pygame.Surface((5,5))
        surf.fill((WHITE))
        rect = surf.get_rect(center = pygame.mouse.get_pos())
        pygame.mouse.set_visible(False)
        surf.set_alpha(150)
        screen.blit(surf, rect)

    def update(self, dt):
        self.stack[-1].update(dt)
 
    def draw(self, screen):
        self.stack[-1].draw(screen)
        self.custom_cursor(screen)
        pygame.display.flip()

    def main_loop(self):
        dt = self.clock.tick(60) * 0.06
        self.get_events()
        self.update(dt)
        self.draw(self.screen)
        
if __name__ == "__main__":
    game = Game()
    while game.running:
        game.main_loop()
        #cProfile.run("game.main_loop()", sort="cumulative")

