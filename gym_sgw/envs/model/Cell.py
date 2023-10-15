from gym_sgw.envs.enums.Enums import MapObjects, Terrains
import random


class Cell:

    def __init__(self, terrain: Terrains = Terrains.none):
        self.terrain = terrain
        self.objects = []
        self.health = -1

    def add_map_object(self, obj: MapObjects):
        self.objects.append(obj)

    def remove_map_object(self, obj: MapObjects):
        # If there's an error on the following line, the most likely error is due to the player
        # object being removed when trying to step forward and the player isn't really there.
        # What would you do to protect against this?
        self.objects.remove(obj)


    def set_health(self, x):
        self.health = x

    def lose_health(self):
        if 'youngInjured' in self.get_data()['objects']:
            self.health -= random.randint(1, 4)
        elif 'midInjured' in self.get_data()['objects']:
            self.health -= random.randint(3, 6)
        elif 'oldInjured' in self.get_data()['objects']:
            self.health -= random.randint(5, 10)

    def get_data(self):
        meta_data = {
            'terrain': self.terrain.name,
            'terrain_key': str(self.terrain.value),
            'objects': [str(obj.name) for obj in self.objects],
            'object_keys': [str(obj.value) for obj in self.objects],
            'health': self.health
        }
        return meta_data
