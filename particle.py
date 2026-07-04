import random

class Particle:
    
    #Creates a new solution
    def __init__(self):
        self.Position = []
        self.Best_Personal_Position = []
        self.Best_Personal_fitness = 0
        self.fitness = 0
        self.retorno = 0
        self.riesgo = 0
        self.id = 0
            
    #Moves a particle to a new location
    def Move_Particle(self, solution, moves, lower_boun, upper_bound):
                
        for x in range(moves):
            pos1 = random.randint(0, len(solution)-1)
            pos2 = random.randint(0, len(solution)-1)
            while(pos1 == pos2):
                pos1 = random.randint(0, len(solution)-1)
                pos2 = random.randint(0, len(solution)-1)
                
            if solution[pos1] != 0:
                
                change = round(solution[pos1] * (1/ random.randint(lower_boun, upper_bound)), 1)
                                
                solution[pos1] = round(solution[pos1] - change,2)
                solution[pos2] = round( solution[pos2] + change,2)
                
        #self.Position = self.Copy_Position(solution, 1)
        return solution
    
    def Copy_Position(self, new_position, is_best, is_new):
        
        if is_best == 0:
            if is_new == 0:
                for i in range(len(new_position)):
                    self.Position[i] = new_position[i] 
            else:
                for i in range(len(new_position)):
                    self.Position.append(new_position[i]) 
        else:
            if is_new == 0:
                for i in range(len(new_position)):
                    self.Best_Personal_Position[i] = new_position[i] 
            else:
                for i in range(len(new_position)):
                    self.Best_Personal_Position.append(new_position[i]) 
                
    def get_position(self, flag_best):
        copy = []
        
        if flag_best == 0:
            for i in range(len(self.Position)):
                copy.append(self.Position[i])
        else:
            for i in range(len(self.Best_Personal_Position)):
                copy.append(self.Best_Personal_Position[i])
        return copy
