pyGOAP
===============================================================================

## Advanced AI for Python

bitcraft (leif dot theden at gmail.com)
v.4 - for python 3 (3.3 tested)

If you have any problems or suggestions, please contact me via email.

*Library released under the LGPL v3*
All other files are public domain.

Demo is: main.py
         lib/*


News
===============================================================================

##### 4/4/14   - First commit with python3 support
##### 2/16/14  - Simplify Actions, new OpenGL display (pyglet)
##### 2/13/14  - New Documentation
##### 2/6/14   - Rewrite


Introduction
===============================================================================

pyGoap is a small library for designing AI in Python.  The basic library is
based off of a well-known idea of using graph searches to to create realistic
agents.  Behavior is determined in real-time and is extremely open ended and
well suited for emergent behaviors, but the performance is poor.

pyGOAP is complex.  It removes many assumptions that are made by many planning
systems.  It is not designed to be fast, but to be interesting.

Details about the pyGOAP implementation:
- World state is not available to Agents, though it is recorded.
- Hints about the world state called "Precepts" are distributed to Agents.
- Precepts are not guaranteed to be delivered, or even to be "correct".
- Each Agent has unique view of World State based on Precepts they receive.
- Agents make plans based on their own Actions and their incomplete knowledge.

This library is not complete, but is working as-is.  Please read
"About the Demo" for an introduction to the capabilities presented in metaphors
about life.  "FUN!"


Concepts
===============================================================================

Here are some terms that I've used/invented for the library.  I'm not a great
writer, so please consult the linked articles for more information.  I've
slightly changed the canonical GOAP implementation as described by Orkin,
but I believe that it leads to a more intuitive process of designing agents,
actions, goals, and plans.

===============================================================================
### Action
*An action is a thing done.  An act.  Swing sword, walk, talk, puke, etc.*

Actions are aware of the Agent that is doing the action.  Actions are executed
*over time* rather than instantly.  They have a duration and can change with
time.  Actions change the state of the Agent, Environment, or other Agents
in some way.  They also have effects and prereqs that modify or ready state.
Actions can emit precepts.

Actions are also able to generate other Actions.

===============================================================================
### Precept
*Precepts are abstractions of physical senses: vision, sound, knowledge, etc.*

Precepts are created by Actions and distributed by the Environment.  Agents
receive Precepts and store them.  Precepts carry information that is specific
to the type of Action (Speech, Motion, Action, etc) and also include more
abstract concepts such as knowledge of the World State or other Agents
(DatumPrecept) and interactions between Agents (PropositionPrecept,
SpeechPrecept, QueryPrecept, etc).

===============================================================================
### Memory
*Memory is a set of Precepts stored by an agent*

When an Agent makes a Plan, the Memory is used to deduce the World State and
to choose the set of Actions that will satisfy a Goal.

In GOAP terminology, Memories replace Blackboards, but function differently.

===============================================================================
### Goal
*Goals are a condition that the Agent wants to satisfy*

Agents can have any number of Goals.  Goals have:
* Relevance: determined by the Goal itself
* A Test: the test determines if the Goal is satisfied or not
* A Touch: change Memory by adding a Precept

This is a huge divergence from GOAP.  Goals in pyGOAP are also used as prereqs
("preconditions") and effects.  This greatly simplifies the planner and removes
a huge duplication of code in building Actions.

===============================================================================
### Plan
*A sequence of Actions*

An Agent's planner will produce a Plan to satisfy a Goal.  Plans are created
when the Agent has a new Goal to satisfy.

===============================================================================
### Agent
*Agents have the ability to plan and do actions*

Agents have Actions, Goals, and Memory.  They receive Precepts from the
Environment and give the Environment Actions that they wish to carry out.

Agents will search through all of its Goals to find the Goal that is most
"relevant".  If the Goal has changed (or perhaps there wasn't a Goal in the
first place), the Agent will attempt to create a Plan that satisfies the Goal.

===============================================================================
### Environment
*Environments contain Agents and other objects*

Environments position things, execute Actions, and distribute Precepts.

===============================================================================


About the Demo
===============================================================================

Please read the docstrings in main.py for more information.


Reference
===============================================================================

http://web.media.mit.edu/~jorkin/goap.html

Be sure to read Jeff Orkin's links starting from his 2003 draft.  This and
other resources can be found at the link above.