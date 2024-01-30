from __future__ import annotations

import os

#Python's type hinting system
from typing import Callable, Tuple, Optional,Union, TYPE_CHECKING

#Importing tcod event system to use tcod's event system.
import tcod.event
from tcod import libtcodpy


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

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER
}


ActionOrHandler = Union[Action,"BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers

if a handler is returned the it will become the active handler for future events.
If an action is returned it will be atrempted adn if it's valid then
MainGameEventHandler will become the active handler.
"""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self,event:tcod.event.Event)->BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state,BaseEventHandler):
            return state
        assert not isinstance(state,Action),f"{self!r} can not handle actions."
        return self
    
    def on_render(self,console:tcod.Console)->None:
        raise NotImplementedError()
    
    def ev_quit(self,event:tcod.event.Quit)->Optional[Action]:
        raise SystemExit()
    

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self,parent_handler:BaseEventHandler,text:str):
        self.parent = parent_handler
        self.text = text

    def on_render(self,console:tcod.Console)->None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.rgb["fg"]//=8
        console.rgb["bg"]//=8

        console.print(
            console.width //2,
            console.height //2,
            self.text,
            fg = color.white,
            bg = color.black,
            alignment = libtcodpy.CENTER,
        )
    
    def ev_keydown(self,event:tcod.event.KeyDown)->Optional[BaseEventHandler]:
        """Any Key Returns to the Parent Handler."""
        return self.parent

#Creating a class called EventHandler which is a subclass of tcod's EventDispatch class.
#Event Dispatch allows us to send an event to his proper method.


class EventHandler(BaseEventHandler):
    def __init__(self,engine:Engine):
        self.engine = engine

    def handle_events(self,event:tcod.event.Event)->BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state,BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            #A valid action was performed.
            if not self.engine.player.is_alive:
                #The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine) # Return to the main handler.
        return self

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
    
    def on_render(self,console: tcod.Console)->None:
        self.engine.render(console)


# This function make Exits itself when any key is pressed.
class AskUserEventHandler(EventHandler):

    
    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[ActionOrHandler]:
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
    
    def ev_mousebuttondown(
            self,event:tcod.event.MouseButtonDown
            )->Optional[ActionOrHandler]:
        """By default any mouse click exits the input handler."""
        return self.on_exit()
    
    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.
        
        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render (self,console:tcod.Console)->None:
        super().on_render(console)

        if self.engine.player.x <=30:
            x = 40
        else:
            x = 0
        
        y = 0

        width = len(self.TITLE)*4

        console.draw_frame(
            x=x,
            y=y,
            width = width,
            height = 7,
            title = self.TITLE,
            clear = True,
            fg = (255,255,255),
            bg = (0,0,0),
        )
        console.print(
            x = x+1, y = y+1, string = f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x = x+1, y = y+2, string = f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x = x+1, y = y+3, string = f"XP For Next Level: {self.engine.player.level.experience_to_next_level}"
        )        
        console.print(
            x = x+1, y = y+4, string = f"Attack: {self.engine.player.fighter.power}"
        )
        console.print(
            x = x+1, y = y+5, string = f"Defense: {self.engine.player.fighter.defense}"
        )
class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self,console:tcod.Console)->None:
        super().on_render(console)

        if self.engine.player.x<=30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y = 0,
            width = 35,
            height = 8,
            title = self.TITLE,
            clear = True,
            fg =(255,255,255),
            bg = (0,0,0),

        )

        console.print(x = x+1, y = 1, string = "Congratulations! You Level Up!")
        console.print(x = x+1, y = 2, string = "Select an attribute to increse.")

        console.print(
            x = x+1,
            y = 4,
            string = f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )

        console.print(
            x = x+1,
            y = 5,
            string = f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
        )  

        console.print(
            x = x+1,
            y = 6,
            string = f"c) Defense (+1 defense, from {self.engine.player.fighter.defense})",
        )   
    
    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0<= index<=2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid Entry.",color.invalid)
            return None
        
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(
            self,event:tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to exit the menu, like normal.
        """
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
                
                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) ({item.name})"

                if is_equipped:
                    item_string = f"{item_string} (E)"
                
                console.print(x+1, y+i+1, item_string)
        else:
            console.print(x+1,y+1, "(Empty)")

    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[ActionOrHandler]:
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
    
    def on_item_selected(self,item:Item)-> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateEventHandler(InventoryEventHandler):
    """Handle using an inventory item."""
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player,item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""
    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item"""

        return actions.DropItem(self.engine.player,item)
    

# SelectIndexHandler is what we’ll use when we want to select a tile on the map.

class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    # Sets the mouse_location to the player's current location.
    def __init__(self,engine:Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y
    
    # Will render the console as normal, but also adds a cursor on top that can be used to show where the current
    # Cursor is.
    def on_render(self,console: tcod.Console) ->None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x,y] = color.white
        console.rgb["fg"][x,y] = color.black

    # Gives a way to move the cursor we're drawing around using the keyboard instead of the mouse (using the mouse is still possible)
    # By holding shift, control or alt while pressing a movement key, the cursor will move around faster by skipping over
    # A few spaces.
    
    # If the player presses a confirm key, the method returns the current cursor's location.
    def ev_keydown(self,event:tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation Keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 # Holding modifier keys will speed up key movement
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RCTRL):
                modifier*=5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier*=10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier*=20
            
            x,y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx*modifier
            y += dy*modifier
            # Clamp the cursor index to the map size
            x = max(0,min(x,self.engine.game_map.width-1))
            y = max(0,min(y,self.engine.game_map.height-1))

            self.engine.mouse_location = x,y
            return None
        
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)
    
    # ev_mousebuttondown also returns the location, if the clicked space is within the map boundaries.
    def ev_mousebuttondown(
            self,event:tcod.event.MouseButtonDown
            ) -> Optional[ActionOrHandler]:
        """Left Click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)
    
    # Abstract method that is implemented by LookHandler.
    def on_index_selected(self, x:int, y:int) ->Optional[ActionOrHandler]:
        """Called When a index is selected."""
        raise NotImplementedError()


# LookHandler inherits from SelectIndexHandler, and all it does is return to the MainGameEventHandler
# when receiving a confirmation key. This is because it doesn’t need to do anything special, it’s just 
# used in the case where our player wants to have a look around.
class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""
    def on_index_selected(self, x:int, y:int) ->MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)



# SingleRangedAttackHandler can be used for any scroll or ranged attack that targets one location.
class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a simgle enemy. Only the enemy selected will be affected."""
    def __init__(
            self, engine:Engine, callback:Callable[[Tuple[int,int]],Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self,x:int,y:int)-> Optional[Action]:
        return self.callback((x,y))
    

class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius:int,
        callback:Callable[[Tuple[int,int]],Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self,console:tcod.Console) ->None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x,y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x = x- self.radius-1,
            y = y-self.radius-1,
            width = self.radius **2,
            height = self.radius **2,
            fg = color.red,
            clear = False,
        )
    
    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x,y))
class MainGameEventHandler(EventHandler):    


    
    #Method that will receive key press events and return either an Action subclass or None
    #if no valid key was pressed.
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:

        #action is the variable that will hold whatever subclass of Action we end up assigning it
        #to. If no valid key press is found it remains set to None.
        action:Optional[Action]=None

        #Key holds the actual key the player pressed. Without additional info about modifiers like
        #'Shift' or 'Alt'
        key = event.sym
        modifier = event.mod
        player = self.engine.player

        if key == tcod.event.KeySym.x:
            return actions.TakeStairsAction(player)

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
            return HistoryViewer(self.engine)

        # Press g to pickup an item
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)

        # Press i to open inventory.
        elif key == tcod.event.KeySym.i:
            return InventoryActivateEventHandler(self.engine)

        # Press d to drop an item
        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)

        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)
        #We return the action.
        return action
    
class GameOverEventHandler(EventHandler):
    def on_quit(self)->None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")# Deletes the active save file.
        raise exceptions.QuitWithoutSaving() # Avoid saving a finished game
    
    def ev_quit(self, event:tcod.event.Quit)->None:
        self.on_quit()
    
    def ev_keydown(self,event:tcod.event.KeyDown)->None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()

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

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
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
            return MainGameEventHandler(self.engine)
        return None

