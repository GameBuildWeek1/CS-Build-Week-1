# Sample Python code that can be used to generate rooms in
# a zig-zag pattern.
#
# You can modify generate_rooms() to create your own
# procedural generation algorithm and use print_rooms()
# to see the world.
import random
import time
from adventure.models import Player, Room

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
directionOffset = [vector2(-2,-1), vector2(-2,0), vector2(0,-2), vector2(-1,-2)];

class branch:
    def __init__(self, direction, x, y, decay, b_chance, dir_chance):
        #decay = chance for branch to die
        #chance = chance for creating a new branch
        #dir is the last direction traveled from;
        #room is the last room visited
        self.dir = direction;
        self.location = vector2(x,y);
        self.decay = decay;
        self.room_exit = 0;
        self.b_chance  = b_chance;
        self.dir_chance = dir_chance;
        self.room = None;
        self.room_step = -5;

    def try_branch(self): #should we branch
        b = random.random() > self.b_chance ;
        if(b == True):
            self.b_chance -= 0.01;
        else:
            self.b_chance += 0.5;
        return b;
        
    def create_room(self,world,branches,can_branch=True, force = False): #should we create a room here
            if(random.random() > 0.2 and force == False):
                world[self.location.y][self.location.x] = 1;
                return True;
            self.room_step = -2;
            r_size = vector2(random.randint(3,6),random.randint(3,6)) #get a random room size
            r_dir = directionOffset[self.dir];
            r_start = vector2(0,0);
            r_start.x = -random.randint(0,r_size.x-1) if r_dir.x == -2  else r_dir.x*r_size.x + (1 if self.dir == 2 else 0);
            r_start.y = -random.randint(0,r_size.y-1) if r_dir.y == -2  else r_dir.y*r_size.y +  (1 if self.dir == 1 else 0);
            r_start = self.location + r_start; #upper left location offset + location + one more move tile (for padding)
            if(r_start.x < 0 or r_start.y < 0):
                return self.draw_back(world); #to close to the edge of the map
            flag = False;
            try:
                for y in range(-1,r_size.y+1): #check area first add padding so we dont have a path that cuts tangent to a room
                    for x in range(-1,r_size.x+1): 
                        if(world[r_start.y + y][r_start.x + x] == 1):
                            world[self.location.y][self.location.x] = 1;
                            flag = True;
                            break;
                    if(flag == True):
                        break;
            except IndexError:
                return self.draw_back(world); #too close to the end of the map to do anything;
            if (flag == False):
                for y in range(r_size.y): #then apply;
                    for x in range(r_size.x):
                        world[r_start.y + y][r_start.x + x] = 1;

                world[self.location.y][self.location.x] = 1;
                self.location = directionValues[direction[self.dir]] + self.location;
                world[self.location.y][self.location.x] = 1;
                self.location = self.location + (r_size-1)*directionValues[direction[self.dir]];
                
                #offset the entrence and exit
                if(self.dir > 1):
                    self.location.y = r_start.y + random.randint(0,r_size.y);
                else:
                    self.location.x = r_start.x + random.randint(0,r_size.x);
            
                if(can_branch == True):
                    world[self.location.y][self.location.x] = 1
                if(can_branch==False):
                    return False;
                if(self.try_branch() == False):
                    return True;
                b = 0;
                if(self.dir < 2):
                    b = 2;

                for i in range(b,b+2): #try to add a branch in every cardinal direction of the room;
                    loc = vector2(r_start.x, r_start.y);
                    if(i == 0):
                        loc.x += random.randint(0,r_size.x-1);
                    elif(i == 1):
                        loc.x += random.randint(0,r_size.x-1);
                        loc.y += r_size.y-1;
                    elif(i == 3):
                        loc.y += random.randint(0,r_size.y-1);
                    elif(i == 2):
                        loc.y += random.randint(0,r_size.y-1);
                        loc.x += r_size.x-1;
                    dir = directionValues[direction[i]];
                    #world[loc.y][loc.x] = 2;
                    brn = branch(i,loc.x, loc.y ,random.randint(100,200), random.random()*0.1, random.random()*0.2)
                    branches.append(brn);
                
                return True;
            world[self.location.y][self.location.x] = 1;
            return True;

    def change_direction(self): #get a new direction for branching and for general direction change
        if(self.dir == 0 or self.dir == 1):
            return random.randint(2,3);
        if(self.dir == 2 or self.dir == 3):
            return random.randint(0,1);
        return self.dir;
    def draw_back(self,world): #draw back if i hit the end of the world so we dont get weird dead ends
        dir = directionValues[direction[self.dir]] * -1; #inverse my direction
        self.location.x = min(max(self.location.x, 0), len(world[0]));
        self.location.y = min(max(self.location.y, 0), len(world));
        for i in range(max(len(world),len(world[0]))+1):
            count = 0;
            i_loc = None;
            for i in range(4):
                loc = self.location + directionValues[direction[i]];
                try:
                    if(world[loc.y][loc.x] == 1 and loc.x > -1 and loc.y > -1):
                        count+=1;
                        i_loc = loc;
                except:
                    pass;
            if(count > 1):
                break;
            try:
                world[self.location.y][self.location.x] = 0;
            except:
                pass;
            if(i_loc is None):
                print("error");
                break;
            self.location = i_loc;
        return False;

    def move(self, world, branches): #main looop 
        #decay branch if decay is low then have a chance of removing branch
        self.decay -= 1;
        self.location = self.location + directionValues[direction[self.dir]]
        if(self.decay < 10):
            if random.randint(0, self.decay) == 0:
                self.create_room(world,branches,False,True);
                return self.draw_back(world);
        change = False;
        if(self.dir_chance > random.random()):
            self.dir = self.change_direction();
            change = True;
        
        if self.location.y < 0 or self.location.x < 0: #if x becomes negitive it looks at the back of the list which we dont want;
            return self.draw_back(world); #always returns false
        try:
            if world[self.location.y][self.location.x] == 1:
                return False;
            if(self.dir > 1 and change == False):
                for y in range(-1, 2, 2): #check to see if we are tangent to a room n s
                    if(world[self.location.y + y][self.location.x] == 1):
                        world[self.location.y][self.location.x] = 1;
                        return False;
            elif(change == False): 
                for x in range(-1, 2, 2): #same but e w
                    if(world[self.location.y][self.location.x + x] == 1):
                        world[self.location.y][self.location.x] = 1;
                        return False;
        except:
            return self.draw_back(world); #always returns false
        self.room_step += 1;
        if(self.room_step > 0):
            return self.create_room(world,branches);
        world[self.location.y][self.location.x] = 1;
        return True;


class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.rooms = []
        self.home = None;
    def create_spawn_room(self, sx,sy):
        self.home = vector2(sx,sy);
        r_start = vector2(sx-2, sy-2);
        r_size = vector2(5,5);
        for y in range(r_size.y):
            for x in range(r_size.x):
                self.grid[r_start.y+y][r_start.x+x] = 1;
        self.grid[self.home.y][self.home.x] = "S";
        return [branch(i,sx+2*directionValues[direction[i]].x,sy+2*directionValues[direction[i]].y, 1000, random.random()*0, random.random()*0.1) for i in range(4)]
    def generate_rooms(self, size_x, size_y, num_rooms, startx=-1, starty=-1, seed=None):
        #check if not set or to close to the edge
        if(startx < 5):
            startx = size_x //2;
        if(starty < 5):
            starty = size_y //2;
        '''
        Fill up the grid, bottom to top, in a zig-zag pattern
        '''
        #reset everything

        if(not seed is None):
            random.seed(seed); #assign seed so we can have more control
        self.__init__();

        self.width = size_x;
        self.height = size_y;
        self.grid = [[0 for j in range(size_x)] for i in range(size_y)] 
        branches = self.create_spawn_room(startx, starty);
        
        while(len(branches) > 0):
            remove = []
            new_b = []
            for b in range(len(branches)):
                #add new branch? changed to the move function
                """ if(branches[b].try_branch() and len(self.rooms) < num_rooms):
                    brnch = branch(branches[b].change_direction(),branches[b].location.x, branches[b].location.y,random.randint(10,100),random.random()*0.1+0.4, random.random()*0.0);
                    new_b.append(brnch)
                    brnch.room = branches[b].room; """
                
                #main branch loop
                m = branches[b].move(self.grid,new_b);

                #remove branch?
                if(m == False):
                    remove.append(b);

            #apply removes
            branches = [branches[b] for b in range(len(branches)) if not b in remove ]

            #apply new branches
            if(len(new_b) > 0):
                branches += new_b;
            
            #optional step by step print out
            """self.print_rooms();
            time.sleep(1/12); """
        flag = False;
        #create an exit
        for i in range(1000):
            x = random.randint(0,size_x);
            y = random.randint(0,size_y);
            try:
                if(self.grid[y][x] == 0):
                    raise;
                count = 0;
                for i in range(4):
                    loc = vector2(x,y);
                    loc = loc + directionValues[direction[i]];
                    if(not self.grid[loc.y][loc.x] == 0):
                        count += 1;
                if(count < 4):
                    raise;
            except:
                continue;
            if ((size_x//3)**2 + (size_y//3)**2) < (x - self.home.x)**2 + (y - self.home.y)**2:
                self.grid[y][x] = "E";
                flag = True;
                break;
        if(flag == False):
            return self.generate_rooms(size_x,size_y,num_rooms,random.randint(size_x//4, (3*size_x)//4),random.randint(size_y//4, (3*size_y)//4));
        
    def print_rooms(self, pos=[]):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        # Add top border
        string = "⬛" * ((self.width) + 2) + "\n"
        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        #reverse_grid = [[random.randint(0,1) for i in range(self.width)]for i in range(self.height)]
        for row in range(len(reverse_grid)):
            string += "#";
            for tile in range(len(reverse_grid[row])):
                flag = False;
                for p in pos:
                    if(isinstance(p,vector2) and p.x == tile and p.y == row):
                        string += "P"
                        flag = True
                        break;
                if(flag == True):
                    continue;
                elif(reverse_grid[row][tile] == 1):
                    string += " "
                elif(reverse_grid[row][tile] == 0):
                    string += "X"
                else:
                    string += str(reverse_grid[row][tile]);

            string += "#\n"
        #reverse_grid.reverse()
        """ for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            string += "#"
            for room in row:
                if room is not None and room.n_to is not None:
                    string += "  |  "
                else:
                    string += "     "
            string += "#\n"
            # PRINT ROOM ROW
            string += "#"
            for room in row:
                if room is not None and room.w_to is not None:
                    string += "-"
                else:
                    string += " "
                if room is not None:
                    string += f"{room.id}".zfill(3)
                else:
                    string += "   "
                if room is not None and room.e_to is not None:
                    string += "-"
                else:
                    string += " "
            string += "#\n"
            # PRINT SOUTH CONNECTION ROW
            string += "#"
            for room in row:
                if room is not None and room.s_to is not None:
                    string += "  |  "
                else:
                    string += "     "
            string += "#\n" """

        # Add bottom border
        string += "⬛" * ((self.width) + 2) + "\n";
        # Print stringing
        print(string);
        
if(__name__ == "__main__"):
    world = [];
    for i in range(4):
        w = World()
        num_rooms = 1000
        width = int(2**(5.5+(i*0.5)));
        height = int(2**(4.5+(i*0.5)));
        w.generate_rooms(width, height, num_rooms, random.randint(width//4, (3*width)//4),random.randint(height//4, (3*height)//4));
        w.print_rooms([vector2(0,0), vector2(1,0)]);
        world.append(w.grid);
    
        #print(w.grid);
        #time.sleep(2);
        ##print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {len(w.rooms)}\n")
    #print(world);
