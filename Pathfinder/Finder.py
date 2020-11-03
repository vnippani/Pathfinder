size = 15
weight = 1
import queue

class priorityQueue(object):
    #create an empty minHeap
    def __init__(self):
        self.minHeap = [] 
        
    #build a heap from a given array of Coord objects, coords
    def buildHeap(self,coords):
        minHeap.append(None)
        for c in coords:
            self.minHeap.append(c)
            c.currentIndex = len(minHeap) - 1
        
        for i in range(len(minHeap)-1,-1,-1): #do heapify down on entire heap, starting from leaves
            self.heapifyDown(i)
        
    #insert a node into the min heap
    def insertNode(self,input):
        if input == None:
           return
        self.minHeap.append(input)
        
        self.heapifyUp(len(minHeap) - 1) #heapify up to rebalance heap
        
    #return root    
    def findMin(self):
        if len(self.minHeap) < 2:
            return None
        return self.minHeap[1]        

    #delete a single heap node
    def delete(self,index):
        if len(self.minHeap) == 1 or index >= len(self.minHeap):
            return
        
        if index != len(self.minHeap) - 1:
            maxCoord = self.minHeap[len(self.minHeap) - 1]
            maxCoord.currentIndex = index
            self.minHeap[index] = maxCoord
        self.minHeap.pop(len(self.minHeap) - 1) #end of list, complexity O(1)
        
        self.heapifyDown(index)
    
    #return and delete root
    def extractMin(self):
        if(len(self.minHeap) < 2):
            return None
        min = self.minHeap[1]     
        self.delete(1)
        return min
    
    #change the distance of a space that is in the heap
    def changeDist(self,c,newDist):
        index = c.currentIndex
        prevDist = c.minDist
        
        c.minDist = newDist
        
        if prevDist < newDist:
            self.heapifyDown(index)
        else:
            self.heapifyUp(index)
            
    #rebalance a node by moving it up the heap
    def heapifyUp(self,index):
        if index == 0:
            return
        
        
        parent = self.minHeap[index/2]
        swap = False
        #determine if a swap is needed
        if parent.minDist > self.minHeap[index].minDist:
            swap = True
        elif parent.minDist == self.minHeap[index].minDist:
            if parent.id > self.minHeap[index].id: #EDGE CASE: Use ID of spaces to decide
                swap = True
            
        #if swap is needed, swap elements in heap and call heapify up on parent index  
        if swap:
            c = self.minHeap[index]
            c.currentIndex = index / 2
            
            parent.currentIndex = index
            
            self.minHeap[index] = parent
            self.minHeap[index/2] = c
            
            heapifyUp(index/2)
            
    def heapifyDown(self,index):
        #if node is a leaf, return
        if index*2 >= len(self.minHeap):
            return
        
        smallestChild = None
        smallestChildIndex = 0
        #determine smallest child
        if index*2 + 1 >= len(self.minHeap): #this is case is if node has only one child
            smallestChild = self.minHeap[index*2]
            smallestChildIndex = index*2
        elif self.minHeap[index*2].minDist < self.minHeap[index*2+1].minDist:
            smallestChild = self.minHeap[index*2]
            smallestChildIndex = index*2
        elif self.minHeap[index*2].minDist > self.minHeap[index*2+1].minDist:
            smallestChild = self.minHeap[index*2+1]
            smallestChildIndex = index*2+1
        else:
            #EDGE CASES, distances equal, use IDs
            if self.minHeap[index*2].id < self.minHeap[index*2+1].id:
                smallestChild = self.minHeap[index*2]
                smallestChildIndex = index*2
            else:
                smallestChild = self.minHeap[index*2+1]
                smallestChildIndex = index*2+1
                
        swap = False
        
        #determine if a swap is needed
        if smallestChild.minDist < self.minHeap[index]:
            swap = True
        elif smallestChild.minDist < self.minHeap[index]:
            if smallestChild.id < self.minHeap[index].id:
                swap = True
            
        #if swap needed, perform swap and call heapify down again    
        if swap:
            current = self.minHeap[index]
            smallestChild.currentIndex = index
            current.currentIndex = smallestChildIndex
            
            self.minHeap[index] = smallestChild
            self.minHeap[smallestChildIndex] = current
            
            self.heapifyDown(smallestChildIndex)
        
class Coord(object):
    #grids are square grids exclusively
    def __init__(self, row, col, weight):
        self.id = size*row + col
        self.row = row
        self.col = col
        self.weight = weight
        self.currentIndex = -1
        self.minDist = 99999999999 #used in Dijkstras
        self.pi = None
        self.neighbors = []
        self.parent = None #used to indicate parent in BFS/DFS/SPT
        
    def reset(self):
        self.minDist = 99999999999
        self.pi = None


def main():
    coords = []
    #initialize coordinates
    for row in range(0,size):
        for col in range(0,size):
            c = Coord(row,col,weight)
            coords.append(c)
    
    #create neighbors array
    for row in range(0,size):
        for col in range(0,size):
            i = size*row + col #locate an element based on its row and col, find neighbors
            c = coords[i] #get the current element
            
            #determine all neighbors of the space
            if row - 1 >= 0:
                j = size*(row - 1) + col
                c.neighbors.append(coords[j])
            if row + 1 < size:
                j = size*(row + 1) + col
                c.neighbors.append(coords[j])
            if col - 1 >= 0:
                j = size*row + col - 1
                c.neighbors.append(coords[j])
            if col + 1 < size:
                j = size*row + col + 1
                c.neighbors.append(coords[j])
    
    walls = {}
    walls[4] = 0
    walls[5] = 0
    walls[6] = 0
    walls[21] = 0
    walls[14] = 0
    
    BFS(coords,224,1,walls)           
    print()
    DFS(coords,224,1,walls)

def BFS(coords,start,end,walls):
    """
    coords: grid of Coord objects
    start: id (or size*row + col) of start space
    end: id of end space
    """
    
    if start < 0 or start >= len(coords):
        return
    if end < 0 or end >= len(coords):
        return
    
    visited = {} #create visited hashmap and queue for spaces to explore
    q = queue.Queue()
    
    startNode = coords[start]
    q.put(startNode)
    visited[start] = 0
    
    result = None #the last node
    
    #BFS Algorithm
    while not q.empty():
        current = q.get()
        
        if current.id == end:
            result = current
            break
        
        for n in current.neighbors:
            if n.id not in visited and n.id not in walls:
                n.parent = current
                visited[n.id] = 0
                q.put(n)
    
                
    if result == None:
        print("err, no valid path")
    else:
        path = {}
        while result != None: #starting from end node, add path to hash map
            path[result.id] = 0
            result = result.parent
        
        #output the grid using print statements
        for row in range(0,size):
            for col in range(0,size):
                i = size * row + col
                if i == start:
                    print("s",end='')
                elif i == end:
                    print("e",end='')
                elif i in path:
                    print("*",end='')
                elif i in walls:
                    print("-",end='')
                else:
                    print(".",end='')              
            
            print()


def DFS(coords,start,end,walls):
    """
    coords: grid of Coord objects
    start: id (or size*row + col) of start space
    end: id of end space
    """
    if start < 0 or start >= len(coords):
        return
    if end < 0 or end >= len(coords):
        return 
    
    visited = {}
    result = DFSHelper(coords,start,end,visited,walls)
    
    if result == None:
        print("err, no valid path")
    else:
        path = {}
        while result != None: #starting from end node, add path to hash map
            path[result.id] = 0
            result = result.parent
        
        #output the grid using print statements
        for row in range(0,size):
            for col in range(0,size):
                i = size * row + col
                if i == start:
                    print("s",end='')
                elif i == end:
                    print("e",end='')
                elif i in path:
                    print("*",end='')
                elif i in walls:
                    print("-",end='')
                else:
                    print(".",end='')              
            
            print()
    
def DFSHelper(coords,current,end,visited,walls):
    """
    coords: grid of Coord objects
    current: id (or size*row + col) of current space
    end: id of end space
    visited: map containing visited nodes
    """
    visited[current] = 0
    
    if current == end:
        return coords[current]
        
    currentSpace = coords[current] #get the space corresponding to id current
    
    for n in currentSpace.neighbors:
        if n.id not in visited and n.id not in walls:
            n.parent = currentSpace
            newPath = DFSHelper(coords,n.id,end,visited,walls)
            if newPath != None:
                return newPath
            
    return None

def Dijkstra(coords,start,end,walls):
    pass

                        
main()           
            