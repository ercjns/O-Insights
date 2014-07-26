# Eric Jones
# July 2014
#
# Orienteering Statistics (v 0.2)

import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import re
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmess

###########################
#      MODEL
###########################

class OEvent:
	''' Represents an O event, with Courses and Runners '''
	def __init__(self, name="Name", runners=[], courses=[]):
		self.name = name
		self.runners = runners
		self.courses = courses

	def loadFromFile(self, filename):
		'''load saved datastructures'''
		pass

	def saveToFile(self):
		'''write data structures for later'''
		pass


class Runner:
	''' Represents a runner at an event, attempting a specific course '''
	def __init__(self, name, punches, course, tags=[]):
		self.name = name				  #String
		self.punches = punches			  #List of Punch objects
		self.path = self.punchestopath()  #List of two-tuples
		self.course = course			  #Course object
		self.tags = tags				  #List of Strings
		self.finishstatus = self.verifycourse()  #Boolean True/False
		self.finishtime = self.punches[-1].split if self.finishstatus else None


	def punchestopath(self):
		''' Takes an ORDERED list of punches, returns the path of (a,b) controls'''
		path = []
		for punch in self.punches:
			a = punch.controlA
			b = punch.controlB
			path.append((a,b))
		return(path)


	def verifycourse(self):
		''' all course legs should be on path for valid runner on the course '''
		numcourselegs = len(self.course.order)
		numcourselegsonpath = 0
		for pairs in self.course.order:
			if pairs not in self.path:
				return False
			else:
				numcourselegsonpath += 1
			if numcourselegs == numcourselegsonpath:
				return True
		return False


class Punch:
	''' Represents a record of an e-punch, A is prev. control, B is this control'''
	def __init__(self, controlA, controlB, leg, split):
		self.controlA = controlA #previous contorl
		self.controlB = controlB #this control
		self.leg = leg 			 #int seconds
		self.split = split		 #int seconds

	def __str__(self):
		a = str(self.controlA)
		b = str(self.controlB)
		t = str(self.leg)
		if self.controlA == 0:
			return("Start -> " + b + ": " + t + " seconds")
		elif self.controlB == 999:
			return(a + " > Finish: " + t + " seconds")
		else:
			return(a + " ---> " + b + ": " + t + " seconds")
		return("Error")

class Course:
	''' Represents a course at an event '''
	def __init__(self, name=None, order=None):
		self.name = name     #String
		self.order = order   #Tuple of two-tuples: ((0,1), (1,2), ..., (5,999))


class WinSplitsScrape:
	''' Scrapes from an html file of the table from winsplits'''
	def __init__(self, file):
		self.file = file
		self.soup = BeautifulSoup(open(self.file))
		rows = self.soup.find_all('tr')
		if rows:
			#row 0 is sorting headers
			self.head = rows[1].find_all('td') #legs and control codes
			self.data = rows[2:] #runner data, 2rows per runner
			return
		else:
			return None

	def getCourse(self):
		''' returns a OStats.Course object based on the given file '''
		try:
			flags = [0]  #init with '0' to represent the start punch.
			leginfoRE = re.compile('\-(([1-9][0-9]*)|[F])'
								   '( \([0-9]{3}\))?') #control code optional for 'F'
			for i in self.head:
				text = leginfoRE.search(i.string)
				if text != None:
					leg, code = text.group(1,3)
					try:
						leg = int(leg)
						code = int(code.strip(' \(\)'))
						flags.append(code)
						if flags[leg] != code:
							raise IndexError("Missed a control somewhere")
					except ValueError:
						if leg == 'F': flags.append(999)
						else: raise ValueError("Control code not recognized")

			pairs = tuple((flags[i], flags[i+1]) for i in range(len(flags)-1))
			return(Course(order=pairs))
		except:
			return None

	def getRunners(self, course):
		''' returns a list of OStats.Runner objects '''
		runners = []

		for i in range(0, len(self.data), 2):
			row0 = self.data[i].find_all('td')
			row1 = self.data[i+1].find_all('td')

			finish = [s.string for s in row0[0:4]]
			name = finish[1]
			status = finish[2]

			#parse legs to list of tuples: [('timestring', 'placestring'), ...]
			legs = [s.string for s in row0[4:-1]]
			legs = [(legs[d], legs[d+1]) for d in range(0,len(legs),2)]

			#parse splits to list of tuples: [('timestring', 'placestring'), ...]
			splits = [s.string for s in row1[1:-1]]
			splits = [(splits[d], splits[d+1]) for d in range(0,len(splits),2)]

			if len(legs) != len(splits):
				raise ValueError("Number of Legs and Splits not equal?")
			if len(legs) != len(course.order):
				raise ValueError("Runner Legs and Course Legs not equal?")

			punches = []
			for j in range(len(course.order)):
				leg = self.toSeconds(legs[j][0])
				split = self.toSeconds(splits[j][0])
				if leg and split:
					#runner data for leg and split in winsplits
					a,b = course.order[j]
					p = Punch(a,b,leg,split)
					punches.append(p)
					continue
				elif (not leg) and split:
					#only split data means runner skipped previous control(s)
					a = punches[-1].controlB
					b = course.order[j][1]
					leg = split - punches[-1].split
					p = Punch(a,b,leg,split)
					punches.append(p)
					continue
				else:
					#skipped this control
					continue

			runners.append(Runner(name=name, punches=punches, course=course))

		return(runners)

	def toSeconds(self, timestring):
		'''Convert a string like 1:23.32 or 5.49 or 0.55 to seconds'''
		if len(timestring) < 3:
			return(None)

		hourmin, seconds = timestring.split('.')
		if ':' in hourmin:
			hours, minutes = hourmin.split(':')
		else:
			hours, minutes = 0, hourmin
		h = int(hours)
		m = int(minutes)
		s = int(seconds)
		return(h*3600 + m*60 + s)


#############################
#          VIEW
#############################


class Application(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.c = ctrl(self)
		self.pack()
		self.viewInit()

	def clearFrame(self):
		for child in self.winfo_children():
			child.destroy()

	def openOld(self):
		tkmess.showwarning(self, message="You can't do this yet.")
		return None

	def openNew(self):
		#file open prompt
		file = tkfd.askopenfile()
		if not file:
			tkmess.showwarning(root, message="No file selected")
			return
		#parse the file
		parse = self.c.loadFile(file)
		if not parse:
			return
		#load a new view
		self.viewRunnerList()

	def viewRunnerList(self):
		self.clearFrame()
		for r in self.c.getRunnerList():
			l = tk.Label(self, text="Runner: " + r.name)
			l.pack()


	def viewInit(self):
		self.clearFrame()
		b1 = tk.Button(self, text="Open previous from csv", command=self.openOld)
		b2 = tk.Button(self, text="New from winsplits html", command=self.openNew)
		b1.pack()
		b2.pack()


##############################
#      CONTROLLER
##############################

class ctrl():
	def __init__(self, app=None):
		self.app = app

	def loadFile(self, file):
		scraper = WinSplitsScrape(file.name)
		if type(scraper.getCourse()) != type(Course()):
			print("not a course")
			tkmess.showwarning(self.app, message="File not recognized")
			return None
		else:
			print("found a course")
			#ask for a name of the event
			#eventnameprompt = tkmess.showinfo(root, message="name is not implemented")
			#courseinfoprompt = tkmess.showinfo(root, message="course info goes here")
			#do some processing
			e = OEvent("eventname")
			self.event = e
			c = scraper.getCourse()
			e.courses.append(c)
			rs = scraper.getRunners(c)
			for r in rs:
				e.runners.append(r)
			return True

	def getRunnerList(self):
		return self.event.runners




if __name__ == "__main__":
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()
	root.destroy()
