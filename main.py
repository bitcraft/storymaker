__author__ = 'Leif'

"""
story generator
===============

program generates stories and illustrates them with GIF's from imgur
gifs will have to be annotated for content and emotional style
"""

class Storyboard:
    def __init__(self):
        self.sketches = []

class Sketch:
    """
    Image with some text to tell the story
    """

    def __init__(self, image, title, desc):
        self.image = image
        self.title = title
        self.desc = desc

class Character:
    def __init__(self, name):
        self.name = name

class Object:
    def __init__(self):
        pass

class Plot:
    """
    device to convey a story
    pygoap...
        goals are subplots
        actions are well...actions, defined in realtime using a set cast
    """
    pass

