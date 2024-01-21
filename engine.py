from typing import Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console

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
        
    # We pass the events to it so it can iterate through them and it uses self.event_handler to handle the events.    
    def handle_events(self,events:Iterable[Any])-> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self,self.player)



    # This function handles drawing our screen, iterating through self.entities and printing them to their proper
    # Locations, then present the contex and clear the console.    
    def render(self,console:Console,context:Context)->None:
        # Calling the game_map render to draw it to the screen.
        self.game_map.render(console)

        for entity in self.entities:
            console.print(entity.x,entity.y,entity.char,fg = entity.color)
        
        context.present(console)

        console.clear()
    
