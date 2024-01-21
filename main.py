#!/usr/bin/env python3
import tcod

from engine import Engine

#Importing EventHandler from input_handlers
from input_handlers import EventHandler

from game_map import GameMap

#Importing the Entity class into main.py
from entity import Entity


def main() ->None:
    #Defining Variables for the Screen Size. 
    #Todo: load this values from a JSON File.
    screen_width = 80
    screen_height = 50

    #Added two integers whiche are used in the GameMap class to describe it's width and height.
    map_width = 80
    map_height = 45

    #tcod will use our font from dejavu10x10_gs_tc.png
    tileset = tcod.tileset.load_tilesheet(
        'src/dejavu10x10_gs_tc.png',32,8,tcod.tileset.CHARMAP_TCOD
    )

    #An instance of our EventHandler Class
    event_handler = EventHandler()

    #Initializing new entities
    player = Entity(int(screen_width/2),int(screen_height/2),"@",(255,255,255))
    npc = Entity(int(screen_width/2-5),int(screen_height/2),"@",(255,255,0))
    entities = {npc,player}

    #The game_map variable holds our initialized GameMap.
    game_map = GameMap(map_width,map_height)
    #We pass it into engine.
    engine = Engine(entities = entities, event_handler=event_handler,game_map = game_map, player=player)
    #This creates the Screen
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset = tileset,
        title = "El Roguelike de Tato",
        vsync=True,
    ) as context:
        #Creates the console to display the elements

        #By default numpy acceses 2D arrays in [y,x] so this line reverses it to [x,y]
        root_console = tcod.console.Console(screen_width,screen_height,order = "F")

        #Game loop core init.
        while True:
            #Printing our @ character.
            engine.render(console=root_console,context=context)

            #This line is the core of the screen updating.
            #context.present updates the screen whit what we've told to display so far.
            events = tcod.event.wait()
            engine.handle_events(events)
            

if __name__ == "__main__":
    main()