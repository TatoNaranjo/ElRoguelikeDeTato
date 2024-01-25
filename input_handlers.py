from __future__ import annotations

#Python's type hinting system
from typing import Optional, TYPE_CHECKING

#Importing tcod event system to use tcod's event system.
import tcod.event
#Importing the Action class and it's subclasses from actions.
from actions import Action,EscapeAction,BumpAction,WaitAction

if TYPE_CHECKING:
    from engine import Engine

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}


#Creating a class called EventHandler which is a subclass of tcod's EventDispatch class.
#Event Dispatch allows us to send an event to his proper method.
class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self,engine:Engine):
        self.engine = engine

    def handle_events(self)->None:
        raise NotImplementedError()
    
    def ev_quit(self,event:tcod.event.Quit)->Optional[Action]:
        raise SystemExit()

# EventHandler is now the base class for our other two classes
class MainGameEventHandler(EventHandler):    
    def handle_events(self)->None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update the FOV before the player's next action.

    
    #Method that will receive key press events and return either an Action subclass or None
    #if no valid key was pressed.
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:

        #action is the variable that will hold whatever subclass of Action we end up assigning it
        #to. If no valid key press is found it remains set to None.
        action:Optional[Action]=None

        #Key holds the actual key the player pressed. Without additional info about modifiers like
        #'Shift' or 'Alt'
        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx,dy = MOVE_KEYS[key]
            action = BumpAction(player,dx,dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)    

        #If the player presed the 'Escape' key, we return EscapeAction to exit the game.
        #EscapeAction will be used to do things like exit menus in a future.
        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(player)
        
        #We return the action.
        return action
    
class GameOverEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()
    
    def ev_keydown(self,event:tcod.event.KeyDown)->Optional[Action]:
        action: Optional[Action]= None

        key = event.sym

        if key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(self.engine.player)

        # No Valid Key Was Pressed
        return action