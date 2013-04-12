""""Implement Agents and Environments (Chapters 1-2).

The class hierarchies are as follows:

Object ## A physical object that can exist in an environment
    Agent
        Wumpus
        RandomAgent
        ReflexVacuumAgent
        ...
    Dirt
    Wall
    ...
    
Environment ## An environment holds objects, runs simulations
    XYEnvironment
        VacuumEnvironment
        WumpusEnvironment

EnvGUI ## A window with a graphical representation of the Environment

EnvToolbar ## contains buttons for controlling EnvGUI

EnvCanvas ## Canvas to display the environment of an EnvGUI

"""
from utils import *
import random, copy

#______________________________________________________________________________


class Object (object):
    """This represents any physical object that can appear in an Environment.
    You subclass Object to get the objects you want.  Each object can have a
    .__name__  slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

    def is_alive(self):
        """Objects that are 'alive' should return true."""
        return hasattr(self, 'alive') and self.alive
		
class Agent (Object):
    """An Agent is a subclass of Object with one required slot,
    .program, which should hold a function that takes one argument, the
    percept, and returns an action. (What counts as a percept or action
    will depend on the specific environment in which the agent exists.) 
    Note that 'program' is a slot, not a method.  If it were a method,
    then the program could 'cheat' and look at aspects of the agent.
    It's not supposed to do that: the program can only look at the
    percepts.  An agent program that needs a model of the world (and of
    the agent itself) will have to build and maintain its own model.
    There is an optional slots, .performance, which is a number giving
    the performance measure of the agent in its environment."""

    def __init__(self):
        self.program = self.make_agent_program()
        self.alive = True
        self.bump = False

    def make_agent_program(self):
        
        def program(percept):
            return raw_input('Percept=%s; action? ' % percept)
        return program
	
def TraceAgent(agent):
    """Wrap the agent's program to print its input and output. This will let
    you see what the agent is doing in the environment."""
    old_program = agent.program
    def new_program(percept):
        action = old_program(percept)
        print '%s perceives %s and does %s' % (agent, percept, action)
        return action
    agent.program = new_program
    return agent

class RandomAgent (Agent):
    "An agent that chooses an action at random, ignoring all percepts."

    def __init__(self, actions):
        self.actions = actions
        super(RandomAgent, self).__init__()

    def make_agent_program(self):
        actions = self.actions
        return lambda percept: random.choice(actions)


#______________________________________________________________________________

loc_A, loc_B = (1, 1), (2, 1) # The two locations for the Vacuum world

class ReflexVacuumAgent (Agent):
    "A reflex agent for the two-state vacuum environment. [Fig. 2.8]"

    def __init__(self):
        super(ReflexVacuumAgent, self).__init__()

    def make_agent_program(self):
        def program((location, status)):
            print 'status'
            print status
            print 'location'
            print location
            
            #if status == 'Dirty':
            if location == 'Dirty':
                print 'XXXXX'
                return 'Suck'
            #elif location == loc_A: return 'Right'
            #elif location == loc_B: return 'Left'
            #elif location == 'Left' || location    elif location == 'Right': return 'Left'
        return program

def RandomVacuumAgent():
    "Randomly choose one of the actions from the vacuum environment."
    return RandomAgent(['Right', 'Left', 'Suck', 'NoOp'])

	
class Environment (object):
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this. Your Environment will typically need to implement:
        percept:           Define the percept that an agent sees.
        execute_action:    Define the effects of executing an action.
                           Also update the agent.performance slot.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    Each object has a .location slot, even though some environments may not
    need this."""

    def __init__(self):
        self.objects = []
        self.agents = []

    def object_classes(self):
        return [] ## List of classes that can go into environment

    def percept(self, agent):
        "Return the percept that the agent sees at this point. Override this."
        abstract

    def execute_action(self, agent, action):
        "Change the world to reflect this action. Override this."
        abstract

    def default_location(self, object):
        "Default location to place a new object with unspecified location."
        return None

    def is_done(self):
        "By default, we're done when we can't find a live agent."
        for agent in self.agents:
            if agent.is_alive(): return False
        return True
    
    def exogenous_change(self):
        "If there is spontaneous change in the world, override this."
        pass

    def step(self):
        """Run the environment for one time step. If the
        actions and exogenous changes are independent, this method will
        do.  If there are interactions between them, you'll need to
        override this method."""
        if not self.is_done():
                actions = [agent.program(self.percept(agent))
                           for agent in self.agents]
                for (agent, action) in zip(self.agents, actions):
                    self.execute_action(agent, action)
                self.exogenous_change()

    def run(self, steps=1000):
        """Run the Environment for given number of time steps."""
        for step in range(steps):
                if self.is_done(): return
                self.step()

    def list_objects_at(self, location, oclass=Object):
        "Return all objects exactly at a given location."
        return [obj for obj in self.objects
                if obj.location == location and isinstance(obj, oclass)]
    
    def some_objects_at(self, location, oclass=Object):
        """Return true if at least one of the objects at location
        is an instance of class oclass.

        'Is an instance' in the sense of 'isinstance',
        which is true if the object is an instance of a subclass of oclass."""

        return self.list_objects_at(location, oclass) != []

    def add_object(self, obj, location=None):
        """Add an object to the environment, setting its location. Also keep
        track of objects that are agents.  Shouldn't need to override this."""

        obj.location = location or self.default_location(obj)
        
        if isinstance(obj, Agent):
                obj.performance = 0
                self.agents.append(TraceAgent(obj))
        else:
            self.objects.append(obj)
        return self

    def delete_object(self, obj):
        """Remove an object from the environment."""
        try:
            self.objects.remove(obj)
        except ValueError, e:
            print e
            print "  in Environment delete_object"
            print "  Object to be removed: %s at %s" % (obj, obj.location)
            trace_list("  from list", self.objects)
        if obj in self.agents:
            self.agents.remove(obj)


def trace_list (name, objlist):
    ol_list = [(obj, obj.location) for obj in objlist]
    print "%s: %s" % (name, ol_list)

class XYEnvironment (Environment):
    """This class is for environments on a 2D plane, with locations
    labelled by (x, y) points, either discrete or continuous.

    Agents perceive objects within a radius.  Each agent in the
    environment has a .location slot which should be a location such
    as (0, 1), and a .holding slot, which should be a list of objects
    that are held."""

    def __init__(self, width=10, height=10):
        super(XYEnvironment, self).__init__()
        self.width = width
        self.height = height
        #update(self, objects=[], agents=[], width=width, height=height)
        self.observers = []
        
    def objects_near(self, location, radius):
        "Return all objects within radius of location."
        radius2 = radius * radius
        return [obj for obj in self.objects
                if distance2(location, obj.location) <= radius2]

    def percept(self, agent):
        "By default, agent perceives objects within radius r."
        

    def execute_action(self, agent, action):
        print agent
        print action
        print "Action"
        print action
        agent.bump = False
        actual_pos = agent.location
        if action == 'Right':            
            new_pos = (actual_pos[0]+1, actual_pos[1])
            self.move_to(agent, new_pos)
        elif action == 'Left':            
            new_pos = (actual_pos[0]-1, actual_pos[1])
            self.move_to(agent, new_pos)
        elif action == 'Up':            
            new_pos = (actual_pos[0], actual_pos[1]-1)
            self.move_to(agent, new_pos)
        elif action == 'Down':            
            new_pos = (actual_pos[0], actual_pos[1]+1)
            self.move_to(agent, new_pos)
            #agent.heading = self.turn_heading(agent.heading, -1)
        #elif action == 'Left':
        #    agent.heading = self.turn_heading(agent.heading, +1)
        #elif action == 'Forward':
        #    self.move_to(agent, vector_add(agent.heading, agent.location))
#         elif action == 'Grab':
#             objs = [obj for obj in self.list_objects_at(agent.location)
#                     if agent.can_grab(obj)]
#             if objs:
#                 agent.holding.append(objs[0])
        #elif action == 'Release':
         #   if agent.holding:
        #5      agent.holding.pop()

    def object_percept(self, obj, agent): #??? Should go to object?
        "Return the percept for this object."
        return obj.__class__.__name__

    def default_location(self, object):
        return (random.choice(self.width), random.choice(self.height))

    def move_to(self, obj, destination):
        "Move an object to a new location."

        # Bumped?
        obj.bump = self.some_objects_at(destination, Obstacle)

        if not obj.bump:
            # Move object and report to observers
            obj.location = destination
            for o in self.observers:
                o.object_moved(obj)
        
    def add_object(self, obj, location=(1, 1)):
        print obj
        print location
        super(XYEnvironment, self).add_object(obj, location)
        obj.holding = []
        obj.held = None
        # self.objects.append(obj) # done in Environment!
        # Report to observers
        for obs in self.observers:
            obs.object_added(obj)

    def delete_object(self, obj):
        super(XYEnvironment, self).delete_object(obj)
        # Any more to do?  Object holding anything or being held?
        for obs in self.observers:
            obs.object_deleted(obj)
    
    def add_walls(self):
        "Put walls around the entire perimeter of the grid."
        for x in range(self.width):
            self.add_object(Wall(), (x, 0))
            self.add_object(Wall(), (x, self.height-1))
        for y in range(self.height-1):
            if y != 0:
                self.add_object(Wall(), (0, y))
                self.add_object(Wall(), (self.width-1, y))

    def add_observer(self, observer):
        """Adds an observer to the list of observers.  
        An observer is typically an EnvGUI.
        
        Each observer is notified of changes in move_to and add_object,
        by calling the observer's methods object_moved(obj, old_loc, new_loc)
        and object_added(obj, loc)."""
        self.observers.append(observer)
        
    def turn_heading(self, heading, inc,
                     headings=[(1, 0), (0, 1), (-1, 0), (0, -1)]):
        "Return the heading to the left (inc=+1) or right (inc=-1) in headings."
        return headings[(headings.index(heading) + inc) % len(headings)]  

class Obstacle (Object):
    """Something that can cause a bump, preventing an agent from
    moving into the same square it's in."""
    pass

class Wall (Obstacle):
    pass

#______________________________________________________________________________
## Vacuum environment 

class Dirt (Object):
    pass
    
class VacuumEnvironment (XYEnvironment):
    """The environment of [Ex. 2.12]. Agent perceives dirty or clean,
    and bump (into obstacle) or not; 2D discrete world of unknown size;
    performance measure is 100 for each dirt cleaned, and -1 for
    each turn taken."""

    def __init__(self, width=10, height=10):
        super(VacuumEnvironment, self).__init__(width, height)
        self.add_walls()

    def object_classes(self):
        return [Wall, Dirt, ReflexVacuumAgent, RandomVacuumAgent, SimpleReflexAgent]

    def percept(self, agent):
        """The percept is a tuple of ('Dirty' or 'Clean', 'Bump' or 'None').
        Unlike the TrivialVacuumEnvironment, location is NOT perceived."""
        print 
        status = if_(self.some_objects_at(agent.location, Dirt),
                     'Dirty', 'Clean')        
        return (status, agent.location)

    def execute_action(self, agent, action):
        if action == 'Suck':
            dirt_list = self.list_objects_at(agent.location, Dirt)
            if dirt_list != []:
                dirt = dirt_list[0]
                agent.performance += 100
                self.delete_object(dirt)
        else:
            super(VacuumEnvironment, self).execute_action(agent, action)

        if action != 'Nop':
            agent.performance -= 1
#______________________________________________________________________________

class SimpleReflexAgent (Agent):
    """This agent takes action based solely on the percept. [Fig. 2.13]"""

    def __init__(self):                
        super(SimpleReflexAgent, self).__init__()

    def make_agent_program(self):        
        def program(percept):
            print 'percept%s', percept
            if percept[0] == 'Dirty':
                return 'Suck'
            elif percept[0] == 'Clean':
                return random.choice(['Left','Right','Up','Down'])                            
        return program

def rule_match(state, rules):
    "Find the first rule that matches state."
    for rule in rules:
        if rule.matches(state):
            return rule
def compare_agents(EnvFactory, AgentFactories, n=10, steps=1000):
    """See how well each of several agents do in n instances of an environment.
    Pass in a factory (constructor) for environments, and several for agents.
    Create n instances of the environment, and run each agent in copies of 
    each one for steps. Return a list of (agent, average-score) tuples."""
    envs = [EnvFactory() for i in range(n)]
    return [(A, test_agent(A, steps, copy.deepcopy(envs))) 
            for A in AgentFactories]

def test_agent(AgentFactory, steps, envs):
    "Return the mean score of running an agent in each of the envs, for steps"
    total = 0
    for env in envs:
        agent = AgentFactory()
        env.add_object(agent)
        env.run(steps)
        total += agent.performance
    return float(total)/len(envs)

#_________________________________________________________________________

__doc__ += """
"""

#______________________________________________________________________________
# GUI - Graphical User Interface for Environments
# If you do not have Tkinter installed, either get a new installation of Python
# (Tkinter is standard in all new releases), or delete the rest of this file
# and muddle through without a GUI.

import Tkinter as tk

class EnvFrame(tk.Tk, object):

    def __init__(self, env, title = 'AIMA GUI', cellwidth=50, n=10):

        # Initialize window

        super(EnvFrame, self).__init__()
        self.title(title)

        # Create components

        canvas = EnvCanvas(self, env, cellwidth, n)
        toolbar = EnvToolbar(self, env, canvas)
        for w in [canvas, toolbar]:
            w.pack(side="bottom", fill="x", padx="3", pady="3")

        canvas.pack()
        toolbar.pack()
        tk.mainloop()

class EnvToolbar(tk.Frame, object):

    def __init__(self, parent, env, canvas):
        super(EnvToolbar, self).__init__(parent, relief='raised', bd=2)

        # Initialize instance variables

        self.env = env
        self.canvas = canvas
        self.running = False
        self.speed = 1.0

        # Create buttons and other controls

        for txt, cmd in [('Step >', self.env.step),
                         ('Ejecutar >>', self.run),
                         ('Detener [ ]', self.stop),
                         ('Listar objetos', self.list_things),
                         ('Listar agentes', self.list_agents)]:
            tk.Button(self, text=txt, command=cmd).pack(side='left')

        tk.Label(self, text='Speed').pack(side='left')
        scale = tk.Scale(self, orient='h',
                         from_=(1.0), to=10.0, resolution=1.0,
                         command=self.set_speed)
        scale.set(self.speed)
        scale.pack(side='left')

    def run(self):
        print 'run'
        self.running = True
        self.background_run()

    def stop(self):
        print 'stop'
        self.running = False

    def background_run(self):
        if self.running:
            self.env.step()
            # ms = int(1000 * max(float(self.speed), 0.5))
            #ms = max(int(1000 * float(self.delay)), 1)
            delay_sec = 1.0 / max(self.speed, 1.0) # avoid division by zero
            ms = int(1000.0 * delay_sec)  # seconds to milliseconds
            self.after(ms, self.background_run)

    def list_things(self):
        print "Objetos en el ambiente:"
        for thing in self.env.objects:
            print "%s at %s" % (thing, thing.location)

    def list_agents(self):
        print "Agentes en el ambiente"
        for agt in self.env.agents:
            print "%s at %s" % (agt, agt.location)

    def set_speed(self, speed):
        self.speed = float(speed)
        
class EnvCanvas (tk.Canvas, object):

    def __init__ (self, parent, env, cellwidth, n):
        canvwidth = cellwidth * n # (cellwidth + 1 ) * n
        canvheight = cellwidth * n # (cellwidth + 1) * n
        super(EnvCanvas, self).__init__(parent, background="white",
                                        width=canvwidth, height=canvheight)

        # Initialize instance variables
        
        self.env = env
        self.cellwidth = cellwidth
        self.n = n

        # Draw the gridlines
        
        if cellwidth:
            for i in range(0, n+1):
                self.create_line(0, i*cellwidth, n*cellwidth, i*cellwidth)
                self.create_line(i*cellwidth, 0, i*cellwidth, n*cellwidth)
                self.pack(expand=1, fill='both')
        self.pack()

        # Set up image dictionary.

        # Ugly hack: we need to keep a reference to each ImageTk.PhotoImage,
        # or it will be garbage collected.  This dictionary maps image files
        # that have been opened to their PhotoImage objects
        self.images = []
        self.imagesObj = []

        # Bind canvas events.
        
        self.bind('<Button-1>', self.user_left) ## What should this do?
        self.bind('<Button-2>', self.user_edit_objects)        
        self.bind('<Button-3>', self.user_add_object)


        for obst in self.env.objects:
            if isinstance(obst, Wall):
                imgwall=tk.PhotoImage(file=r"images\wall-icon.gif")                                                            
            else:
                imgwall=tk.PhotoImage(file=r"images\dirt05-icon.gif")
            test = [imgwall, obst.location]
            self.imagesObj.append(test)

        for imgO in self.imagesObj:
            self.create_image(self.cell_topleft_xy(imgO[1]), anchor="nw", image=imgO[0])


   # for obs in self.env.objects:
        #dibujar ob    
    def user_left(self, event):
        print 'left at %d, %d' % self.event_cell(event)

    def user_edit_objects(self, event):
        """Choose an object within radius and edit its fields."""
        pass

    def user_add_object(self, event):
        """Pops up a menu of Object classes; you choose the
        one you want to put in this square."""
        cell = self.event_cell(event)
        xy = self.cell_topleft_xy(cell)
        menu = tk.Menu(self, title='Edit (%d, %d)' % cell)
        # Generalize object classes available,
        # and why is self.run the command?
        #for (txt, cmd) in [('Wumpus', self.run), ('Pit', self.run)]:
        #    menu.add_command(label=txt, command=cmd)
        obj_classes = self.env.object_classes()
        
        
        def draw_agent(agentType):
            def draw ():
                print agentType

                obj = agentType()
                
                self.env.add_object(obj, cell)
                
                print "Drawing agent %s at cell %s xy %s" % (obj, cell, xy)                
                if isinstance(obj, ReflexVacuumAgent):
                    tk_image=tk.PhotoImage(file=r"images\vacuum-icon.gif")
                    self.images.append(tk_image)
                elif isinstance(obj, RandomAgent):
                    tk_image=tk.PhotoImage(file=r"images\vacuum-icon.gif")
                    self.images.append(tk_image)
                elif isinstance(obj, Wall):
                    tk_image=tk.PhotoImage(file=r"images\wall-icon.gif")
                    self.images.append(tk_image)
                elif isinstance(obj, Dirt):
                    tk_image=tk.PhotoImage(file=r"images\dirt05-icon.gif")
                    self.images.append(tk_image)
                else:
                    tk_image=tk.PhotoImage(file=r"images\vacuum-icon.gif")
                    self.images.append(tk_image)
                
                
                for img in self.images:
                    self.create_image(xy, anchor="nw", image=img)                
                                    
            return draw

        for agentType in obj_classes:
            menu.add_command(label=agentType.__name__, command=draw_agent(agentType))
            
        menu.tk_popup(event.x + self.winfo_rootx(),
                      event.y + self.winfo_rooty())
        
    def event_cell (self, event):
        return self.xy_cell((event.x, event.y))

    def xy_cell (self, (x, y)):
        """Given an (x, y) on the canvas, return the row and column
        of the cell containing it."""
        w = self.cellwidth
        return x / w, y / w
    
    def cell_topleft_xy (self, (row, column)):
        """Given a (row, column) tuple, return the (x, y) coordinates
        of the cell(row, column)'s top left corner."""

        w = self.cellwidth
        return w * row, w * column
    
v = VacuumEnvironment();
w = EnvFrame(v);
