# Eric Jones
# June, 2014
#
# WinSplits Scraping and Analysis

import Crono
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


class oRacePlotting:

    def plotTimeBehindLeader(race, debug=False):
        #get splits at each control for each runner
        for i in range(1,race.controls+1):
            order = race.orderAtControl(i)
            fastest = order[0].splits[str(i)][0]
            for runner in order:
                behind = runner.splits[str(i)][0] - fastest
                runner.tbhldata.append((fastest.toSeconds(), behind.toSeconds()))
                if debug: print("At control %d: %s is %d behind" % i, runner.name, behind)

        #display the data
        for runner in race.runners:
            if runner.status == False: continue
            x,y = ([x for x,y in runner.tbhldata], [-y for x,y in runner.tbhldata])
            plt.plot(x,y, 'x-')
        plt.show()

    def plotPerformanceIndex(race, debug=False):
        '''
        A runner's performance index on a leg is defined as the average of the
        fastest 25% split times on that leg divided by the runner's split time
        '''
        pass


class oRaceResults:
    ''' contatins results for many runners
    may also contain data structures optimized for further analysis'''
    def __init__(self):
        self.runners = []
        self.controls = 0

    def addRunner(self, runner):
        self.runners.append(runner)
        if self.controls == 0:
            self.controls = len(runner.legs.keys())
        elif len(runner.legs.keys()) != self.controls:
            raise ValueError("Differet Number of Controls")
        else:
            return True

    def prepList(self, condition, debug=False):
        removelist = []
        mylist = self.runners[:]
        for runner in mylist:
            if condition(runner): removelist.append(runner)
        for runner in removelist:
            mylist.remove(runner)
            if debug: print("removed: ", runner.name)
        return mylist

    def orderOnLeg(self, leg, debug=False):
        runners = self.prepList(lambda x: True if x.legs[str(leg)][1] == False else False, debug)
        x = sorted(runners, key=(lambda runner: runner.legs[str(leg)][1]))

        if debug:
            answer = []
            for runner in x:
                answer.append((runner.name, runner.legs[str(leg)]))
            return answer
        return x

    def orderAtControl(self, control, debug=False):
        runners = self.prepList(lambda x: True if x.splits[str(control)][1]==False else False, debug)
        x = sorted(runners, key=(lambda runner: runner.splits[str(control)][1]))

        if debug:
            answer = []
            for runner in x:
                print(runner.name, runner.splits[str(control)])
                answer.append((runner.name, runner.splits[str(control)]))
            return answer
        return x

    def timeLostOnLeg(self, leg, debug=False):
        x = self.orderOnLeg(leg)
        fastest = x[0].legs[str(leg)][0]
        timelost = []
        for runner in x:
            name = runner.name
            timeback = runner.legs[str(leg)][0] - fastest
            timelost.append((name,timeback))
        return timelost



class oRunnerResult:
    ''' contains the results for one runner in one race '''
    def __init__(self, name, time, rank, legs, splits):
        self.name = name
        self.time = time
        self.rank = rank
        self.legs = legs
        self.splits = splits
        self.status = True if self.time else False

        self.tbhldata = []


class winSplitsScraper:
    def __init__(self, filename):
        self.soup = BeautifulSoup(open(filename))

    def scrapeRaceResults(self):
        oResults = oRaceResults()
        rows = self.soup.find_all('tr')
        rows = rows[2:]
        runner_idx = range(0,len(rows),2)
        for i in runner_idx:
            #scrape the runner results
            oRunner = self.__scrapeRunnerTimes(rows[i:i+2])

            #add the runner to the race results
            oResults.addRunner(oRunner)

        #return the race resuts
        return oResults


    def __scrapeRunnerTimes(self, rows):
        '''
        Convert table data for one runner into an oRunnerResult object
        '''
        row0 = rows[0].find_all('td')
        row1 = rows[1].find_all('td')

        #Finish information
        final = row0[0:4]
        rank = self.__parseRank(final[0].string)
        name = str(final[1].string)
        time = self.__parseTime(final[2].string)

        #Legs: control to control times.
        legs = row0[4:-1]
        legs = self.__parseTimeRankData(legs)

        #splits: cumulative times at each control
        splits = row1[1:-1]
        splits = self.__parseTimeRankData(splits)

        #dump the data into a oRunnerResult
        runner = oRunnerResult(name, time, rank, legs, splits)

        return(runner)

    def __parseTime(self, souptimestring):
        '''
        Convert a BeautifulSoup NavigableString to a Crono.Time
        "1:23.45" => 1 hour, 23 minutes, 45 seconds
        '''

        timestring = str(souptimestring)

        if '.' not in timestring:
            return False

        hourmin, seconds = timestring.split('.')
        if ':' in hourmin:
            hours, minutes = hourmin.split(':')
        else:
            hours, minutes = 0, hourmin

        try:
            time = Crono.Time(int(hours), int(minutes), int(seconds))
            return time
        except:
            return False

    def __parseRank(self, souprankstring):

        rankstring = str(souprankstring)
        rankstring = rankstring.strip('()')
        try:
            return int(rankstring)
        except:
            return False


    def __parseTimeRankData(self, soupdata):
        '''
        Convert a set of soup tags to a dict
        '''
        res = {}
        leg = 1

        for i in range(0,len(soupdata),2):
            timestring = soupdata[i].string
            time = self.__parseTime(timestring)
            rankstring = soupdata[i+1].string
            rank = self.__parseRank(rankstring)
            res[str(leg)] = (time, rank)
            leg += 1
        return res

if __name__ == "__main__":
    x = winSplitsScraper('winsplits_140201_p7m_wiol_7.html')
    race = x.scrapeRaceResults()

    # race.orderAtControl(1, True)
    oRacePlotting.plotTimeBehindLeader(race)

    #
    # print(race.timeLostOnLeg(4))
