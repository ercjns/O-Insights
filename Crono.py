#Eric Jones
#June 2014
#
# Crono library
# Time functions


class Time:
	def __init__(self, hours=0, minutes=0, seconds=0, mseconds=0):
		if hours < 0: raise(ValueError("No negative time!"))
		if minutes >= 60 or minutes < 0: raise(ValueError("Invalid minutes"))
		if seconds >= 60 or seconds < 0: raise(ValueError("Invalid seconds"))
		if mseconds >=1000 or mseconds < 0: raise(ValueError("Invalid mseconds"))

		self.hours = hours
		self.minutes = minutes
		self.seconds = seconds
		self.mseconds = mseconds

	def __add__(a, b):
		mseconds = a.mseconds + b.mseconds
		seconds = a.seconds + b.seconds
		minutes = a.minutes + b.minutes
		hours = a.hours + b.hours

		if mseconds >= 1000:
			mseconds = mseconds - 1000
			seconds += 1
		if seconds >= 60:
			seconds = seconds - 60
			minutes += 1
		if minutes >= 60:
			minutes = minutes - 60
			hours += 1

		return Time(hours, minutes, seconds, mseconds)


	def __sub__(a, b):
		mseconds = a.mseconds - b.mseconds
		if mseconds < 0:
			mseconds += 1000
			a.seconds -= 1
		seconds = a.seconds - b.seconds
		if seconds < 0:
			seconds += 60
			a.minutes -= 1
		minutes = a.minutes - b.minutes
		if minutes < 0:
			minutes += 60
			a.hours -= 1
		hours = a.hours - b.hours
		if hours < 0:
			raise(ValueError('No Negative time'))

		return Time(hours, minutes, seconds, mseconds)

	def __repr__(a):
		if a.hours == 0 and a.mseconds == 0:
			return "%d:%02d:%02d" % (0, a.minutes, a.seconds)
		elif a.mseconds == 0:
			return "%d:%02d:%02d" % (a.hours, a.minutes, a.seconds)
		elif a.hours == 0:
			return "%d:%02d:%02d.%03d" % (0, a.minutes, a.seconds, a.mseconds)
		else:
			return "%d:%02d:%02d.%03d" % (a.hours, a.minutes, a.seconds, a.mseconds)

	def toSeconds(a):
		return (a.hours*60*60) + (a.minutes*60) + (a.seconds) + (a.mseconds)

def secsToCrono(a):
	if type(a) != int:
		raise(TypeError('must be an int'))
		
	seconds = a
	minutes = 0
	hours = 0

	if seconds > 60:
		minutes, seconds = divmod(seconds, 60)
	if minutes > 60:
		hours, minutes = divmod(minutes, 60)
	return Time(hours, minutes, seconds)
