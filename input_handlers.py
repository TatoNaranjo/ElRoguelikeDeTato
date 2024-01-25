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

    def handle_events(self,context: tcod.context.Context)->None:
        for event in tcod.event.wait():
            context.convert_event(event)
            self.dispatch(event)
    
    def ev_mousemotion(self,event:tcod.event.MouseButton)->None:
        if self.engine.game_map.in_bounds(event.tile.x,event.tile.y):
            self.engine.mouse_location = event.tile.x , event.tile.y
    def ev_quit(self,event:tcod.event.Quit)->Optional[Action]:
        raise SystemExit()
    
    def on_render(self,console: tcod.Console)->None:
        self.engine.render(console)

# EventHandler is now the base class for our other two classes
class MainGameEventHandler(EventHandler):    
    # Iterates through the events, and uses context.convert_event to give the event knowledge on the
    # Mouse position. It then dispatches that event, to be handled like normal.
    def handle_events(self,context:tcod.context.Context)->None:
        for event in tcod.event.wait():
            context.convert_event(event)
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
        
        elif key == tcod.event.KeySym.v:
            self.engine.event_handler = HistoryViewer(self.engine)
        #We return the action.
        return action
    
class GameOverEventHandler(EventHandler):
    def handle_events(self,context:tcod.context.Context) -> None:
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

