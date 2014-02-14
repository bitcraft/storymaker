# pyGOAP v.4
_______________________________________________________________________________

## Advanced AI for Python

bitcraft (leif dot theden at gmail.com)
v.4 - for python 3 (3.3 tested)

If you have any problems or suggestions, please contact me via email.

*Library released under the LGPL v3*
*Demo released under the GPL v3*

Demo is: main.py
         lib/*

All other files are public domain.


## News
_______________________________________________________________________________

##### 2/13/14  - New Documentation!
##### 2/6/14   - Rewrite!

   
## Introduction
_______________________________________________________________________________

pyGoap is a small library for designing AI in Python.  The basic library is
based off of a well-known idea of using graph searches to to create realistic
agents in real-time.  Behavior is determined in real-time and is extremely open
ended and well suited for emergent behaviors.

This library is not complete, but is working as-is.  Please read 
"About the Demo" for an introduction to the capabilities presented in metaphors
about life.  FUN!


## Concepts
_______________________________________________________________________________

Here are some terms that I've used/invented for the library.  I'm not a great
writer, so please consult the linked articles for more information.  I've
slightly changed the canonical GOAP implementation as described by Orkin,
but I believe that it leads to a more intuitive process of designing agents,
actions, goals, and plans.

_______________________________________________________________________________
### Action
*An action is a thing done.  An act.  Swing sword, walk, talk, puke, etc.*  

Actions are aware of the Agent that is doing the action.  Actions are executed
*over time* rather than instantly.  They have a duration and can change with
time, but not through the agent.  Actions change the state of the Agent,
Environment, or other Agents in some way.

_______________________________________________________________________________
### Precept
*Precepts are abstractions of physical senses: vision, sound, knowledge, etc.*  

Precepts are created by Actions and distributed by the environment.  Agents
receive precepts and store them.  Precepts carry information that is specific
to the type of precept (Speech, Action, etc).

_______________________________________________________________________________
### Memory
*Precepts remembered by an agent*

When an agent makes a plan, the memory is used to deduce the state of the agent
and to choose the set of actions that will satisfy a goal.  Memory is simply
a list of precepts that has been stored by an agent.

In GOAP terminology, Memories replace Blackboards, but function differently.

_______________________________________________________________________________
### Ability
*Agents have abilities: ability to swing swords, walk, talk, puke, etc.*  

Abilities generate Contexts.  A collection of Abilities roughly forms what
GOAP calls "Action Sets".

_______________________________________________________________________________
### Context
*Context is an action, what is required, and what happens when it finishes.*  

Contexts are created by Abilities.  Contexts are dynamic and are unique to the
state of the Agent.

In GOAP terminology, a Context is roughly the same as an Action.

_______________________________________________________________________________
### Goal
*Goals are a condition that the Agent wants to satisfy.*  

Agents can have any number of Goals.  
Goals have:
* Relevance: determined by the goal itself
* A Test: the test determines if the goal is satisfied or not
* A Touch: change Memory by adding a precept

This is a huge divergence from GOAP.  Goals in pyGOAP are also used as prereqs
("preconditions") and effects.  This greatly simplifies the planner and removes
a huge duplication of code in building Abilities (GOAP "actions").

_______________________________________________________________________________
### Plan
*A sequence of Contexts.*

An Agent's planner will produce a Plan to satisfy a Goal.  Plans are created
when the Agent has a new Goal to satisfy.

_______________________________________________________________________________
### Agent
*Agents have the ability to plan and do actions.*  

Agents have abilities, goals, and memory.  They receive precepts from the
environment and give the environment actions that they wish to carry out.

Agents will search through all of it's Goals when it receives a new precept
and find the Goal that is most "relevant".  If the Goal has changed (or perhaps
there wasn't a goal in the first place), the Agent will attempt to create a
plan that satisfies the Goal.  If it cannot, it will simply try again once
a new precept is received from the environment.

_______________________________________________________________________________
### Environment
*Environments contain Agents and other objects.*  

Environments position things, execute actions, and distribute precepts.

_______________________________________________________________________________


## About the Demo
_______________________________________________________________________________

Please read the docstrings in main.py for more information.


## Reference
_______________________________________________________________________________

http://web.media.mit.edu/~jorkin/goap.html

Be sure to read Jeff Orkin's links starting from his 2003 draft.  This and
other resources can be found at the link above.