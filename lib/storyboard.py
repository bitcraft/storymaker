class Storyboard:
    def __init__(self):
        self.sketches = list()


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


