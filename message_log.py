from typing import List, Reversible, Tuple
import textwrap

import tcod

import color

# Will be used to save and display messages in our log. It includes three pieces of information:
"""
plain_text: The actual message text.
fg: The "Foreground" color of the message.
count: Used to display something like "The Orc Attacks(x3)"
"""
class Message:
    def __init__(self, text:str, fg:Tuple[int,int,int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1
    
    @property
    def full_text(self)->str:
        """The Full text of this message incluiding the count if necessary."""
        if self.count>1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text

# It keeps a list of the message's received.
class MessageLog:
    def __init__(self) -> None:
        self.messages:List[Message] = []

    # Is what adds the message to the log. text is required but fg will just default to
    # White if nothing is given. Stack tells us whether to stack messages or not.
    # If we are allowing stacking, and the added message matches the previous message, we
    # just increment the previous message’s count by 1. If it’s not a match, we add it to the list.
    def add_message(
            self,text:str,fg:Tuple[int,int,int] = color.white,*,stack:bool = True,
    ) -> None:
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count+=1
        else:
            self.messages.append(Message(text,fg))
    
    # Render calls render_messages which is a static method that actually renders the messages to the screen.
    # It renders them in reverse order, to make it appear that the messages are scrolling in an upwards direction.
    def render(
            self, console: tcod.console.Console, x: int, y: int, width: int, height: int,
    ) -> None:
        """
        Render this log over the given area.
        'x','y','width','height' is the rectangular region to render onto the 'console'
        """
        self.render_messages(console,x,y,width,height,self.messages)
    
    @staticmethod
    def render_messages(
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """
        Render the messages provided.
        The 'messages' are rendered starting at the last message and working backwards 
        """
        y_offset = height-1

        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text,width)):
                console.print(x=x,y=y+y_offset, string = line, fg=message.fg)
                y_offset -=1
                if y_offset < 0:
                    return # No more space to print messages.