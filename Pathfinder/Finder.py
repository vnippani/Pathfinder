import queue
import math
import pygame
import sys

#set pygame screen settings
TOTALWIDTH = 800
WIDTH = 600

WIN = pygame.display.set_mode((TOTALWIDTH,WIDTH))
pygame.display.set_caption("Pathfinder")

pygame.init()
pygame.font.init()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

size = 40

SPOTWIDTH = WIDTH / size

gameFont = pygame.font.SysFont('Corbel',20) 
tileFont = pygame.font.SysFont('Corbel',10) 

#by default, all spaces have an edge weight of 1 (abs(2-1) == abs(1-2)) 
weight1 = 1 
weight2 = 2

setting = 3 #determines what occurs when the user clicks the grid

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

class Button(object):
	def __init__(self,x,y,color,width,height,text,id):
		self.x = x
		self.y = y
		self.color = color
		self.width = width
		self.height = height
		self.text = text
		self.id = id
	
	def draw(self,win):
		pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.height))
		win.blit(self.text , (self.x + self.width /8,self.y + self.height / 8)) 
		
	def clicking(self,click):
		if click[0] > self.x and click[0] < self.x + self.width:
			if click[0] > self.y and click[1] < self.y + self.height:
				return True
		return False
	
 	
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
		self.text = tileFont.render(str(self.weight),True,BLACK)
  
	def changeWeight(self):
		self.weight = (self.weight + 1) % 10
		if self.weight == 0:
			self.weight = 1
		self.text = tileFont.render(str(self.weight),True,BLACK)

	def resetWeight(self,weightGiven):
		self.weight = weightGiven
		self.text = tileFont.render(str(self.weight),True,BLACK)
  
	def reset(self):
		self.minDist = 99999999999
		self.pi = None
	
	def resetColor(self):
		self.color = WHITE
		
  	
	def getColor(self):
		return self.color
	def get_pos(self):
		return self.row, self.col

	def is_start(self):
		return self.color == ORANGE

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

	def make_visited(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = RED
  
	def make_finalPath(self):
		self.color = BLUE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

  
	def displayGridNum(self,win,sett):
	
		if sett == 3:
			win.blit(self.text , (self.x + self.width /2.5,self.y + self.width / 2.5)) 


def main():
	sys.setrecursionlimit(size*size + 10)
	global setting
	setting = 0
	coords = initializeGrid()
	
	#testing code
	walls = {}
	
  
	run = True #use to exit the game
 
	
	text = gameFont.render('quit',True,RED)
 	
	buttons = []
 
	text = gameFont.render('BFS',True,RED)
	b = Button(630,50,WHITE,100,50,text,0)
	buttons.append(b)
  
	text = gameFont.render('DFS',True,RED)
	b = Button(630,150,WHITE,100,50,text,1)
	buttons.append(b)  
	
	text = gameFont.render('Setting',True,RED)
	b = Button(630,250,WHITE,100,50,text,2)
	buttons.append(b)  
	
	text = gameFont.render('Dijkstra',True,RED)
	b = Button(630,350,WHITE,100,50,text,2)
	buttons.append(b) 	
 
	text = gameFont.render('Clear',True,RED)
	b = Button(630,450,WHITE,100,50,text,2)
	buttons.append(b)
  	
	#set initial start and end
	start = 0
	end = 1
	coords[start].make_start()
	coords[end].make_end()
 
	BFSRunning = False
	DFSRunning = False
	DijkstraRunning = False
 
	
	while run:

		pygame.time.delay(10)
		
		pos = None
		for event in pygame.event.get(): 
			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()

			if event.type == pygame.QUIT: #if the X is pressed
				run = False
    

    
		if pos != None:
			print(setting)
			if(pos[0] >= 600):
				buttonClicked = -1
				for i in range(0, len(buttons)):
					if buttons[i].clicking(pos):
						buttonClicked = i 
						break	#due to placement of buttons, if one is clicked, others can't be
				
    			#iterate through all buttons to see if they were pressed
				if buttonClicked == 0: #run BFS
					BFS(coords,start,end,walls,buttons)

				elif buttonClicked == 1: #run DFS
					DFS(coords,start,end,walls,buttons)
	
				elif buttonClicked == 2: #change setting
					setting = (setting + 1) % 4
				elif buttonClicked == 3: #run Dijkstras Algorithm
					Dijkstra(coords,start,end,walls,buttons)
				elif buttonClicked == 4: #clear the entire grid, reset start and end pos
					resetStartEnd = resetGrid(coords,walls)
					start = resetStartEnd[0]
					end = resetStartEnd[1]
     
				pygame.time.delay(190) #extra delay to prevent multiple rapid clicks
				
			else:
				row = pos[1] // SPOTWIDTH #the y coordinate
				col = pos[0] // SPOTWIDTH #the x coordinate
				row = int(row)
				col = int(col)
				if setting == 0: #creates barriers
					
					if not coords[size*row + col].is_end() and not coords[size*row + col].is_start():
						currentColor = coords[size*row + col].getColor()
						if currentColor == WHITE:
							coords[size*row + col].make_barrier()	
							walls[size*row + col] = 0

				elif setting == 1: #set new start
					if size*row + col not in walls:
						coords[start].resetColor()
						start = size*row+col		
						coords[start].make_start()

				elif setting == 2: #set new end
					if size*row + col not in walls:
						coords[end].resetColor()
						end = size*row+col		
						coords[end].make_end()
				
				elif setting == 3:
					coords[size*row + col].changeWeight()
					pygame.time.delay(190)

  		
		
		displayWorld(coords,buttons)

  		

def displayCoords(coords):
	for row in range(0,size):
		for col in range(0,size):
			coords[size*row+col].draw(WIN)
			coords[size*row+col].displayGridNum(WIN,setting)
			
	

def resetGrid(coords,walls):
	walls.clear()
	weight = weight1
	for row in range(0,size):
		for col in range(0,size):
			if weight == weight1:
				weight = weight2
			else:
				weight = weight1
			
			c = Coord(row,col,weight)
			coords.append(c)

			coords[size*row + col].reset()
			coords[size*row + col].resetColor()
			coords[size*row + col].resetWeight(weight)
   
		if (size % 2) == 0:
			if weight == weight1:
				weight = weight2
			else:
				weight = weight1  

	start = 0
	end = 1
	coords[0].make_start()
	coords[1].make_end()
	return [start, end]

def displayButtons(buttons):
	for button in buttons:
		button.draw(WIN)			


def displayWorld(coords,buttons):
	WIN.fill((0,0,0)) 
	displayCoords(coords)
	displayButtons(buttons) 
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
	
def outputGrid(result,start,end,walls,coords,buttons):
	if result == None:
		print("err, no valid path")
	else:
		while result != None: #starting from end node, add path to hash map. 
			if result.id != start and result.id != end:
				result.make_finalPath()
			result.draw(WIN)
			pygame.time.delay(2)
			pygame.display.update()
   
			result = result.pi #move to next space in path
			
		
		

def BFS(coords,start,end,walls,buttons):
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
		pygame.time.delay(3)
		currentNode = q.get()		

		if currentNode.id == end:
			result = currentNode
			break
		
		if currentNode.id != start:
			currentNode.make_path()
			currentNode.draw(WIN)
  
		for n in currentNode.neighbors:
			if n.id not in visited and n.id not in walls:
				n.pi = currentNode
				visited[n.id] = 0
				q.put(n)
				if n.id != end:
					n.make_visited()
					n.draw(WIN)
    
		pygame.display.update()
  
	outputGrid(result,start,end,walls,coords,buttons)             
	
def DFS(coords,start,end,walls,buttons):
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
	result = DFSHelper(coords,start,start,end,visited,walls,buttons)
	
	outputGrid(result,start,end,walls,coords,buttons)    
	  
def DFSHelper(coords,start,current,end,visited,walls,buttons):
	"""
	coords: grid of Coord objects
	current: id (or size*row + col) of current space
	end: id of end space
	visited: map containing visited nodes
	"""
	visited[current] = 0
	
	pygame.time.delay(2)
	
	if current == end:
		return coords[current]
	
	
	currentSpace = coords[current] #get the space corresponding to id current
 
	if currentSpace.id != start:
		currentSpace.make_path()
		currentSpace.draw(WIN)
	
	pygame.display.update()
 
	for n in currentSpace.neighbors:
		if n.id not in visited and n.id not in walls:
			n.pi = currentSpace
			newPath = DFSHelper(coords,start,n.id,end,visited,walls,buttons)
			if newPath != None:
				return newPath
	
	
 		
	return None

def Dijkstra(coords,start,end,walls,buttons):
	for n in coords:
		n.reset()
		if n.id not in walls and n.id != start and n.id != end:
			n.make_visited() #all nodes are in the queue
			n.draw(WIN)
			pygame.display.update()
		pygame.time.delay(1)
	
	coords[start].minDist = 0
	q = priorityQueue()
	q.buildHeap(coords,walls)
	
	
	while q.getSize() != 1:

		v = q.extractMin()

		if v.id != start and v.id != end:
			v.make_path()
			v.draw(WIN)
	
		neighbors = v.neighbors
		
		for u in neighbors:
			if u not in walls:
				btwWeight = abs(v.weight - u.weight)
				relax(v,u,btwWeight,q)

		pygame.display.update()
  
	result = coords[end]
	outputGrid(result,start,end,walls,coords,buttons)    
	   
#used in Dijkstras Algorithm   
def relax(v,u,btwWeight,q):
	if u.minDist > v.minDist + btwWeight:
		q.changeDist(u,v.minDist + btwWeight)
		u.pi = v
						
main()           
			