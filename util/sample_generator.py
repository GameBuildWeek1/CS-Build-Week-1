# Sample Python code that can be used to generate rooms in
# a zig-zag pattern.
#
# You can modify generate_rooms() to create your own
# procedural generation algorithm and use print_rooms()
# to see the world.
import random
import time

class vector2:
    def __init__(self, x=0, y=0):
        self.x = x;
        self.y = y;
    def __add__(self,other):
        try:
            return vector2(self.x+other.x, self.y+ other.y);
        except:
            return vector2(self.x + other, self.y + other);
    def __sub__(self,other):
        try:
            return vector2(self.x-other.x, self.y-other.y);
        except:
            return vector2(self.x - other, self.y - other);
    def __mul__(self,other):
        try:
            return vector2(self.x*other.x, self.y*other.y);
        except:
            return vector2(self.x * other, self.y * other);
    def __truediv__(self,other):
        try:
            return vector2(self.x/other.x, self.y/other.y);
        except:
            return vector2(self.x / other, self.y / other);
    def __iadd__(self, other):
        self = self.__add__(other);
    def __isub__(self, other):
        self = self.__sub__(other);
    def __imul__(self, other):
        self = self.__mul__(other);
    def __idiv__(self, other):
        self = self.__truediv__(other);
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y;
    def __str__(self):
        return "x: " + str(self.x) + " y: " + str(self.y);

class Room:
    def __init__(self,id, name, description, x, y):
        self.id = id
        self.name = name
        self.description = description
        self.n_to = None
        self.s_to = None
        self.e_to = None
        self.w_to = None
        self.x = x
        self.y = y
    def __repr__(self):
        if self.e_to is not None:
            return f"({self.x}, {self.y}) -> ({self.e_to.x}, {self.e_to.y})"
        return f"({self.x}, {self.y})"
    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"{direction}_to", connecting_room)
        setattr(connecting_room, f"{reverse_dir}_to", self)
    def get_room_in_direction(self, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        return getattr(self, f"{direction}_to")

directionValues = {"n": vector2(0,-1), "s": vector2(0,1), "e": vector2(1,0), "w": vector2(-1,0)}
direction = ["n","s","e","w"]


class branch:
    def __init__(self, direction, x, y, decay, b_chance, dir_chance):
        #decay = chance for branch to die
        #chance = chance for creating a new branch
        #dir is the last direction traveled from;
        #room is the last room visited
        self.dir = direction;
        self.location = vector2(x,y);
        self.decay = decay;
        self.b_chance  = b_chance;
        self.dir_chance = dir_chance;
        self.room = None;

    def try_branch(self):
        b = random.random() > self.b_chance ;
        if(b == True):
            self.b_chance -= 0.01;
        else:
            self.b_chance += 0.5;
        return b;

    def change_direction(self):
        if(self.dir == 0 or self.dir == 1):
            return random.randint(2,3);
        if(self.dir == 2 or self.dir == 3):
            return random.randint(0,1);
        return self.dir;

    def move(self, rooms):
        #decay branch if decay is low then have a chance of removing branch
        self.decay -= 1;
        if(self.decay < 10):
            if random.randint(0, self.decay) == 0:
                return None;
        if(self.dir_chance > random.random()):
            self.dir = self.change_direction();

        self.location = self.location + directionValues[direction[self.dir]]
        
        if self.location.y < 0 or self.location.x < 0: #if x becomes negitive it looks at the back of the list which we dont want;
            return None;
        try:
            if not rooms[self.location.y][self.location.x] == None:
                self.room.connect_rooms(rooms[self.location.y][self.location.x], direction[self.dir]);
                return None;
        except:
                return None;
        temp = self.room;
        self.room = Room(self.location.x*10 + self.location.y,"Room " + str(self.location.x) + str(self.location.y), "hello", self.location.x, self.location.y);
        if(not temp == None):
            temp.connect_rooms(self.room, direction[self.dir]);
        return self.room;


class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.rooms = []
        self.home = None;
    def generate_rooms(self, size_x, size_y, num_rooms):
        '''
        Fill up the grid, bottom to top, in a zig-zag pattern
        '''
        self.__init__();
        self.width = size_x;
        self.height = size_y;
        branches = [branch(i,size_x//2,size_y//2,num_rooms, random.random()*0.1+0.1, random.random()*0.1+0.1) for i in range(4)]
        self.grid = [[None for j in range(size_x)] for i in range(size_y)] 
        self.rooms.append(Room(0000, "Starting Point", "This is where you start",size_x//2,size_y//2))
        self.grid[size_y//2][size_x//2] = self.rooms[0];
        for i in branches:
            i.room = self.rooms[0];
        self.home = self.rooms[0];
        while(len(branches) > 0):
            remove = []
            new_b = []
            for b in range(len(branches)):
                if(branches[b].try_branch() and len(self.rooms) < num_rooms and not branches[b].room == None ):
                    brnch = branch(branches[b].change_direction(),branches[b].location.x, branches[b].location.y,random.randint(10,100),random.random()*0.2, random.random()*0.9);
                    new_b.append(brnch)
                    brnch.room = branches[b].room;
                m = branches[b].move(self.grid);
                if(m == None):
                    remove.append(b);
                else:
                    try:
                        self.grid[branches[b].location.y][ branches[b].location.x] = m;
                    except:
                        remove.append(b);
                        continue;
                    self.rooms.append(m);
            #self.print_rooms();
            #time.sleep(2);
            branches = [branches[b] for b in range(len(branches)) if not b in remove ]
            if(len(new_b) > 0):
                branches += new_b;

    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        # Add top border
        str = "# " * ((3 + self.width * 5) // 2) + "\n"

        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        #reverse_grid.reverse()
        for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.n_to is not None:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to is not None:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to is not None:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to is not None:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"

        # Add bottom border
        str += "# " * ((3 + self.width * 5) // 2) + "\n"

        # Print string
        print(str)

""" w = World()
num_rooms = 1000
width = 42
height = 16
w.generate_rooms(width, height, num_rooms) """
##w.print_rooms()
##time.sleep(2);
##print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {len(w.rooms)}\n")
