from typing import Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

#from actions import EscapeAction,MovementAction
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler

class Engine:
    # The init function takes three arguments:
    """
    entities: A set of entities which behaves kind a list of enforces uniqueness. We can't add an Entity to the set twice.
    event_handler: it will handle our events.
    player: The player entity, we have a separate reference to it outside of entities for ease of access. We'll need to
            access player a lot more than a random entity in entities.
    """
    def __init__(self,entities:Set[Entity],event_handler:EventHandler,game_map:GameMap,player:Entity):
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()
        
    # We pass the events to it so it can iterate through them and it uses self.event_handler to handle the events.    
    def handle_events(self,events:Iterable[Any])-> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self,self.player)

            self.update_fov() # Update the FOV before the player's next action.
    
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
    def render(self,console:Console,context:Context)->None:
        # Calling the game_map render to draw it to the screen.
        self.game_map.render(console)

        for entity in self.entities:
            #Only print entities that are in the FOV
            if self.game_map.visible[entity.x,entity.y]:
                console.print(entity.x , entity.y ,entity.char, fg = entity.color)
            
        
        context.present(console)

        console.clear()
    
