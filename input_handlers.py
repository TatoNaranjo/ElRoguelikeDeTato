from __future__ import annotations

#Python's type hinting system
from typing import Optional, TYPE_CHECKING

#Importing tcod event system to use tcod's event system.
import tcod.event
#Importing the Action class and it's subclasses from actions.
from actions import Action,EscapeAction,BumpAction

if TYPE_CHECKING:
    from engine import Engine

#Creating a class called EventHandler which is a subclass of tcod's EventDispatch class.
#Event Dispatch allows us to send an event to his proper method.
class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self,engine:Engine):
        self.engine = engine

    def handle_events(self)->None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update the FOV before the player's next action.
    #ev_quit is called when we receive a "quit" event, it happens when the player click 'X'
    #on the window of the program.
    def ev_quit(self,event: tcod.event.Quit)-> Optional[Action]:
        
        #Quitting the program with SystemExit()
        raise SystemExit()
    
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

        #If the up key is pressed, our character moves upwards.
        if key == tcod.event.KeySym.UP:
            action = BumpAction(player,dx=0,dy = -1)
        #If the up key is pressed, our character moves backwards.
        elif key == tcod.event.KeySym.DOWN:
            action = BumpAction(player,dx=0,dy=1)
        #If the up key is pressed, our character moves leftwards.
        elif key == tcod.event.KeySym.LEFT:
            action = BumpAction(player,dx=-1,dy=0)
        #If the up key is pressed, our character moves rightwards.
        elif key == tcod.event.KeySym.RIGHT:
            action = BumpAction(player,dx=1,dy = 0)

        #If the player presed the 'Escape' key, we return EscapeAction to exit the game.
        #EscapeAction will be used to do things like exit menus in a future.
        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(player)
        
        #We return the action.
        return action