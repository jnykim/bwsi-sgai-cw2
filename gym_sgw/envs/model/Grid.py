import random
import json
import xlrd
from typing import List
import numpy as np
import pygame as pg
from gym_sgw.envs.model.Cell import Cell
from gym_sgw.envs.enums.Enums import MapObjects, Terrains, Actions, Orientations, MapProfiles, MapColors, NPCDirection

class Grid:

    def __init__(self, map_file: str = None, rows=25, cols=25, random_profile: MapProfiles = MapProfiles.uniform):
        self.map_file = map_file
        self.rows = rows
        self.cols = cols
        self.random_profile = random_profile
        self.player_orientation = None
        self.player_location = None
        # Data collection
        # Totals
        self.collect_data = True
        self.mid_peds = 0
        self.young_peds = 0
        self.old_peds = 0
        self.mid_injured = 0
        self.young_injured = 0
        self.old_injured = 0
        self.zombies = 0
        self.batteries = 0
        self.turns_mud = 0
        self.turns_fire = 0
        self.peds_injured = 0
        self.peds_injured_percentage = 0.0
        # Squished
        self.mid_peds_squished = 0
        self.young_peds_squished = 0
        self.old_peds_squished = 0
        self.mid_injured_squished = 0
        self.young_injured_squished = 0
        self.old_injured_squished = 0
        self.zombies_squished = 0
        self.mid_peds_squished_percentage = 0.0
        self.young_peds_squished_percentage = 0.0
        self.old_peds_squished_percentage = 0.0
        self.mid_injured_squished_percentage = 0.0
        self.young_injured_squished_percentage = 0.0
        self.old_injured_squished_percentage = 0.0
        self.zombies_squished_percentage = 0.0
        # Picked up
        self.mid_injured_pickedup = 0
        self.young_injured_pickedup = 0
        self.old_injured_pickedup = 0
        self.batteries_pickedup = 0
        self.mid_injured_pickedup_percentage = 0.0
        self.young_injured_pickedup_percentage = 0.0
        self.old_injured_pickedup_percentage = 0.0
        self.batteries_pickedup_percentage = 0.0
        # Saved
        self.mid_injured_saved = 0
        self.young_injured_saved = 0
        self.old_injured_saved = 0
        self.mid_injured_saved_percentage = 0.0
        self.young_injured_saved_percentage = 0.0
        self.old_injured_saved_percentage = 0.0
        # Changed
        self.changed_zombies = 0
        self.changed_zombies_percentage = 0.0
        # Grid
        self.grid = self.read_in_map() if map_file is not None else self.random_grid()
        self.map_max_energy = None

        self.mid_pickedup = False
        self.young_pickedup = False
        self.old_pickedup = False
        self.mid_squashed=False
        self.young_squashed=False
        self.old_squashed=False
        self.zsplat=False
        self.psplat=False
        self.soundlink=""
        self.sound=False

    def read_in_map(self):

        # Hard-coded Constants
        SYMBOL_PLAYER_LIST = ['^', '>', 'v', '<']
        SYMBOL_MIDINJURED = '*'
        SYMBOL_YOUNGINJURED = 'o'
        SYMBOL_OLDINJURED = 'u'
        SYMBOL_ZOMBIE = 'Z'
        SYMBOL_BATTERY = '#'
        SYMBOL_MIDPEDESTRIAN = '@'
        SYMBOL_YOUNGPEDESTRIAN = 'a'
        SYMBOL_OLDPEDESTRIAN = 'e'
        SHEET_INDEX = 0

        # Open Excel file
        book = xlrd.open_workbook(self.map_file, formatting_info=True)

        # Each sheet (tabs at the bottom) contains 1 map
        sheet = book.sheet_by_index(SHEET_INDEX)
        print('Loading Map: {}'.format(sheet.name))

        # Get constants defined in spreadsheet -- cells are 0 indexed (hardcoded references for now)
        max_width = int(sheet.cell(19, 3).value)
        max_height = int(sheet.cell(20, 3).value)
        start_row = int(sheet.cell(21, 3).value) - 1
        start_col = int(sheet.cell(22, 3).value) - 1
        self.map_max_energy = int(sheet.cell(25, 3).value)

        color_indexes = {}
        # Get color constants for terrain, found in the legend
        for i in range(7):
            xfx = sheet.cell_xf_index(2 + i, 1)
            xf = book.xf_list[xfx]
            bgx = xf.background.pattern_colour_index
            color_indexes[bgx] = i  # i = enum value, where 0 = none, etc.

        # Get end rows and cols of map
        max_rows = min(sheet.nrows, start_row + max_height)
        max_cols = min(sheet.ncols, start_col + max_width)
        end_row = start_row
        end_col = start_col

        # Get the bounds of the map
        for row_ in range(start_row, max_rows):
            for col_ in range(start_col, max_cols):
                cell = sheet.cell(row_, col_)
                xfx = sheet.cell_xf_index(row_, col_)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                # Check if cell is empty
                if not cell.value and color_indexes[bgx] == 0:
                    continue
                # otherwise update the end_row and end_col
                else:
                    end_row = max(end_row, row_)
                    end_col = max(end_col, col_)

        # Set the bounds of the map
        num_rows = end_row - start_row + 1
        num_cols = end_col - start_col + 1

        # Update important things based on the read in map
        self.rows = num_rows
        self.cols = num_cols

        grid = []
        for r_ in range(num_rows):
            grid_row = []
            for c_ in range(num_cols):
                row_, col_ = r_ + start_row, c_ + start_col
                sheet_cell = sheet.cell(row_, col_)
                xfx = sheet.cell_xf_index(row_, col_)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                # Terrain
                if bgx in color_indexes:
                    grid_cell = Cell(Terrains(color_indexes[bgx]))
                else:
                    grid_cell = Cell()
                # Objects
                if sheet_cell.value in SYMBOL_PLAYER_LIST:
                    grid_cell.add_map_object(MapObjects.player)
                    self.player_location = [r_, c_]
                    if sheet_cell.value == '^':
                        self.player_orientation = Orientations.up
                    elif sheet_cell.value == '>':
                        self.player_orientation = Orientations.right
                    elif sheet_cell.value == 'v':
                        self.player_orientation = Orientations.down
                    elif sheet_cell.value == '<':
                        self.player_orientation = Orientations.left
                    else:
                        raise ValueError('Invalid player icon')
                elif sheet_cell.value == SYMBOL_MIDINJURED:
                    grid_cell.add_map_object(MapObjects(1))
                    grid_cell.set_health(100)
                    self.mid_injured += 1
                elif sheet_cell.value == SYMBOL_YOUNGINJURED:
                    grid_cell.add_map_object(MapObjects(2))
                    grid_cell.set_health(100)
                    self.young_injured += 1
                elif sheet_cell.value == SYMBOL_OLDINJURED:
                    grid_cell.add_map_object(MapObjects(3))
                    grid_cell.set_health(100)
                    self.old_injured += 1
                elif sheet_cell.value == SYMBOL_ZOMBIE:
                    grid_cell.add_map_object(MapObjects(7))
                    self.zombies += 1
                elif sheet_cell.value == SYMBOL_BATTERY:
                    grid_cell.add_map_object(MapObjects(8))
                    self.batteries += 1
                elif sheet_cell.value == SYMBOL_MIDPEDESTRIAN:
                    grid_cell.add_map_object(MapObjects(4))
                    self.mid_peds += 1
                elif sheet_cell.value == SYMBOL_YOUNGPEDESTRIAN:
                    grid_cell.add_map_object(MapObjects(5))
                    self.young_peds += 1
                elif sheet_cell.value == SYMBOL_OLDPEDESTRIAN:
                    grid_cell.add_map_object(MapObjects(6))
                    self.old_peds += 1

                # Add cell to grid[][]
                grid_row.append(grid_cell)

            grid.append(grid_row)

        return grid

    def random_grid(self):
        empty_grid = self._get_empty_grid_with_boarders()
        random_grid = self._random_fill_setup(empty_grid)
        return random_grid

    def _get_empty_grid_with_boarders(self) -> List:
        grid = list()
        for r_ in range(self.rows):
            row_data = []
            for c_ in range(self.cols):
                # Put edges to the top and bottom
                if r_ == 0 or r_ == self.rows - 1:
                    cell_data = Cell(Terrains.out_of_bounds)
                # Put edges to the left and right
                elif c_ == 0 or c_ == self.cols - 1:
                    cell_data = Cell(Terrains.out_of_bounds)
                # Set normal defaults then
                else:
                    cell_data = Cell(Terrains.floor)
                row_data.append(cell_data)
            grid.append(row_data)
        return grid

    def _random_fill_setup(self, grid):
        # This replicates the excel workbook that generates random maps. Directly implemented for ease of use.
        # The only difference is that this implementation also adds the player with a valid orientation.

        # Define map element's cumulative probability table based on the mode (magic numbers tuned by instructors)
        mode = self.random_profile

        if mode == MapProfiles.trolley:
            p_wall = 30
            p_floor = 79
            p_hospital = 80
            p_fire = 83
            p_mud = 86
            p_midInjured = 88
            p_youngInjured = 89
            p_oldInjured = 90
            p_youngpedestrian = 91
            p_oldpedestrian = 92
            p_midPedestrian = 94

            p_zombie = 99
            p_battery = 100
        elif mode == MapProfiles.sparse:
            p_wall = 20
            p_floor = 79
            p_hospital = 80
            p_fire = 83
            p_mud = 86
            p_midInjured = 87
            p_youngInjured = 88
            p_oldInjured = 89
            p_youngpedestrian = 92
            p_oldpedestrian = 93
            p_midPedestrian = 96
            p_zombie = 99
            p_battery = 100
        elif mode == MapProfiles.pacman:
            p_wall = 35
            p_floor = 65
            p_hospital = 65
            p_fire = 65
            p_mud = 65
            p_midInjured = 65
            p_youngInjured = 65
            p_oldInjured = 65 
            p_youngpedestrian = 69
            p_oldpedestrian = 72
            p_midPedestrian = 75
            p_zombie = 95
            p_battery = 100
        elif mode == MapProfiles.spoiled:
            #values below for pedestrians/victims need to be changed
            p_wall = 10
            p_floor = 64
            p_hospital = 69
            p_fire = 72
            p_mud = 75
            p_midInjured = 94
            p_youngInjured = 95
            p_oldInjured = 96 
            p_youngpedestrian = 97
            p_oldpedestrian = 98
            p_midPedestrian = 99
            p_zombie = 100
            p_battery = 100
        elif mode == MapProfiles.twisty:
            # values below for pedestrians/victims need to be changed
            p_wall = 37
            p_floor = 88
            p_hospital = 89
            p_fire = 90
            p_mud = 91
            p_midInjured = 92
            p_youngInjured = 93
            p_oldInjured = 94
            p_youngpedestrian = 95
            p_oldpedestrian = 96
            p_midPedestrian = 97
            p_zombie = 98
            p_battery = 100
        elif mode == MapProfiles.volcano:
            # values below for pedestrians/victims need to be changed
            p_wall = 2
            p_floor = 53
            p_hospital = 54
            p_fire = 79
            p_mud = 91
            p_midInjured = 92
            p_youngInjured = 93
            p_oldInjured = 94
            p_youngpedestrian = 95
            p_oldpedestrian = 96
            p_midPedestrian = 97
            p_zombie = 98
            p_battery = 100
        else:  # Default to the uniform case
            p_wall = 11
            p_floor = 23
            p_hospital = 34
            p_fire = 45
            p_mud = 56
            p_midInjured = 67
            p_youngInjured = 68
            p_oldInjured = 69 
            p_youngpedestrian = 78
            p_oldpedestrian = 79
            p_midPedestrian = 80
            p_zombie = 89
            p_battery = 100

        # for each cell in the grid
        for r_ in range(len(grid)):
            for c_ in range(len(grid[r_])):
                # Start the player in the middle of the grid facing right
                if r_ == int(self.rows // 2) and c_ == int(self.cols // 2):
                    grid[r_][c_].add_map_object(MapObjects.player)
                    self.player_location = [r_, c_]
                    self.player_orientation = Orientations.right
                    continue
                curr_cell = grid[r_][c_]

                # Leave in place any boarder walls that we may have set already in the grid when we initialized it.
                if curr_cell.terrain is Terrains.out_of_bounds:
                    continue

                # Get a random int between 1 and 100, note these bounds are both inclusive
                cell_roll = random.randint(1, 100)  # We could use a random continuous value if we wanted too!
                if cell_roll < p_wall:
                    grid[r_][c_].terrain = Terrains.wall
                elif cell_roll < p_floor:
                    grid[r_][c_].terrain = Terrains.floor
                elif cell_roll < p_hospital:
                    grid[r_][c_].terrain = Terrains.hospital
                elif cell_roll < p_fire:
                    grid[r_][c_].terrain = Terrains.fire
                elif cell_roll < p_mud:
                    grid[r_][c_].terrain = Terrains.mud
                elif cell_roll < p_midInjured:
                    grid[r_][c_].add_map_object(MapObjects.midInjured)
                    grid[r_][c_].set_health(100)
                    self.mid_injured += 1
                elif cell_roll < p_youngInjured:
                    grid[r_][c_].add_map_object(MapObjects.youngInjured)
                    grid[r_][c_].set_health(100)
                    self.young_injured += 1
                elif cell_roll < p_oldInjured:
                    grid[r_][c_].add_map_object(MapObjects.oldInjured)
                    grid[r_][c_].set_health(100)
                    self.old_injured += 1
                elif cell_roll < p_youngpedestrian:
                    grid[r_][c_].add_map_object(MapObjects.youngPedestrian)
                    self.young_peds += 1
                elif cell_roll < p_oldpedestrian:
                    grid[r_][c_].add_map_object(MapObjects.oldPedestrian)
                    self.old_peds += 1
                elif cell_roll < p_midPedestrian:
                    grid[r_][c_].add_map_object(MapObjects.midPedestrian)
                    self.mid_peds += 1
                elif cell_roll < p_zombie:
                    grid[r_][c_].add_map_object(MapObjects.zombie)
                    self.zombies += 1
                elif cell_roll <= p_battery:
                    grid[r_][c_].add_map_object(MapObjects.battery)
                    self.batteries += 1
                else:
                    raise RuntimeError('Random cell value out of range?')
        return grid

    def do_turn(self, action: Actions):
        self.sound=False
        # Update player position based on current location and orientation
        if action == Actions.step_forward:
            self._execute_step_forward()
        elif action == Actions.turn_left:
            self._execute_turn_left()
        elif action == Actions.turn_right:
            self._execute_turn_right()
        # Didn't find a valid action so defaulting to none
        elif action == Actions.none:
            pass
        else:
            raise ValueError('Invalid action found while attempting to do turn on the Grid.')
            # Idea 2: Looping over entire grid and if cell has a P/Z/I, move npc randomly
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if len(cell.objects) == 0:
                    continue
                # print(cell.get_data().values())
                if MapObjects.player not in cell.objects:
                    toMove = [MapObjects.zombie, MapObjects.youngInjured, MapObjects.oldInjured,
                          MapObjects.midInjured, MapObjects.midPedestrian, MapObjects.youngPedestrian,
                              MapObjects.oldPedestrian]
                    if cell.objects[0] in toMove:
                        self.random_object_move([r, c])

        # Remove health from injured
        for r_ in range(len(self.grid)):
            for c_ in range(len(self.grid[r_])):
                target=self.grid[r_][c_]
                if MapObjects.player not in target.objects and len(target.objects) !=0:
                    target.lose_health()
                    #turn victims into zombies if health is 0 or below
                    if target.health<=0:
                        if MapObjects.midInjured in target.objects:
                            target.remove_map_object(MapObjects.midInjured)
                            target.add_map_object(MapObjects.zombie)
                            self.zombies += 1
                            self.changed_zombies += 1
                        if MapObjects.oldInjured in target.objects:
                            target.remove_map_object(MapObjects.oldInjured)
                            target.add_map_object(MapObjects.zombie)
                            self.zombies += 1
                            self.changed_zombies += 1
                        if MapObjects.youngInjured in target.objects:
                            target.remove_map_object(MapObjects.youngInjured)
                            target.add_map_object(MapObjects.zombie)
                            self.zombies += 1
                            self.changed_zombies += 1
        # Process penalties and rewards
        # Baseline score, energy numbers for each move, modify these based on the cell we end up at
        turn_score = self._get_score_of_action()  # Total score is captured in the env
        energy_action = self._get_energy_of_action()  # can be negative if gained energy
        done = False  # always false, the game object will keep track of total energy and total score
        self.peds2victs()
        return turn_score, energy_action, done

    def _execute_step_forward(self):

        self.zsplat=False
        self.psplat=False

        # Get the next position based on orientation
        curr_pos = self.player_location
        if self.player_orientation == Orientations.right:
            next_pos = [curr_pos[0], curr_pos[1] + 1]
        elif self.player_orientation == Orientations.left:
            next_pos = [curr_pos[0], curr_pos[1] - 1]
        elif self.player_orientation == Orientations.up:
            next_pos = [curr_pos[0] - 1, curr_pos[1]]
        elif self.player_orientation == Orientations.down:
            next_pos = [curr_pos[0] + 1, curr_pos[1]]
        else:
            raise RuntimeError('Invalid orientation when trying to move forward')
            # Check validity of move
        if not self._is_valid_move(next_pos):
                next_pos = curr_pos


            # Update the player's position
        self.player_location = next_pos

            # Grab the current and next cell
        curr_cell = self.grid[curr_pos[0]][curr_pos[1]]
        next_cell = self.grid[next_pos[0]][next_pos[1]]

        # Check if injured will be picked up
        if MapObjects.midInjured not in curr_cell.objects and MapObjects.youngInjured not in curr_cell.objects and MapObjects.oldInjured not in curr_cell.objects:
            if MapObjects.midInjured in next_cell.objects:
                self.mid_pickedup = True

            elif MapObjects.youngInjured in next_cell.objects:
                self.young_pickedup = True

            elif MapObjects.oldInjured in next_cell.objects:
                self.old_pickedup = True

        elif MapObjects.player not in next_cell.objects :
            if MapObjects.midInjured in next_cell.objects:
                self.mid_squashed = True
                next_cell.remove_map_object(MapObjects.midInjured)
            elif MapObjects.youngInjured in next_cell.objects:
                self.young_squashed = True
                next_cell.remove_map_object(MapObjects.youngInjured)
            elif MapObjects.oldInjured in next_cell.objects:
                self.old_squashed= True
                next_cell.remove_map_object(MapObjects.oldInjured)

            # Update the player's position in the cells
        curr_cell.remove_map_object(MapObjects.player)
        next_cell.add_map_object(MapObjects.player)
        # Update the map objects in cells so they move with the player (update injured, passengers)
        # add a point for picking up the victim here?
        if MapObjects.midInjured in curr_cell.objects:
            curr_cell.remove_map_object(MapObjects.midInjured)
            next_cell.add_map_object(MapObjects.midInjured)
        elif MapObjects.youngInjured in curr_cell.objects:
            curr_cell.remove_map_object(MapObjects.youngInjured)
            next_cell.add_map_object(MapObjects.youngInjured)
        elif MapObjects.oldInjured in curr_cell.objects:
            curr_cell.remove_map_object(MapObjects.oldInjured)
            next_cell.add_map_object(MapObjects.oldInjured)


    # added function below
    def peds2victs(self):
        for r_ in range(len(self.grid)):
                for c_ in range(len(self.grid[r_])):
                    if self.grid[r_][c_].terrain is not Terrains.out_of_bounds:
                        if MapObjects.midPedestrian in self.grid[r_][c_].objects and random.randint(0,2)==0:
                            if MapObjects.zombie in self.grid[r_ + 1][c_].objects or MapObjects.zombie in self.grid[r_ - 1][c_].objects or MapObjects.zombie in self.grid[r_][c_ + 1].objects or MapObjects.zombie in self.grid[r_][c_ - 1].objects:
                                self.grid[r_][c_].remove_map_object(MapObjects.midPedestrian)
                                self.grid[r_][c_].add_map_object(MapObjects.midInjured)
                                self.grid[r_][c_].set_health(100);
                                self.mid_injured += 1
                                self.peds_injured += 1
                        elif MapObjects.youngPedestrian in self.grid[r_][c_].objects and random.randint(0,3)==0:
                            if MapObjects.zombie in self.grid[r_ + 1][c_].objects or MapObjects.zombie in self.grid[r_ - 1][c_].objects or MapObjects.zombie in self.grid[r_][c_ + 1].objects or MapObjects.zombie in self.grid[r_][c_ - 1].objects:
                                self.grid[r_][c_].remove_map_object(MapObjects.youngPedestrian)
                                self.grid[r_][c_].add_map_object(MapObjects.youngInjured)
                                self.grid[r_][c_].set_health(100);
                                self.young_injured += 1
                                self.peds_injured += 1
                        elif MapObjects.oldPedestrian in self.grid[r_][c_].objects and random.randint(0,1)==0:
                            if MapObjects.zombie in self.grid[r_ + 1][c_].objects or MapObjects.zombie in self.grid[r_ - 1][c_].objects or MapObjects.zombie in self.grid[r_][c_ + 1].objects or MapObjects.zombie in self.grid[r_][c_ - 1].objects:
                                self.grid[r_][c_].remove_map_object(MapObjects.oldPedestrian)
                                self.grid[r_][c_].add_map_object(MapObjects.oldInjured)
                                self.grid[r_][c_].set_health(100)
                                self.old_injured += 1
                                self.peds_injured += 1

    def _execute_turn_left(self):
        if self.player_orientation == Orientations.right:
            self.player_orientation = Orientations.up
        elif self.player_orientation == Orientations.left:
            self.player_orientation = Orientations.down
        elif self.player_orientation == Orientations.up:
            self.player_orientation = Orientations.left
        elif self.player_orientation == Orientations.down:
            self.player_orientation = Orientations.right
        else:
            raise RuntimeError('Invalid orientation when trying to change orientation left')

    def _execute_turn_right(self):
        if self.player_orientation == Orientations.right:
            self.player_orientation = Orientations.down
        elif self.player_orientation == Orientations.left:
            self.player_orientation = Orientations.up
        elif self.player_orientation == Orientations.up:
            self.player_orientation = Orientations.right
        elif self.player_orientation == Orientations.down:
            self.player_orientation = Orientations.left
        else:
            raise RuntimeError('Invalid orientation when trying to change orientation right')

    def _get_score_of_action(self):
        # Default Reward Scheme
        MIDPICKUP_REWARD = 2 # +2 per picked-up middle aged victim
        YOUNGPICKUP_REWARD = 3 # +3 per picked-up young victim
        OLDPICKUP_REWARD = 1 # +1 per picked-up old victim
        MIDRESCUE_REWARD = 11  # +11 per rescued middle aged victim (picked up one by one and delivered to hospital)
        YOUNGRESCUE_REWARD = 12  # +12 per rescued young victim (picked up one by one and delivered to hospital)
        OLDRESCUE_REWARD = 10  # +10 per rescued old victim (picked up one by one and delivered to hospital)
        MIDPED_PENALTY = -10  # -10 per squished middle aged pedestrian (or mobile pedestrian)
        YOUNGPED_PENALTY = -15  # -15 per squished young pedestrian (or mobile pedestrian)
        OLDPED_PENALTY = -13  # -13 per squished old pedestrian (or mobile pedestrian)
        MIDVIC_PENALTY = -5  # -1 per squished middle aged victim (if you already have one onboard and enter it’s space, SQUISH)
        YOUNGVIC_PENALTY = -6  # -3 per squished young victim (if you already have one onboard and enter it’s space, SQUISH)
        OLDVIC_PENALTY = -4  # -2 per squished old victim (if you already have one onboard and enter it’s space, SQUISH)
        FIRE_PENALTY = -5  # -5 per entry into fire (each entry; but otherwise it doesn’t actually hurt you)
        ZOMBIE_REWARD = 2  # +2 per squished zombie (ZOMBIE DEATH!)
        t_score = 0

        # Grab the cell where the player is (after the move)
        end_cell: Cell = self.grid[self.player_location[0]][self.player_location[1]]

        # Add a reward if they picked up a victim
        if self.mid_pickedup:
            t_score += MIDPICKUP_REWARD
            self.mid_pickedup = False
            self.soundlink="pickup"
            self.sound=True
            self.mid_injured_pickedup += 1
        elif self.young_pickedup:
            t_score += YOUNGPICKUP_REWARD
            self.young_pickedup = False
            self.soundlink = "pickup"
            self.sound=True
            self.young_injured_pickedup += 1
        elif self.old_pickedup:
            t_score += OLDPICKUP_REWARD
            self.old_pickedup = False
            self.soundlink = "pickup"
            self.sound=True
            self.old_injured_pickedup += 1
        # Add a reward if they rescued a victim
        if end_cell.terrain == Terrains.hospital:
            if MapObjects.midInjured in end_cell.objects:
                t_score += MIDRESCUE_REWARD  # Deliver the injured
                end_cell.remove_map_object(MapObjects.midInjured)  # Remove them from the board
                self.soundlink="dropoff"
                self.sound=True
                self.mid_injured_saved += 1
            if MapObjects.youngInjured in end_cell.objects:
                t_score += YOUNGRESCUE_REWARD  # Deliver the injured
                end_cell.remove_map_object(MapObjects.youngInjured)  # Remove them from the board
                self.soundlink = "dropoff"
                self.sound = True
                self.young_injured_saved += 1
            if MapObjects.oldInjured in end_cell.objects:
                t_score += OLDRESCUE_REWARD  # Deliver the injured
                end_cell.remove_map_object(MapObjects.oldInjured)  # Remove them from the board
                self.soundlink = "dropoff"
                self.sound = True
                self.old_injured_saved += 1

        # Add a penalty if you squish an injured person
        if self.mid_squashed:
            t_score += MIDVIC_PENALTY
            self.mid_squashed = False
            self.psplat = True
            self.sound = True
            self.soundlink = "psplat"
            self.mid_injured_squished += 1
        elif self.young_squashed:
            t_score += YOUNGVIC_PENALTY
            self.young_squashed = False
            self.psplat = True
            self.sound = True
            self.soundlink = "psplat"
            self.young_injured_squished += 1
        elif self.old_squashed:
            t_score += OLDVIC_PENALTY
            self.old_squashed = False
            self.psplat = True
            self.sound = True
            self.soundlink = "psplat"
            self.old_injured_squished += 1
        # Add a penalty for going into fire
        if end_cell.terrain == Terrains.fire:
            t_score += FIRE_PENALTY  # ouch
            self.sound=True
            self.soundlink="flame"
            self.turns_fire += 1
        if MapObjects.oldPedestrian in end_cell.objects:
            end_cell.remove_map_object(MapObjects.oldPedestrian)
            t_score+=OLDPED_PENALTY
            self.sound=True
            self.soundlink="psplat"
            self.psplat=True
            self.old_peds_squished += 1
        if MapObjects.midPedestrian in end_cell.objects:
            end_cell.remove_map_object(MapObjects.midPedestrian)
            t_score+=MIDPED_PENALTY
            self.sound=True
            self.soundlink="psplat"
            self.psplat=True
            self.mid_peds_squished += 1
        if MapObjects.youngPedestrian in end_cell.objects:
            end_cell.remove_map_object(MapObjects.youngPedestrian)
            t_score+=YOUNGPED_PENALTY
            self.sound=True
            self.soundlink="psplat"
            self.psplat=True
            self.young_peds_squished += 1
        # Add reward for squishing a zombie
        if MapObjects.zombie in end_cell.objects:
            end_cell.remove_map_object(MapObjects.zombie)
            t_score += ZOMBIE_REWARD  # RUN IT OVER!
            self.zsplat = True
            self.sound = True
            self.soundlink = "zsplat"
            self.zombies_squished += 1


        return t_score

    def _get_energy_of_action(self):
        # Default energy scheme
        BAT_POWER = 20  # Battery = + 20 energy
        MUD_DRAIN = -5  # Mud = 5 energy penalty
        BASE_ENERGY = -1  # All moves costs something
        t_energy = 0

        # Grab the cell where the player is (after the move)
        end_cell: Cell = self.grid[self.player_location[0]][self.player_location[1]]

        # Add energy if you hit a battery (and remove it from the board)
        if MapObjects.battery in end_cell.objects:
            t_energy += BAT_POWER  # I HAAAAVVVEEEEEE THEEEE POOWEEERRRRRRRRRRR
            end_cell.remove_map_object(MapObjects.battery)
            self.sound=True
            self.soundlink="charge"
            self.batteries_pickedup += 1
        # Drain energy if you hit mud (do not remove it from the board)
        if end_cell.terrain == Terrains.mud:
            t_energy += MUD_DRAIN  # wah wah
            self.sound=True
            self.soundlink="mud"
            self.turns_mud += 1

        # Add in base energy
        t_energy += BASE_ENERGY

        return t_energy

    def _is_valid_move(self, pos) -> bool:
        # Don't let the player move out of bounds or through walls
        curr_cell = self.grid[pos[0]][pos[1]]
        return curr_cell.terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]

    def _is_valid_ped_move(self, pos) -> bool:
        # Don't let the npcs move out of bounds or through walls or into unrealistic locations
        curr_cell = self.grid[pos[0]][pos[1]]
        return curr_cell.terrain in [Terrains.floor] and len(curr_cell.objects)==0

    def random_object_move(self, pos):
        #get position of object
        r= pos[0]
        c=pos[1]
        #randomize direction
        dir = random.randint(0, 3)
        if dir == NPCDirection.move_up:
            next_cell = [r - 1, c]
        elif dir == NPCDirection.move_down:
            next_cell = [r + 1, c]
        elif dir == NPCDirection.move_right:
            next_cell = [r, c + 1]
        elif dir == NPCDirection.move_left:
            next_cell = [r, c - 1]
        else:
            raise RuntimeError ("NPC Movement Error")
        #makes sure move is acceptable
        if not self._is_valid_ped_move(next_cell):
            return None;
        #stores previous cell values
        prev=self.grid[r][c]
        prevh=prev.health
        prevobj=prev.objects[0]
        #restores last cell
        prev.remove_map_object(prevobj)
        prev.set_health(-1)
        #updates next cell with object and health of previous cell
        self.grid[next_cell[0]][next_cell[1]].add_map_object(prevobj)
        self.grid[next_cell[0]][next_cell[1]].set_health(prevh)

    @staticmethod
    #find which sprite is shown
    def gethealthrange(x):

        if x >60:
            return "1"
        if x>30:
            return "2"
        else:
            return "3"


    def get_human_cell_value(self, row, col):

        cell = self.grid[row][col]
        cell_val = ''
        k= self.gethealthrange(cell.health)
        if MapObjects.none in cell.objects:
            cell_val += '?'
        if MapObjects.player in cell.objects:
            if self.player_orientation == Orientations.up:
                p_icon = '^'
            elif self.player_orientation == Orientations.down:
                p_icon = 'v'
            elif self.player_orientation == Orientations.left:
                p_icon = '<'
            elif self.player_orientation == Orientations.right:
                p_icon = '>'
            else:
                raise ValueError('Invalid player orientation while retrieving cell value for encoding/decoding')
            cell_val += p_icon
        if MapObjects.battery in cell.objects:
            cell_val += 'B'
        if MapObjects.midInjured in cell.objects:
            cell_val += '*'+k
        if MapObjects.youngInjured in cell.objects:
            cell_val += 'o'+k
        if MapObjects.oldInjured in cell.objects:
            cell_val += 'u'+k
        if MapObjects.midPedestrian in cell.objects:
            cell_val += '@'
        if MapObjects.youngPedestrian in cell.objects:
            cell_val += 'a'
        if MapObjects.oldPedestrian in cell.objects:
            cell_val += 'e'
        if MapObjects.zombie in cell.objects:
            cell_val += 'Z'

        return cell_val

    def _get_machine_cell_value(self, row, col):

        # Encode each cell value with an integer between 0 and 70
        # The ten's place is a map of the terrains as follows:
        #     none, out of bounds, wall=0
        #     floor = 1-20s(nonplayer) and 20s(player)
        #     mud = 30s
        #     fire = 40's
        #     hospital = 50's
        # The one's place is a map of the map object as follows:
        #     none = +0
        #     old pedestrian=2
        #     old injured 1=3
        #     old injured 2=4
        #     old injured 3=5
        #     mid pedestrian=6
        #     mid injured 1=7
        #     mid injured 2=8
        #     mid injured 3=9
        #     young pedestrian=10
        #     young injured 1=11
        #     young injured 2=12
        #     young injured 3=13
        #     zombie=14
        #     battery=15
        #
        #     player_up = +1
        #     player_down = +2
        #     player_left = +3
        #     player_right = +4
        #     player_up full=+5
        #     player_down full=+6
        #     player_left full= +7
        #     player_right full= +8
        #
        cell = self.grid[row][col]
        cell_val = 0

        # Get the ten's place based on the terrain, only ever one kind of terrain
        if cell.terrain == Terrains.none or cell.terrain == Terrains.wall or cell.terrain == Terrains.out_of_bounds:
            cell_val += 0
        elif cell.terrain == Terrains.floor:
            cell_val += 1
        elif cell.terrain == Terrains.mud:
            cell_val += 30
        elif cell.terrain == Terrains.fire:
            cell_val += 40
        elif cell.terrain == Terrains.hospital:
            cell_val += 50
        else:
            raise ValueError('Invalid cell terrain while retrieving cell value for encoding/decoding.')

        # Technically supports more than one object so order here matters
        if MapObjects.player in cell.objects:
            if cell.terrain==Terrains.floor:
                cell_val=20
            if len(cell.objects)==1:
                if self.player_orientation==Orientations.up:
                    cell_val+=1
                if self.player_orientation==Orientations.down:
                    cell_val+=2
                if self.player_orientation==Orientations.left:
                    cell_val+=3
                if self.player_orientation==Orientations.right:
                    cell_val+=4
            else:
                if self.player_orientation==Orientations.up:
                    cell_val+=5
                if self.player_orientation==Orientations.down:
                    cell_val+=6
                if self.player_orientation==Orientations.left:
                    cell_val+=7
                if self.player_orientation==Orientations.right:
                    cell_val+=8
        elif MapObjects.oldPedestrian in cell.objects:
            cell_val+=1
        elif MapObjects.oldInjured in cell.objects:
            if cell.health>60:
                cell_val+=2
            elif cell.health>30:
                cell_val+=3
            else:
                cell_val+=4
        elif MapObjects.youngPedestrian in cell.objects:
            cell_val+=5
        elif MapObjects.youngInjured in cell.objects:
            if cell.health>60:
                cell_val+=6
            elif cell.health>30:
                cell_val+=7
            else:
                cell_val+=8
        elif MapObjects.midPedestrian in cell.objects:
            cell_val+=9
        elif MapObjects.midInjured in cell.objects:
            if cell.health>60:
                cell_val+=10
            elif cell.health>30:
                cell_val+=11
            else:
                cell_val+=12
        elif MapObjects.zombie in cell.objects:
            cell_val+=13
        elif MapObjects.battery in cell.objects:
            cell_val += 14
        return cell_val

    def postRewards(self):
        addedPoints = 0
        for r in range(self.rows):
            for c in range(self.cols):
                target = self.grid[r][c]
                if MapObjects.youngPedestrian in target.objects:
                    addedPoints += 5
                elif MapObjects.oldPedestrian in target.objects:
                    addedPoints += 3
                elif MapObjects.midPedestrian in target.objects:
                    addedPoints += 4
        return addedPoints

    def human_encode(self, turns_executed, action_taken, energy_remaining, game_score):
        # Package up "Grid" object in a way that is viewable to humans (multi-line string)
        grid_data = dict()
        for r_ in range(self.rows):
            for c_ in range(self.cols):
                grid_data[f'{r_}, {c_}'] = self.grid[r_][c_].get_data()
        grid_data['status'] = {
            'turns_executed': turns_executed,
            'action_taken': action_taken,
            'energy_remaining': energy_remaining,
            'game_score': game_score
        }
        return json.dumps(grid_data)

    def machine_encode(self, turns_executed, action_taken, energy_remaining, game_score):
        # Package up the "grid" object to be compatible with state space
        # self.observation_space = spaces.Box(low=0, high=60, shape=(self.num_rows, self.num_cols), dtype='uint8')
        # Create a numpy array with the right dtype filled with zeros and then add in the state values for each cell
        machine_state = np.zeros((self.rows + 1, self.cols), dtype='uint8')
        for r_ in range(self.rows):
            for c_ in range(self.cols):
                cell_val = self._get_machine_cell_value(r_, c_)
                machine_state[r_, c_] = cell_val

        # Add some status fields to the state in the last row
        machine_state[self.rows, 0] = int(turns_executed)
        machine_state[self.rows, 1] = int(action_taken[1])
        machine_state[self.rows, 2] = int(energy_remaining)
        machine_state[self.rows, 3] = int(game_score)

        return machine_state

    def human_render(self, turns_executed, action_taken, energy_remaining, game_score, cell_size=30):
        # Print out the human encoding to standard out
        print('Turns Executed: {0} | Action: {1} | Energy Remaining: {2} | '
              'Score: {3} | Full State: {4}'.format(turns_executed, action_taken,
                                                    energy_remaining, game_score,
                                                    self.human_encode(turns_executed, action_taken,
                                                                      energy_remaining, game_score)))

        # Show a nicer display
        pg.init()
        game_screen = pg.display.set_mode((1000, 800))
        pg.display.set_caption("SGW")
        play_area = pg.Surface((self.rows * cell_size, self.cols * cell_size))
        play_area.fill(pg.color.Color(MapColors.play_area.value))
        game_screen.fill(pg.color.Color(MapColors.game_screen.value))

        # Populate each cell
        for r_ in range(self.rows):
            for c_ in range(self.cols):

                # Set the right background color
                cell = self.grid[r_][c_]
                if cell.terrain == Terrains.none:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.out_of_bounds:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.wall:
                    cell_color = pg.color.Color(MapColors.wall_tile.value)
                elif cell.terrain == Terrains.floor:
                    cell_color = pg.color.Color(MapColors.floor_tile.value)
                elif cell.terrain == Terrains.mud:
                    cell_color = pg.color.Color(MapColors.mud_tile.value)
                elif cell.terrain == Terrains.fire:
                    cell_color = pg.color.Color(MapColors.fire_tile.value)
                elif cell.terrain == Terrains.hospital:
                    cell_color = pg.color.Color(MapColors.hospital_tile.value)
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')

                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                pg.draw.rect(play_area, cell_color, (c_ * cell_size, r_ * cell_size, cell_size, cell_size))
                game_screen.blit(play_area, play_area.get_rect())

                # Add in the cell value string
                pg.font.init()
                cell_font = pg.font.SysFont(pg.font.get_default_font(), 20)
                cell_val = self.get_human_cell_value(r_, c_)
                text_surf = cell_font.render(cell_val, True, pg.color.Color(MapColors.text.value))
                play_area.blit(text_surf, ((c_ * cell_size) + cell_size // 2, (r_ * cell_size) + cell_size // 2))

        # Handle window events and allow for the window to be closed
        game_exit = False
        while not game_exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_exit = True
            pg.display.update()
        pg.quit()

    def machine_render(self, turns_executed, action_taken, energy_remaining, game_score):
        # Render briefly for the machine (not likely to be seen, mainly for debugging)
        # Print the raw machine encoding for debugging only
        print('Turns Executed: {0} | Action: {1} | Energy Remaining: {2} | '
              'Score: {3} | Full State: {4}'.format(turns_executed, action_taken,
                                                    energy_remaining, game_score,
                                                    self.machine_encode(turns_executed, action_taken,
                                                                        energy_remaining, game_score)))

    @staticmethod
    def pp_info(turns_executed, action_taken, energy_remaining, game_score):
        print('Turns Executed: {0} | Action: {1} | Energy Remaining: {2} | '
              'Score: {3}'.format(turns_executed, action_taken, energy_remaining, game_score))


if __name__ == '__main__':
    my_grid = Grid()
    score, energy, is_done = my_grid.do_turn(Actions.step_forward)
    #my_grid.pedestrian_move()
    #my_grid.injured_move()
    #my_grid.zombie_move()
    my_grid.human_render(0, 'test', 50, 0)
    new_location = my_grid.player_location
    new_cell = my_grid.grid[new_location[0]][new_location[1]]
    print(str(new_cell.get_data()) + '  @ loc: {}'.format(new_location))
