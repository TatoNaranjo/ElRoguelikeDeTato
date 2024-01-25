from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

#from actions import EscapeAction,MovementAction
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar,render_names_at_mouse_location

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler
class Engine:
    game_map: GameMap
    # The init function takes three arguments:
    """
    entities: A set of entities which behaves kind a list of enforces uniqueness. We can't add an Entity to the set twice.
    event_handler: it will handle our events.
    player: The player entity, we have a separate reference to it outside of entities for ease of access. We'll need to
            access player a lot more than a random entity in entities.
    """
    def __init__(self,player:Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0,0)
        self.player = player
    
    def handle_enemy_turns(self)-> None:
        for entity in self.game_map.entities - {self.player}:
            if entity.ai:
                entity.ai.perform()
        

    
    """
    transparency: This is the first argument, which we're passing self.game_map.tiles["transparent"]. transparency takes a 2D numpy array, 
                  and considers any non-zero values to be transparent. This is the array it uses to calculate the field of view.
    pov: The origin point for the field of view, which is a 2D index. We use the player's x and y position here.
    radius: How far the FOV extends.
    """
    def update_fov(self) -> None:
        """Recompute the visible area based on the player's POV"""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x,self.player.y),
            radius = 8,
        )
        # If a tile is "visible" it should be added to "explored",
        # Sets the explored array to include everything in the visible array, plus it already had.
        # This means: Any tile the player can see, the player also explored.
        self.game_map.explored |= self.game_map.visible



    # This function handles drawing our screen, iterating through self.entities and printing them to their proper
    # Locations, then present the contex and clear the console.    
    def render(self,console:Console)->None:
        # Calling the game_map render to draw it to the screen.
        self.game_map.render(console)
        self.message_log.render(console=console,x=21,y=45,width=40,height=5)

        render_bar(
            console = console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )
        render_names_at_mouse_location(console=console, x = 21, y = 44, engine=self)


        
    
