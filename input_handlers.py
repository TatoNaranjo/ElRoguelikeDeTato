from __future__ import annotations

#Python's type hinting system
from typing import Optional, TYPE_CHECKING

#Importing tcod event system to use tcod's event system.
import tcod.event

import actions
from actions import(
    Action,
    BumpAction,
    PickupAction,
    WaitAction
)
import color
from entity import Item
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

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

    def handle_events(self,event:tcod.event.Event)->None:
        self.handle_action(self.dispatch(event))

    def handle_action(self,action:Optional[Action])->bool:
        """
        Handle actions returned from event methods
        
        Returns True if the action will advance a turn.
        """
        if action is None:
            return False
        
        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0],color.impossible)
            return False #Skip Enemy Turn on Exceptions.
        
        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True
    
    def ev_mousemotion(self,event:tcod.event.MouseButton)->None:
        if self.engine.game_map.in_bounds(event.tile.x,event.tile.y):
            self.engine.mouse_location = event.tile.x , event.tile.y
    def ev_quit(self,event:tcod.event.Quit)->Optional[Action]:
        raise SystemExit()
    
    def on_render(self,console: tcod.Console)->None:
        self.engine.render(console)


# This function make Exits itself when any key is pressed.
class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""
    def handleaction(self,action:Optional[Action])->bool:
        """Return to the main event handler when a valid action was performed."""
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False
    
    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[Action]:
        """By Default any key exits the input handler"""
        if event.sym in { # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,

        }:
            return None
        return self.on_exit()
    
    def ev_mousebuttondown(self,event:tcod.event.MouseButtonDown)->Optional[Action]:
        """By default any mouse click exits the input handler."""
        return self.on_exit()
    
    def on_exit(self) -> Optional[Action]:
        """Called when the user is trying to exit or cancel an action.
        
        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


"""
InventoryEventHandler subclasses AskUserEventHandler, and renders the items within the player's Inventory. 
Depending on where the player is standing, the menu will render off to the side, so the menu won't cover the player. 
If there's nothing in the inventory, it just prints “Empty”. 
Notice that it doesn't give itself a title, as that will be defined in a different subclass (more on that in a bit).

The ev_keydown function takes the user's input, from letters a - z, and associates that with an index in the inventory. 
If the player pressed “b”, for example, the second item in the inventory will be selected and returned. If the player 
presses a key like “c” (item 3) but only has one item, then the message “Invalid entry” will display. If any other key 
is pressed, the menu will close.

"""
class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.
    
    what happens depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self,console:tcod.console)-> None:
        """Render an inventory menu, which displays the items in the inventory and the letter to select them
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <=3:
            height = 3

        if self.engine.player.x <=30:
            x = 40

        else:
            x = 0
        
        y = 0

        width = len(self.TITLE)+4

        console.draw_frame(
            x = x,
            y = y,
            width = width,
            height = height,
            title = self.TITLE,
            clear = True,
            fg = (255,255,255),
            bg = (0,0,0),

        )
        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a")+i)
                console.print(x+1,y+i+1,f"({item_key}) {item.name}")
        else:
            console.print(x+1,y+1, "(Empty)")

    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0<= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid Entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    
    def on_item_selected(self,item:Item)-> Optional[Action]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateEventHandler(InventoryEventHandler):
    """Handle using an inventory item."""
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Return the action for the selected item."""
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""
    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[Action]:
        """Drop this item"""

        return actions.DropItem(self.engine.player,item)
# EventHandler is now the base class for our other two classes
class MainGameEventHandler(EventHandler):    


    
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
            raise SystemExit()
        
        # Press v to see the message log.
        elif key == tcod.event.KeySym.v:
            self.engine.event_handler = HistoryViewer(self.engine)

        # Press g to pickup an item
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)

        elif key == tcod.event.KeySym.i:
            self.engine.event_handler = InventoryActivateEventHandler(self.engine)

        elif key == tcod.event.KeySym.d:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        #We return the action.
        return action
    
class GameOverEventHandler(EventHandler):

    
    def ev_keydown(self,event:tcod.event.KeyDown)->None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP:-1,
    tcod.event.KeySym.DOWN:1,
    tcod.event.KeySym.PAGEUP:-10,
    tcod.event.KeySym.PAGEDOWN:10,
}

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            self.engine.event_handler = MainGameEventHandler(self.engine)

