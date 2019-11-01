import pygame
from sys import exit


class EventLoop:
    def __init__(self, loop_running=False, actions=None, extra_actions=None):
        self.action_map = {pygame.QUIT: exit, }
        if isinstance(actions, dict):
            self.action_map.update(actions)     # add custom actions, if provided
        self.additional = extra_actions
        self.loop_running = loop_running

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.action_map[event.type]()   # quit game with no argument passed
            elif event.type in self.action_map:
                try:
                    self.action_map[event.type](event)    # execute events from map
                except TypeError:
                    self.action_map[event.type]()       # event function may not accept any parameters
            if self.additional:
                for a_map in self.additional:
                    if event.type in a_map:
                        try:
                            a_map[event.type](event)
                        except TypeError:
                            a_map[event.type]()
