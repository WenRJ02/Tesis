import math
import random
import pandas as pd
import time
import statistics
from ACFL import GLCV
from particle import Particle
from Dinamic import Dinamic


class PSO:
    
    assets = []
    histo=[]
    
    def __init__(self,  size, maxgen, assets, acl,acg,v):
        self.swarm_size = size
        self.max_gen = maxgen
        self.budget = 0
        self.swarm = []
        self.assets = assets
        self.Best_Swarm_Position = []
        self.Worst_Swarm_Position = []
        self.Best_Swarm_fitness = 0
        self.Worst_Swarm_fitness = 0
        self.asset_return = []
        self.asset_cov = []
        self.best_return = 0
        self.best_risk = 0
        self.worst_return = 0
        self.worst_risk = 0
        self.acc_local = acl
        self.acc_global = acg
        self.velocity = v
        
    def run(self, fuzzy, Fuzzy_parameters):
        
        self.read_data()
        
        start = time.time()
        
        if fuzzy == 1:
            GCLV_Return =  GLCV(Fuzzy_parameters[0], Fuzzy_parameters[1], Fuzzy_parameters[2])
            GCLV_Risk =  GLCV(Fuzzy_parameters[3], Fuzzy_parameters[4], Fuzzy_parameters[5])
        else:
            GCLV_Return = []
            GCLV_Risk = []
        
        self.create_initial_swarm(fuzzy, Fuzzy_parameters, GCLV_Return, GCLV_Risk)
        c1 = self.acc_local #Componente de aceleracion local
        c2 = self.acc_global #Componente de aceleracion global
        velocidad = self.velocity # cantidad de movimientos
        flag_select = 0
        
        for generation in range(self.max_gen):
            
           # print("Gen "+ str(generation))
                
            for particle in self.swarm:
                
                # Determinar si se ahra moviento basado en mejor solucion local o global
                mov_local = random.randint(1,10) * c1
                mov_global = random.randint(1,10) * c2
                
                if mov_local >= mov_global:
                    mov = particle.get_position(1)
                else:
                    mov = self.Best_Swarm_Position.copy()
                    
                pos = particle.Move_Particle(mov, velocidad, 1, 100)
                particle.Copy_Position(pos, 0, 0)
                
                if fuzzy == 0:
                    #Normal
                    particle.fitness = self.get_fitness(particle)
                else:
                    #Fuzzy
                    particle.fitness = self.get_fitness_ACFL(particle, Fuzzy_parametros, GCLV_Return, GCLV_Risk)
                
                if particle.fitness > particle.Best_Personal_fitness:
                    particle.Best_Personal_fitness = particle.fitness
                    particle.Best_Personal_Position = particle.get_position(0)
                    
                if particle.fitness > self.Best_Swarm_fitness:
                    self.Best_Swarm_fitness = particle.fitness
                    self.Best_Swarm_Position = particle.get_position(1)
                    self.best_return = particle.retorno
                    self.best_risk = particle.riesgo 
                    
                if particle.fitness < self.Worst_Swarm_fitness:
                    self.Worst_Swarm_fitness = particle.fitness
                    self.Worst_Swarm_Position = particle.get_position(1)
                    self.worst_return = particle.retorno
                    self.worst_risk = particle.riesgo 
                    
               # print(str(self.best_return) +" "+ str(self.best_risk))
        end = time.time()
        
        run_time = end-start
        
        #print(str(self.best_return) +" "+ str(self.best_risk) + " "+str(self.worst_return) +" "+ str(self.worst_risk))
        #print(str(self.Best_Swarm_fitness) + " " +str(self.best_return) +" "+ str(self.best_risk))
        return self.swarm
        
    
    def create_initial_swarm(self, fuzzy, param, GCLV_re, GCLV_ri):
        
        #First distribute the weigths equaly
        weight = math.trunc(100/self.assets)
        count = 0
        generalized_solution = []
        
        for i in range(self.assets):
            generalized_solution.append(weight)
            count = count + weight
            
        if count < 100:
            
            generalized_solution[0] = generalized_solution[0] + (100-count)
            
        #Then, use generalized solution to inititalize the swarm
        id_part = 0
        for particle in range(self.swarm_size):
            particle = Particle()
            particle.id = id_part
            id_part = id_part + 1
            pos = particle.Move_Particle(generalized_solution, 50, 1, 100)
            particle.Copy_Position(pos, 0, 1)
            particle.Copy_Position(pos, 1, 1)
            
            if fuzzy == 0:
                particle.fitness = self.get_fitness(particle)
                particle.Best_Personal_fitness = particle.fitness
            else:
                particle.fitness = self.get_fitness_ACFL(particle, param, GCLV_re, GCLV_ri)
                particle.Best_Personal_fitness = particle.fitness
            
              
            if len(self.swarm) == 0:
                self.Best_Swarm_fitness = particle.Best_Personal_fitness
                self.Worst_Swarm_fitness = particle.Best_Personal_fitness
                self.Best_Swarm_Position = particle.get_position(1)
                
                
            self.swarm.append(particle) #Creates a diferent random solution
            
            if  particle.Best_Personal_fitness > self.Best_Swarm_fitness:
                self.Best_Swarm_fitness = particle.Best_Personal_fitness
                self.Best_Swarm_Position = particle.get_position(1)
                
            if particle.Best_Personal_fitness < self.Worst_Swarm_fitness:
                self.Worst_Swarm_fitness = particle.Best_Personal_fitness
                self.Worst_Swarm_Position = particle.get_position(1)
        
        #print(self.Best_Swarm_fitness)
        return 0
    
    def read_data(self):
        
        df = pd.read_excel('Instance4.xlsx', sheet_name='COV')
        for asset in range(self.assets):
            self.asset_return.append(df['Returns'][asset])
                             
        self.asset_cov = df    
        return 0
        
    
    def get_return(self, particle):
        
        total_return = 0
        
        for i in  range(self.assets):
            total_return = total_return + (particle.Position[i] * self.asset_return[i])

        return total_return
    
    def get_risk(self, particle):
        
        total_risk = 0
        
        count = 0
        for i in range(self.assets):
            i = count
            for j in range(self.assets):
                if i != j:
                    x = self.asset_cov.iloc[i][j+1]
                    #y = self.asset_cov.iloc[i][j]
                    total_risk = total_risk + (particle.Position[i] * particle.Position[j] * x)
            count = count + 1
        return total_risk
    
    def get_COV(self, i, j):
        
        j = j+1
            
        print(self.asset_cov.iloc[i][j])
        cov = self.asset_cov.iloc[i][j]
        
        return cov
        
    
    def get_fitness(self, particle):
        
        asset_return = self.get_return(particle)
        asset_risk = self.get_risk(particle)
        
        particle.retorno = asset_return
        particle.riesgo = asset_risk
        
        fitness = asset_return - asset_risk
        
        
        return fitness
    
    def get_fitness_ACFL(self, particle, parametros, GCLV_Retu, GCLV_Ri):
        
        asset_return = self.get_return(particle)
        asset_risk = self.get_risk(particle)
        
        particle.retorno = asset_return
        particle.riesgo = asset_risk
        
        fitness = asset_return - asset_risk
        
        GCLV_Return =  GLCV(parametros[0], parametros[1], parametros[2])
        GCLV_Risk =  GLCV(parametros[3], parametros[4], parametros[5])
        
        fuzzy_ret = GCLV_Return.GLCV_run(asset_return)
        fuzzy_risk =  GCLV_Risk.GLCV_run(asset_risk)
        fit_fuzzy = math.sqrt(fuzzy_ret * fuzzy_risk)
        
        return fit_fuzzy
    
    def print_sol(self, sol, fuzzy, parametros):    
        
        count = 0
        
        particle = Particle()
        particle.Position = sol.copy()
        
        return_sol = self.get_return(particle)
        total_risk = self.get_risk(particle)
        fit = return_sol - total_risk

        if fuzzy == 1:
            GCLV_Return =  GLCV(parametros[0], parametros[1], parametros[2])
            GCLV_Risk =  GLCV(parametros[3], parametros[4], parametros[5])
            re = GCLV_Return.GLCV_run(return_sol)
            ri = GCLV_Risk.GLCV_run(total_risk)
            fit = re * ri
            print(fit)
            print("" + str(return_sol) + " ==" + str(total_risk))
            #print("" + str(total_risk))
            print("" + str(re) + " ==" + str(ri))
          #  print(ri)   
            
        else:
            print(fit)
            print("" + str(return_sol))
            print("" + str(total_risk))
            


            
      
   
    