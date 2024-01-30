from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

from resources import color

if TYPE_CHECKING:
    from tcod import Console
    from resources.engine import Engine
    from resources.game_map import GameMap

def get_names_at_location(x: int, y:int, game_map:GameMap)->str:
    if not game_map.in_bounds(x,y) or not game_map.visible[x,y]:
        return ""
    
    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )
    return names.capitalize()


# Adding the render of the Health Points bar.
def render_bar(
        console: Console,current_value:int, maximum_value:int, total_width:int
)-> None:
    bar_width = int(float(current_value)/maximum_value*total_width)

    console.draw_rect(x=0,y=45,width = total_width, height = 1, ch = 1,bg=color.bar_empty)

    if bar_width>0:
        console.draw_rect(
            x = 0, y = 45, width = bar_width, height = 1, ch = 1, bg = color.bar_filled
        )
    
    console.print(
        x = 1, y = 45, string = f"HP: {current_value}/{maximum_value}",fg=color.bar_text
    )

def render_dungeon_level(
        console: Console,dungeon_level:int,location: Tuple[int,int]
)-> None:
    """
    Render the level the player is currentlly on, at the given location.
    """
    x,y = location
    console.print(x=x, y=y, string = f"Dungeon Level: {dungeon_level}")


# Takes the console x and y coordinates (The location to draw the names) and the engine.
# it grabs the mouse’s current x and y positions, and passes them to get_names_at_location, 
# which we can assume for the moment will return the list of entity names we want. Once we 
# have these entity names as a string, we can print that string to the given x and y location 
# on the screen, with console.print.
def render_names_at_mouse_location(
        console: Console, x: int, y:int, engine:Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    # If coordinates are currently visible to the player, we create a string of the entity's name at
    # The spot, separated by a comma.
    names_at_mouse_location = get_names_at_location(
        x = mouse_x, y = mouse_y, game_map=engine.game_map
    )

    console.print(x==x, y=y, string = names_at_mouse_location)