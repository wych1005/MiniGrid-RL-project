from gym_minigrid.minigrid import Ball
from gym_minigrid.roomgrid import RoomGrid
from gym_minigrid.register import register
# from time import sleep

class ModifiedBUP(RoomGrid):
    def __init__(self, seed=None):
        room_size = 12
        super().__init__(
            num_rows=1,
            num_cols=2,
            room_size=room_size,
            max_steps=16*room_size**2,
            seed=seed
        )

        self.task = "REMOVE_OBSTACLE"
        self.count = 0

    def _gen_grid(self, width, height):
        super()._gen_grid(width, height)

        # Add a box to the room on the right
        obj, self.box_pos = self.add_object(1, 0, kind="box")
        # Make sure the two rooms are directly connected by a locked door
        self.door, self.pos = self.add_door(0, 0, 0, locked=True)
        # Block the door with a ball
        color = self._rand_color()
        self.grid.set(self.pos[0]-1, self.pos[1], Ball(color))
        # Add a key to unlock the door
        self.add_object(0, 0, 'key', self.door.color)
        self.place_agent(0, 0)
        self.obj = obj
        self.mission = "pick up the %s %s" % (obj.color, obj.type)

    def remove_obstacle(self, action):
        if self.task == "REMOVE_OBSTACLE":
            if self.grid.get(self.pos[0]-1, self.pos[1]) and self.grid.get(self.pos[0]-1, self.pos[1]).object_type == 'ball':
                self.reward = self._reward()
                self.task = "UNLOCK_DOOR"

    def unlock_door(self, action):
        if self.task == "UNLOCK_DOOR":
            if action == self.actions.toggle:
                if self.door.is_open:
                    self.reward = self._reward()
                    self.task = "IN_PROXIMITY"
                    self.ud = True

    def in_proximity(self, action):
        if self.task == "IN_PROXIMITY":
            x, y = self.box_pos[0], self.box_pos[1]
            if (self.box_pos[0], self.box_pos[1]) == (x-1, y+1) or (x, y+1) or (x+1, y+1) or (x+1, y) or (x+1, y-1) or (x, y-1) or (x-1, y-1) or (x-1, y):
                self.reward = self._reward()
                self.task = "MOVE_BOX"
                self.ip = True

    def move_box(self, action):
        if self.task == "MOVE_BOX":
            if action == self.actions.pickup:
                if self.carrying and self.carrying == self.obj:
                    self.reward = self._reward()
                    self.done = True

    def switch_case(self, task, action):
        switcher = {"REMOVE_OBSTACLE": self.remove_obstacle(action),
                    "UNLOCK_DOOR": self.unlock_door(action),
                    "IN_PROXIMITY": self.in_proximity(action),
                    "MOVE_BOX": self.move_box(action) 
                    }
        switcher[task]

    def step(self, action):
        obs, self.reward, self.done, info = super().step(action)
        # print("TASK: ", self.task)
        self.switch_case(self.task, action)
        if self.done:
            self.count += 1
        print("COUNT: ", self.count)
        return obs, self.reward, self.done, info

register(
    id='MiniGrid-ModifiedBUP-v0',
    entry_point='gym_minigrid.envs:ModifiedBUP'
)
