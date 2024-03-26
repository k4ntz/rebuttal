from ocatari.core import OCAtari
import importlib
import pygame
import numpy as np
import sys

GameList = ["Pong"]


LAST_ENEMY_Y_POS = 127
BALL_PREVIOUS_X_POS = 130

def lazy_enemy(self):
    """
    Enemy does not move after returning the shot.
    """
    ram = self.get_ram()
    global LAST_ENEMY_Y_POS, BALL_PREVIOUS_X_POS
    if 0 < ram[11] < 5:
        self.set_ram(21, 127)
        self.set_ram(49, 130)
    if BALL_PREVIOUS_X_POS < ram[49]:
        self.set_ram(21, LAST_ENEMY_Y_POS)
    BALL_PREVIOUS_X_POS = ram[49]
    LAST_ENEMY_Y_POS = ram[21]


def modif_funcs(modifs):
    step_modifs, reset_modifs = [], []
    for mod in modifs:
        if mod == "lazy_enemy":
            step_modifs.append(lazy_enemy)
    return step_modifs, reset_modifs


class HackAtari(OCAtari):
    """
    Modified environments from OCAtari
    """
    def __init__(self, game: str, modifs=[], *args, **kwargs):
        """
        Initialize the game environment.
        """
        super().__init__(game, *args, **kwargs)
        covered = False
        for cgame in GameList:
            if cgame in game:
                covered = True
        if not covered:
            raise ValueError(f"Game {game} is not covered in the HackAtari")
        global modif_funcs
        self.alter_ram_steps, self.alter_ram_reset = modif_funcs(modifs)
        self._oc_step = self.step
        self.step = self._alter_step
        self._oc_reset = self.reset
        self.reset = self._alter_reset
    
    def _alter_step(self, action):
        """
        Take a step in the game environment after altering the ram.
        """
        for func in self.alter_ram_steps:
            func(self)
        ret = self._oc_step(action)
        for func in self.alter_ram_steps:
            func(self)
        return ret

    def _alter_reset(self, *args, **kwargs):
        ret = self._oc_reset(*args, **kwargs)
        for func in self.alter_ram_reset:
            func(self)
        return ret



class HumanPlayable(HackAtari):
    """
    HumanPlayable: Enables human play mode for the game.
    """

    def __init__(self, game, modifs=[], *args, **kwargs):
        """
        Initializes the HumanPlayable environment with the specified game and modifications.
        """
        kwargs["render_mode"] = "human"
        kwargs["render_oc_overlay"] = True
        kwargs["frameskip"] = 1
        super(HumanPlayable, self).__init__(game, modifs, *args, **kwargs)
        self.reset()
        self.render()  # Initialize the pygame video system

        self.paused = False
        self.current_keys_down = set()
        self.keys2actions = self.env.unwrapped.get_keys_to_action()



    def run(self):
        '''
        run: Runs the BoxingExtendedHuman environment, allowing human interaction with the game.
        '''
        pygame.init()
        self.running = True
        while self.running:
            self._handle_user_input()
            if not self.paused:
                action = self._get_action()
                self.step(action)
                self.render()
        pygame.quit()

    def _get_action(self):
        '''
        _get_action: Gets the action corresponding to the current key press.
        '''
        pressed_keys = list(self.current_keys_down)
        pressed_keys.sort()
        pressed_keys = tuple(pressed_keys)
        if pressed_keys in self.keys2actions.keys():
            return self.keys2actions[pressed_keys]
        else:
            return 0  # NOOP

    def _handle_user_input(self):
        '''
        _handle_user_input: Handles user input for the BoxingExtendedHuman environment.
        '''
        self.current_mouse_pos = np.asarray(pygame.mouse.get_pos())

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:  # Window close button clicked
                self.running = False

            elif event.type == pygame.KEYDOWN:  # Keyboard key pressed
                if event.key == pygame.K_p:  # 'P': Pause/Resume
                    self.paused = not self.paused

                if event.key == pygame.K_r:  # 'R': Reset
                    self.env.reset()

                elif (event.key,) in self.keys2actions.keys():  # Env action
                    self.current_keys_down.add(event.key)

            elif event.type == pygame.KEYUP:  # Keyboard key released
                if (event.key,) in self.keys2actions.keys():
                    self.current_keys_down.remove(event.key)


if __name__ == "__main__":
    print("\n\nRandom agent playing, modify the script to integrate your agent " +
          "or play as a human by using `human` as an script argument.\n\n")
    if "human" in sys.argv:
        env = HumanPlayable("Pong", ["lazy_enemy"])
        env.run()
    else:
        env = HackAtari("Pong", ["lazy_enemy"], render_mode="human")
        env.reset()
        done = False
        env.render()
        while not done:
            # load agent here
            action = env.action_space.sample()
            _, _, _, done, _ = env.step(action)
        env.close()