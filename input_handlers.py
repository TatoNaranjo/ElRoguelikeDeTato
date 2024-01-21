#Python's type hinting system
from typing import Optional

#Importing tcod event system to use tcod's event system.
import tcod.event
#Importing the Action class and it's subclasses from actions.
from actions import Action,EscapeAction,MovementAction

#Creating a class called EventHandler which is a subclass of tcod's EventDispatch class.
#Event Dispatch allows us to send an event to his proper method.
class EventHandler(tcod.event.EventDispatch[Action]):

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

        #If the up key is pressed, our character moves upwards.
        if key == tcod.event.KeySym.UP:
            action = MovementAction(dx=0,dy = -1)
        #If the up key is pressed, our character moves backwards.
        elif key == tcod.event.KeySym.DOWN:
            action = MovementAction(dx=0,dy=1)
        #If the up key is pressed, our character moves leftwards.
        elif key == tcod.event.KeySym.LEFT:
            action = MovementAction(dx=-1,dy=0)
        #If the up key is pressed, our character moves rightwards.
        elif key == tcod.event.KeySym.RIGHT:
            action = MovementAction(dx=1,dy = 0)

        #If the player presed the 'Escape' key, we return EscapeAction to exit the game.
        #EscapeAction will be used to do things like exit menus in a future.
        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction()
        
        #We return the action.
        return action