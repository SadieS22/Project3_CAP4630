"""
Name: Sadie Shank
Course: CAP 4630
Date: 06.30.23
Instructor: Dr. Marques
Assignment #: 3

Description: 
This program runs the traveling salesman problem using ant colony optimization. This was a lot easier to implement in my 
opinion than the traveling salesman problem with the genetic algorithm. 
Sources:
https://www.youtube.com/watch?v=8lYKzj470zc
http://www.scholarpedia.org/article/Ant_colony_optimization
https://github.com/yammadev/aco-tsp
https://github.com/nishnash54/TSP_ACO
https://github.com/rochakgupta/aco-tsp
"""

import math
import random
from matplotlib import pyplot as plt

#I am reading in the number of cities that are wanted and assigning that number to the number of ants that should then exist
#since there should be one ant per city
citynum = 0
citynum = int(input("Enter the number of cities that you want: "))
antnum = citynum

#This is my City class. I was able to reuse this from project two. It specifies x and y coordinates. 
class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

#This is my Ant class. I assigned each ant to its own city.  
class Ant:
    def __init__(self, city):
        self.city = city

#Here I am randomly generating a list of points for each city that the user specified they wanted. 
city_list = []
for i in range(citynum):
    city_list.append(City(x=int(random.random() * 200), y=int(random.random() * 200)))

#Here I am randomly assigning an ant to each city and making sure that the ant is not assigned to a city that already 
#has an ant. I was able to use the logic for this from project 2 as well. The assigned cities just keep track of which 
#cities have already been assigned an ant and the ant list is the list of each ant with its city. 
assigned_cities = []
antlist = []

for i in range(antnum):
    available_cities = [city for city in city_list if city not in assigned_cities]
    random_city = random.choice(available_cities)
    assigned_cities.append(random_city)
    antlist.append(Ant(city=random_city))

#Going through every city in the city list and finding its distance to every other city. 
#This is my distance array. I decided to try an approach where we create an array for each distance so there is easy lookup. 
#This means that when we want to find how far it is from city 3 to city 27, we can just find distance[3][27] and that will
#have the distance. 
distance = [[0] * citynum for _ in range(citynum)]

#As a result of having a 2D array, I need to iterate through every city combo possible and store the values.
for i in range(citynum):
    for j in range(citynum):
        #If we are asking for the distance from one city to itself, it's just zero. 
        if i == j:
            distance[i][j] = 0
        else:
            #This calculates the distnace between two cities using the pythagorean theorem. 
            distance[i][j] = math.sqrt((city_list[i].x - city_list[j].x) ** 2 + (city_list[i].y - city_list[j].y) ** 2)


#I am creating a 2d array to store pheromone values for each edge between cities.
pheromonenum = (citynum * (citynum - 1)) / 2
pheromone = [[0] * citynum for _ in range(citynum)]

#I am initializing all of the pheromone values to zero at the beginning. The values of [i][j] are the same as those of [j][i]
#When the values need to be updated later on, it will update both [i][j] and [j][i]
for i in range(citynum):
    for j in range(citynum):
          pheromone[i][j] = 0
          pheromone[j][i] = 0

#Inputting the number of iterations. 
numiterate = int(input("Enter the number of iterations: "))

#Inputting the pheromone evaporation rate. I am allowing the user to enter it if they want to - otherwise
#the default is going to be 0.5.
yon = input("Would you like to specify a value for the pheromone evaporation rate? Default is 0.5: (Y/N) ")

if yon == 'Y' or yon == 'y':
    pherevaprate = float(input("Enter the pheromone evaporation rate (between 0.1 and 0.9): "))

    if pherevaprate > 0.9 or pherevaprate < 0.1:
        print("That is out of range, the pheromone evaporation rate is going to be set to 0.5.")
        pherevaprate = 0.5

else:
    pherevaprate = 0.5

#Inputting the pheromone deposit amount. I am allowing the user to enter it if they want to - otherwise
#the default is going to be 0.01.
yon = input("Would you like to specify a value for the pheromone deposit amount? Default is 0.01: (Y/N) ")

if yon == 'Y' or yon == 'y':
    pherodepam = float(input("Enter the pheromone deposit amount (between 0.01 and 0.1): "))

    if pherodepam > 0.1 or pherodepam < 0.01:
        print("That is out of range, the pheromone deposit amount is going to be set to 0.01.")
        pherodepam = 0.01

else:
    pherodepam = 0.01

#I had to do a lot of research with this part of the algorithm because I thought that ACO could just
#pick the highest pheromone value and the lowest distance, but in fact that would lead to a problem
#and it is better to do this by allowing the algorithm to pick a different route if it wants to, so 
#I am implemeting this using probability. 
def antroute(city_list, antlist, distance, pheromone, ant_index):
    #I am taking the ant and the ant's city so I can do the calculations with each ant
    ant = antlist[ant_index]
    current_city_index = city_list.index(ant.city)
    #This is a list of the cities that have been visited so far. I am only putting the current city in, 
    #which is the city that corresponds to the ant because it will be added to but only this city has been
    #visited.
    visited_cities = [current_city_index]

    #I am going through every city that has not been visited until all of the cities have been visited. 
    while len(visited_cities) < len(city_list):
        #I am making a list of all the cities that have not been visited yet.
        unvisited_cities = [city_index for city_index in range(len(city_list)) if city_index not in visited_cities]
        #Calculate the attractiveness of each neighboring city
        attractiveness = []
        #This cycles through every city that has not been visited. 
        for neighbor_city_index in unvisited_cities:
            dist = distance[current_city_index][neighbor_city_index]
            #This just verifies that the same cities didn't get picked - that the current city is not equal to the neighbor city
            if dist != 0:
                pheromone_level = pheromone[current_city_index][neighbor_city_index]
                        #Instead of just dividing pheromone_level by dist to get the better value, I decided that squaring
                        #pheromone_level and cubing dist would show that higher pheromone and lower distances are better, it 
                        #basically emphasizes them more. 
                attractiveness.append((pheromone_level ** 2) / (dist ** 3))

        total_attractiveness = sum(attractiveness)

        if total_attractiveness == 0:
            #If there is not attractiveness yet, then all the cities have equal probability, so it just randomly picks one. 
            next_city_index = random.choice(unvisited_cities)
        else:
            #This is dividing the attractiveness of one piece by the total attractiveness. 
            #Therefore, the higher the attractiveness, the better chance of getting picked. 
            probabilities = [attract / total_attractiveness for attract in attractiveness]
            next_city_index = random.choices(unvisited_cities, probabilities)[0]

        #This make the current city the next city and puts that city as one of the visited ones. 
        current_city_index = next_city_index
        visited_cities.append(current_city_index)

    visited_cities.append(city_list.index(ant.city))
    #The ant's path now has the visited city in it. 
    ant.path = [city_list[index] for index in visited_cities]

def antpaths(city_list, antlist, distance, pherevaprate, pherodepam):
    for i in range(len(antlist)):
        antroute(city_list, antlist, distance, pheromone, i)
    
    #This is updating all the pheromone values after the ant has chosen its path. 
    for i in range(len(city_list)):
        for j in range(i + 1, len(city_list)):
            #This slowly evaporates the pheromone on the trails. 
            pheromone[i][j] *= (1 - pherevaprate)
            pheromone[j][i] *= (1 - pherevaprate)
            
            #This is adding pheromone to the new path the ant chose. 
            for ant in antlist:
                path = ant.path
                if path[i] == j or path[j] == i:
                    pheromone[i][j] += pherodepam
                    pheromone[j][i] += pherodepam

#This calls antpath which calls antroute
for _ in range(numiterate):
    antpaths(city_list, antlist, distance, pherevaprate, pherodepam)

#This is for the intial route and the distance so we can see the difference in how much it changed. 
initial_route = antlist[0].path
initial_distance = 0
#I am going through and calculating the distance of the initial route
for i in range(len(initial_route) - 1):
    city_index1 = city_list.index(initial_route[i])
    city_index2 = city_list.index(initial_route[i + 1])
    distancebetween = distance[city_index1][city_index2]
    initial_distance += distancebetween
    
print("Initial Route:", initial_route)
print("Initial Distance:", initial_distance)

#This was a bit more tricky because now I needed to sort everything, but I ended up calculating the distances
#for all of the routes in this easy embedded for loop and then I just found the corresponding index and printed 
#that out. 
allpathdistance = []
for ant in antlist:
    ant_route = ant.path
    ant_distance = 0
    #I am going through and calculating the distance of the initial route
    for i in range(len(ant_route) - 1):
        city_index1 = city_list.index(ant_route[i])
        city_index2 = city_list.index(ant_route[i + 1])
        distancebetween = distance[city_index1][city_index2]
        ant_distance += distancebetween
    allpathdistance.append(ant_distance)

final_distance = min(allpathdistance)
smallest_route_index = allpathdistance.index(final_distance)
final_route = antlist[smallest_route_index].path

print("Final Route:", final_route)
print("Final Distance:", final_distance)

#This part of the program is to use matplotlib to print out graphs showing the path that the ants take
def plot_path(city_list, path):
    x = [city.x for city in city_list]
    y = [city.y for city in city_list]

    #This is going to plot all the cities
    plt.figure()
    plt.scatter(x, y, color='red', zorder=2)

    #I am actually plotting the paths here. 
    for i in range(len(path) - 1):
        city1 = path[i]
        city2 = path[i + 1]
        plt.plot([city1.x, city2.x], [city1.y, city2.y], color='blue', zorder=1)

    plt.show()

#This now calls the function and plots the path for the final route
plot_path(city_list, final_route)