"""
Contains a set of useful precept types for use with an environment.

implementation note:
    some evidence shows that named tuples are "slow".
"""

from collections import namedtuple as nt


# used to remember where entities are
PositionPrecept = nt('PositionPrecept', 'entity, position')

# used to remember what the time is
TimePrecept = nt('TimePrecept', 'time')

# used to remember a single piece of data
DatumPrecept = nt('DatumPrecept', 'entity, name, value')

# used to query another agent
QueryPrecept = nt('QueryPrecept', 'entity, name, value')

# used to remember "seeing" (or hearing) an action performed
ActionPrecept = nt('ActionPrecept', 'entity, action, object')

# used by one agent to suggest an action take place
# this is used to coordinate actions between agents
PropositionPrecept = nt('PropositionPrecept', 'entity, action, object')

# used to remember spoken words
SpeechPrecept = nt('SpeechPrecept', 'entity, message')

# used to store moods
MoodPrecept = nt('MoodPrecept', 'entity, name, value')

