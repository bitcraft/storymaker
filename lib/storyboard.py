__author__ = 'Leif'


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


import sqlite3
import os


class Storyteller:
    """
    images:
        file name
        metadata:
            actor:
                class (human, cat, dog, car, etc)
            emotion:
                class (sad, happy, euphoric, etc)
                intensity (float)
            action:
                class (pass, run, express emotion, etc)
                intensity (float)
    """

    db_fn = 'images/images.db'

    def __init__(self):
        self.conn = None
        self.new_db()

    def init_db(self):
        self.conn = sqlite3.connect(self.db_fn)
        with self.conn:
            c = self.conn.cursor()
            c.execute('CREATE TABLE ImagesMeta(FileName TEXT, Price INT)')

    def new_db(self):
        self.conn = None
        os.unlink(self.db_fn)
        self.init_db()
