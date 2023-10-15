from enum import IntEnum, Enum


class Terrains(IntEnum):
    none = 0
    out_of_bounds = 1
    wall = 2
    floor = 3
    mud = 4
    fire = 5
    hospital = 6


class MapObjects(IntEnum):
    none = 0
    midInjured = 1
    youngInjured = 2
    oldInjured = 3
    midPedestrian = 4
    youngPedestrian = 5
    oldPedestrian = 6
    zombie = 7
    battery = 8
    player = 9


class Actions(IntEnum):
    none = 0
    turn_left = 1
    turn_right = 2
    step_forward = 3


class NPCDirection(IntEnum):
    move_up = 0
    move_right = 1
    move_down = 2
    move_left = 3


class Orientations(IntEnum):
    up = 0
    right = 1
    down = 2
    left = 3


class PlayTypes(IntEnum):
    human = 0
    machine = 1


class MapProfiles(IntEnum):
    uniform = 0
    trolley = 1
    sparse = 2
    pacman = 3
    spoiled = 4
    twisty = 5
    volcano = 6


class MapColors(Enum):
    play_area = '#000000'
    game_screen = '#6665adff'
    black_tile = '#000000'
    wall_tile = '#4b4b51ff'
    floor_tile = '#86868cff'
    mud_tile = '#723415ff'
    fire_tile = '#bd4713ff'
    hospital_tile = '#8c2e3aff'
    text = '#ffffff'
