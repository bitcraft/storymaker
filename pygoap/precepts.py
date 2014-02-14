"""
Contains a set of useful precept types for use with an environment.

implementation note:
    recent evidence shows that named tuples are *slow*.
    i'll continue to use them however, as they are advertised as memory efficient.
    ...needs more evidence, however
"""

from collections import namedtuple as nt


# used to remember where entities are
PositionPrecept = nt('PositionPrecept', 'entity, position')

# used to remember what the time is
TimePrecept = nt('TimePrecept', 'time')

# used to remember a single piece of data
DatumPrecept = nt('DatumPrecept', 'entity, name, value')

# used to remember "seeing" an action performed
ActionPrecept = nt('ActionPrecept', 'entity, action, object')

# used to remember spoken words
SpeechPrecept = nt('SpeechPrecept', 'entity, message')

# used to store moods
MoodPrecept = nt('MoodPrecept', 'entity, name, value')