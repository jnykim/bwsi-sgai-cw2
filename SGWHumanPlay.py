import json
import uuid
import gym
import random
import gym_sgw  # Required, don't remove!
import pygame as pg
from gym_sgw.envs.enums.Enums import Actions, Terrains, PlayTypes, MapProfiles, MapColors, NPCDirection
import os
import time
class SGW:
    """
    Human play game variant.
    """
    def __init__(self, data_log_file='data_log.json', max_energy=50, map_file=None,
                 rand_prof=MapProfiles.trolley, num_rows=25, num_cols=25):
        self.ENV_NAME = 'SGW-v0'
        self.DATA_LOG_FILE_NAME = data_log_file
        self.GAME_ID = uuid.uuid4()
        self.env = None
        self.current_action = Actions.none
        self.max_energy = max_energy
        self.map_file = map_file
        self.rand_prof = rand_prof
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.is_game_over = False
        self.turn = 0
        self.max_turn = 300  # to prevent endless loops and games
        self.cell_size = 30
        self.game_screen = None
        self.play_area = None
        self.current_direction = NPCDirection.move_up

        # Always do these actions upon start
        self._setup()

    def _setup(self):
        # Game parameters
        self.env = gym.make(self.ENV_NAME)
        self.env.play_type = PlayTypes.human  # We will get human states and observations back
        self.env.render_mode = PlayTypes.machine  # We'll draw these manually
        self.env.max_energy = self.max_energy
        self.env.map_file = self.map_file
        self.env.rand_profile = self.rand_prof
        self.env.num_rows = self.num_rows
        self.env.num_cols = self.num_cols
        self.env.reset()
        # Report success
        print('Created new environment {0} with GameID: {1}'.format(self.ENV_NAME, self.GAME_ID))


    def done(self):
        print("Episode finished after {} turns.".format(self.turn))
        self.env.grid.sound=False
        self._draw_screen()
        pg.quit()
        self._cleanup()

    def _cleanup(self):
        self.env.close()

    def _draw_screen(self):
        # Update the screen with the new observation, use the grid object directly
        # Populate each cell
        personhit=self.env.grid.psplat
        zombiehit=self.env.grid.zsplat
        soundOn=self.env.grid.sound

        pg.font.init()
        cell_font = pg.font.SysFont(pg.font.get_default_font(), 35)
        for r_ in range(self.env.grid.rows):
            for c_ in range(self.env.grid.cols):
                cell = self.env.grid.grid[r_][c_]
                if cell.terrain == Terrains.none:
                    cell_top=None;
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.out_of_bounds:
                    cell_top = None;
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.wall:
                    cell_top = os.path.join("Images","wall.png");
                    cell_color = None
                elif cell.terrain == Terrains.floor:
                    cell_top = os.path.join("Images","pavement.png");
                    cell_color = None
                elif cell.terrain == Terrains.mud:
                    cell_top = os.path.join("Images","mud.png");
                    cell_color = None;
                elif cell.terrain == Terrains.fire:
                    cell_top = os.path.join("Images","fire.png");
                    cell_color = os.path.join("Images","pavement.png");
                elif cell.terrain == Terrains.hospital:
                    cell_top = os.path.join("Images","hospital.png");
                    cell_color = os.path.join("Images","pavement.png");
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')
                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                if cell_color==os.path.join("Images","pavement.png"):
                    pic = pg.image.load(cell_color).convert();
                    pic = pg.transform.smoothscale(pic, (self.cell_size, self.cell_size))
                    self.play_area.blit(pic, (c_ * self.cell_size, r_ * self.cell_size))
                elif cell_color!= None:
                    pg.draw.rect(self.play_area, cell_color, (c_ * self.cell_size, r_ * self.cell_size,
                                                          self.cell_size, self.cell_size))

                self.game_screen.blit(self.play_area, self.play_area.get_rect())

                if cell_top!=None:
                    pic = pg.image.load(cell_top).convert_alpha();
                    pic = pg.transform.smoothscale(pic, ( self.cell_size,self.cell_size))
                    self.play_area.blit(pic, (c_ * self.cell_size, r_ * self.cell_size))
                # Add in the cell value string
                cell_val = self.env.grid.get_human_cell_value(r_, c_)
                # cell_val = '{},{}'.format(r_, c_)
                sprite=None
                p=False
                if cell_val!="":
                    if cell_val=='^' and len (cell_val)==1:
                        sprite=os.path.join("Images","ambulance_up.png");
                        p=True
                    elif cell_val=='v' and len (cell_val)==1:
                        sprite=os.path.join("Images","ambulance_down.png");
                        p=True
                    elif cell_val=='<' and len (cell_val)==1:
                        sprite=os.path.join("Images","ambulance_left.png");
                        p=True
                    elif cell_val=='>' and len (cell_val)==1:
                        sprite=os.path.join("Images","ambulance_right.png");
                        p=True
                    elif cell_val[0] == '^':
                            sprite=os.path.join("Images","ambulance_upON.png");
                            p=True
                    elif cell_val[0] == 'v':
                            sprite=os.path.join("Images","ambulance_downON.png");
                            p=True
                    elif cell_val[0] == '<':
                            sprite=os.path.join("Images","ambulance_leftON.png");
                            p=True
                    elif cell_val[0] == '>':
                            sprite=os.path.join("Images","ambulance_rightON.png");
                            p=True
                    elif cell_val == 'Z':
                            sprite = sprite=os.path.join("Images","zombie.png");
                    elif cell_val=="B":
                        sprite=os.path.join("Images","battery.png");
                    elif cell_val=='@':
                        sprite=os.path.join("Images","MPed.png");
                    elif cell_val=='a':
                        sprite=os.path.join("Images","YPed.png");
                    elif cell_val=='e':
                        sprite=os.path.join("Images","OPed.png");
                    elif cell_val == '*1':
                       sprite=os.path.join("Images","Minj1.png");
                    elif cell_val == '*2':
                        sprite=os.path.join("Images","Minj2.png");
                    elif cell_val == '*3':
                        sprite=os.path.join("Images","Minj3.png");
                    elif cell_val == 'o1':
                        sprite=os.path.join("Images","Yinj1.png");
                    elif cell_val == 'o2':
                        sprite=os.path.join("Images","Yinj2.png");
                    elif cell_val == 'o3':
                        sprite=os.path.join("Images","Yinj3.png");
                    elif cell_val == 'u1':
                        sprite=os.path.join("Images","OInj1.png");
                    elif cell_val == 'u2':
                        sprite=os.path.join("Images","OInj2.png");
                    elif cell_val == 'u3':
                        sprite=os.path.join("Images","OInj3.png");
                    else:
                        sprite=None;
                if sprite!=None:
                    if p and personhit:
                        puddle =os.path.join("Images","psplat.png");
                        pic = pg.image.load(puddle).convert_alpha();
                        pic = pg.transform.smoothscale(pic, (self.cell_size, self.cell_size))
                        self.play_area.blit(pic, (c_ * self.cell_size, r_ * self.cell_size))
                    if p and zombiehit:
                        puddle =os.path.join("Images","zsplat.png");
                        pic = pg.image.load(puddle).convert_alpha();
                        pic = pg.transform.smoothscale(pic, (self.cell_size, self.cell_size))
                        self.play_area.blit(pic, (c_ * self.cell_size, r_ * self.cell_size))
                    pic = pg.image.load(sprite).convert_alpha();
                    pic = pg.transform.smoothscale(pic, (self.cell_size, self.cell_size))
                    self.play_area.blit(pic, (c_ * self.cell_size, r_ * self.cell_size))
                else:
                    text_surf = cell_font.render(cell_val, True, pg.color.Color(MapColors.text.value))
                    self.play_area.blit(text_surf, ((c_ * self.cell_size) + self.cell_size // 2,
                                                (r_ * self.cell_size) + self.cell_size // 2))
        #render stats panel
        pg.draw.rect(self.game_screen, "#000000", (self.env.grid.cols * self.cell_size + 5, 5,
                                                           self.cell_size * 8, self.cell_size * 5))
        pg.draw.rect(self.game_screen, '#ffffff', (self.env.grid.cols * self.cell_size + 7, 7,
                                                           self.cell_size * 8 - 4, self.cell_size * 5 - 4))
        pointstring=str(self.env.points())+" points earned"
        energystring=str(self.env.energyleft())+" energy left"
        points = cell_font.render(pointstring, True, "#000000")
        self.game_screen.blit(points, ((self.env.grid.cols * self.cell_size + 10, 10,)))
        energy = cell_font.render(energystring, True, "#000000")
        self.game_screen.blit(energy, ((self.env.grid.cols * self.cell_size + 10, 50,)))
        pg.draw.rect(self.game_screen, "#b6b6b6", (self.env.grid.cols * self.cell_size + 10, 90,
                                                   self.cell_size * 8 - 9, self.cell_size*.7))
        pg.draw.rect(self.game_screen, "#1D98C7", (self.env.grid.cols * self.cell_size + 13, 93,
                                                   (self.env.energyleft()/100)*(self.cell_size * 8 - 9-6), self.cell_size * .7-6))
        if soundOn:
            soundlink = self.env.grid.soundlink
            if soundlink== "pickup":
                sound=os.path.join("Images","pickup.mp3");
            elif soundlink=="dropoff":
                sound=os.path.join("Images","dropoff.mp3");
            elif soundlink=="psplat":
                sound=os.path.join("Images","psplat.mp3");
            elif soundlink=="zsplat":
                sound=os.path.join("Images","zsplat.mp3");
            elif soundlink=="flame":
                sound=os.path.join("Images","flame.mp3");
            elif soundlink=="mud":
                sound=os.path.join("Images","mud.mp3");
            elif soundlink=="charge":
                sound=os.path.join("Images","charge.mp3");
            pg.mixer.music.load(sound)
            pg.mixer.music.play(0)
        pg.display.update()

    def run(self):

        print('Starting new game with human play!')
        # Set up pygame loop for game, capture actions, and redraw the screen on action
        self.env.reset()
        self.env.render_mode = PlayTypes.machine  # We'll draw the screen manually and not render each turn
        pg.init()
        self.game_screen = pg.display.set_mode((1000, 800))
        pg.display.set_caption('SGW Human Play')
        self.play_area = pg.Surface((self.env.grid.rows * self.cell_size, self.env.grid.cols * self.cell_size))
        self.play_area.fill(pg.color.Color(MapColors.play_area.value))
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        self._draw_screen()

        # Main game loop, capture window events, actions, and redraw the screen with updates until game over
        game_exit = False
        while not game_exit:
            for event in pg.event.get():

                # Exit game upon window close
                if event.type == pg.QUIT:
                    game_exit = True
                    self.done()

                if self.turn < self.max_turn and not self.is_game_over:

                    # Execute main turn logic
                    # Start by getting the action, only process a turn if there is an actual action
                    # Catch the player inputs, capture key stroke
                    action = None
                    npc_action = None
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            game_exit = True
                            pg.quit()
                            self.done()
                        if event.key in [pg.K_w, pg.K_SPACE, pg.K_UP, pg.K_3]:
                            action = Actions.step_forward
                        if event.key in [pg.K_a, pg.K_LEFT, pg.K_1]:
                            action = Actions.turn_left
                        if event.key in [pg.K_d, pg.K_RIGHT, pg.K_2]:
                            action = Actions.turn_right
                        if event.key in [pg.K_s, pg.K_DOWN, pg.K_0]:
                            action = Actions.none

                        #p = random.uniform(0, 1)
                        #if p < 0.25:
                        #    npc_action = NPCDirection.move_up
                        #elif p < 0.5:
                        #    npc_action = NPCDirection.move_down
                        #elif p < 0.75:
                        #    npc_action = NPCDirection.move_right
                        #elif p < 1:
                        #    npc_action = NPCDirection.move_left

                    if action is not None:
                        if action in [Actions.step_forward, Actions.turn_right, Actions.turn_left, Actions.none]:
                            # We have a valid action, so let's process it and update the screen
                            encoded_action = self.env.encode_raw_action(action)  # Ensures clean action
                            action_decoded = self.env.decode_raw_action(encoded_action)

                            # Take a step, print the status, render the new state
                            observation, reward, done, info = self.env.step(encoded_action)
                            self.env.pp_info()
                            self.is_game_over = done


                            # Write action and stuff out to disk.
                            data_to_log = {
                                'game_id': str(self.GAME_ID),
                                'turn': self.turn,
                                'raw_action': action,
                                'action': action_decoded,
                                'reward': reward,
                                'game_done': done,
                                'game_info': {k.replace('.', '_'): v for (k, v) in info.items()},
                                'raw_state': observation
                            }
                            with open(self.DATA_LOG_FILE_NAME, 'a') as f_:
                                f_.write(json.dumps(data_to_log) + '\n')
                                f_.close()

                            # Tick up turn
                            self.turn += 1
                            if self.is_game_over:
                                game_exit = True
                                self.done()

                            # Draw the screen
                            if not self.is_game_over:
                                self._draw_screen()

                else:
                    # Else end the game
                    game_exit = True
                    self.done()

        pg.quit()
