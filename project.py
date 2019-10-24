import sys
import os


for x in os.walk("./"):
        if(x[0][0] == '.' or x[0][0] == "_"):
                continue;
        sys.path.append('./' + x[0]);
	
	
