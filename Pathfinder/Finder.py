import queue
import math
import pygame

#set pygame screen settings
WIDTH = 600
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("Pathfinder")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

size = 25

SPOTWIDTH = WIDTH / size

setting = 0

#by default, all spaces have an edge weight of 1 (abs(2-1) == abs(1-2)) 
weight1 = 1 
weight2 = 2

class Spot(object):
	
	def __init__(self,row,col,width):
		self.row = row
		self.col = col
		self.x = col * SPOTWIDTH
		self.y = row * SPOTWIDTH
		self.color = WHITE
		self.width = width
		self.minDist = 99999999999 #used in Dijkstras
		self.pi = None #used to indicate parent in BFS/DFS/SPT
		self.neighbors = []
		self.currentIndex = -1
		
	def get_pos(self):
		return self.row, self.col
	
	def is_visited(self):
		return self.color == RED 
	
	def is_open(self):
		return self.color == GREEN
	
	def is_Wall(self):
		return self.color == BLACK
	
	def is_end(self):
		return self.color == TURQUOISE
	
	def reset(self):
		self.color = WHITE
		
	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	
class priorityQueue(object):
	#create an empty minHeap
	def __init__(self):
		self.minHeap = [] 
		
	#build a heap from a given array of Coord objects, coords
	def buildHeap(self,coords,walls):
		self.minHeap.append(None)
		for c in coords:
			if c.id not in walls:
				self.minHeap.append(c)
				c.currentIndex = len(self.minHeap) - 1
		
		for i in range(len(self.minHeap)-1,0,-1): #do heapify down on entire heap, starting from leaves
			self.heapifyDown(i)

	def getSize(self):
		return len(self.minHeap)
	
	#insert a node into the min heap
	def insertNode(self,input):
		if input == None:
		   return
		self.minHeap.append(input)
		
		self.heapifyUp(len(self.minHeap) - 1) #heapify up to rebalance heap
		
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
		if index == 1:
			return
		
		
		parent = self.minHeap[index//2]
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
			c.currentIndex = index // 2
			
			parent.currentIndex = index
			
			self.minHeap[index] = parent
			self.minHeap[index//2] = c
			
			self.heapifyUp(index//2)
			
	def heapifyDown(self,index):
		#if node is a leaf, return
		if index*2 >= len(self.minHeap):
			return
		
		smallestChild = None
		smallestChildIndex = 1
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
		if smallestChild.minDist < self.minHeap[index].minDist:
			swap = True
		elif smallestChild.minDist == self.minHeap[index].minDist:
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
		self.x = col * SPOTWIDTH
		self.y = row * SPOTWIDTH
		self.color = WHITE
		self.width = SPOTWIDTH
  
		self.id = size*row + col
		self.row = row
		self.col = col
		self.weight = weight
		self.currentIndex = -1
		self.minDist = 99999999999 #used in Dijkstras
		self.pi = None #used to indicate parent in BFS/DFS/SPT
		self.neighbors = []
		
	def reset(self):
		self.minDist = 99999999999
		self.pi = None
		self.color = WHITE
  	

	def get_pos(self):
		return self.row, self.col
	
	def is_visited(self):
		return self.color == RED 
	
	def is_open(self):
		return self.color == GREEN
	
	def is_Wall(self):
		return self.color == BLACK
	
	def is_end(self):
		return self.color == TURQUOISE
		
	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))



def main():
	
	coords = initializeGrid()
	
	#testing code
	walls = {}
	walls[4] = 0
	walls[5] = 0
	walls[6] = 0
	walls[21] = 0
	walls[14] = 0
	
	
	BFS(coords,324,1,walls)           
	print()
	DFS(coords,324,1,walls)
	
	print()
		
	Dijkstra(coords,324,1,walls)    
  
	run = True #use to exit the game
	while run:
		pygame.time.delay(10)
		
		pos = None
		for event in pygame.event.get(): 
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()

			if event.type == pygame.QUIT: #if the X is pressed
				run = False
				
		if pos != None:
			print(pos)
			row = pos[1] // SPOTWIDTH #the y coordinate
			col = pos[0] // SPOTWIDTH #the x coordinate

			if setting == 0: #creates barriers

				coords[int(size*row + col)].make_barrier()
		
		displayWorld(coords)
		

def displayWorld(coords):
    for row in range(0,size):
        for col in range(0,size):
            coords[size*row+col].draw(WIN)
    pygame.display.update()

			
		   
#BACK END AND PATHFINDING FUNCTIONS    
def initializeGrid():
	coords = []
	weight = weight2
	#initialize coordinates
	for row in range(0,size):
		for col in range(0,size):
			if weight == weight1:
				weight = weight2
			else:
				weight = weight1
			
			c = Coord(row,col,weight)
			coords.append(c)
		if (size % 2) == 0:
			if weight == weight1:
				weight = weight2
			else:
				weight = weight1   
				
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
	return coords
	
def outputGrid(result,start,end,walls):
	if result == None:
		print("err, no valid path")
	else:
		path = {}
		while result != None: #starting from end node, add path to hash map. 
			path[result.id] = 0
			result = result.pi
		
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
		currentNode = q.get()		
		
		if currentNode.id == end:
			result = currentNode
			break
		
		for n in currentNode.neighbors:
			if n.id not in visited and n.id not in walls:
				n.pi = currentNode
				visited[n.id] = 0
				q.put(n)
	
	outputGrid(result,start,end,walls)             
	
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
	
	outputGrid(result,start,end,walls)    
	  
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
			n.pi = currentSpace
			newPath = DFSHelper(coords,n.id,end,visited,walls)
			if newPath != None:
				return newPath
			
	return None

def Dijkstra(coords,start,end,walls):
	for n in coords:
		n.reset()
	coords[start].minDist = 0
	q = priorityQueue()
	q.buildHeap(coords,walls)
	
	while q.getSize() != 1:
		v = q.extractMin()
		neighbors = v.neighbors
		
		for u in neighbors:
			if u not in walls:
				btwWeight = abs(v.weight - u.weight)
				relax(v,u,btwWeight,q)
	
	result = coords[end]
	outputGrid(result,start,end,walls)    
	   
#used in Dijkstras Algorithm   
def relax(v,u,btwWeight,q):
	if u.minDist > v.minDist + btwWeight:
		q.changeDist(u,v.minDist + btwWeight)
		u.pi = v
						
main()           
			