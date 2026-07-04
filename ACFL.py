import math
import statistics

class GLCV:
    
    def __init__(self, alfa, gama, eme):
        self.eme = eme
        self.alfa = alfa
        self.gama = gama
        self.deno_max = 0
        self.sol_actuales = []
        
    def S(self, x):
        
        # math.exp dara error si e esta elevado a un numero positivo grande
        # en aproximadamente e elevado a 200 esta el error, porque e tiene a infinito
        #en aproximadamente e elevado a -200 tiende a 0
        
        if -self.alfa*(x-self.gama) > 220:
            print("Combination tiende a infinito")
            denominador = 1 + math.exp(-self.alfa*(x-self.gama))
            denominador = 1 / denominador
            return 0
        if -self.alfa*(x-self.gama) < -220:
            denominador = 1 + math.exp(-self.alfa*(x-self.gama))
            denominador = 1 / denominador
            
            #print("Combination tiende a cero")
            return 0
        
        denominador = 1 + math.exp(-self.alfa*(x-self.gama))
        denominador = 1 / denominador
        
        return denominador
        
    def C(self, x, y):
        
        prod = math.sqrt(x * y)
        
        return prod
    
    def GLCV_run(self, x):
        
        a = self.S(x)
        b = 1 - a
        
        a = pow( a, self.eme)
        b = pow( b, 1 - self.eme)
        
        num = self.C(a, b)
        dem = 1
        
        res = num/dem
        if num/dem > 1:
            print("GLCV mayor 1")
        
        return res
     
    def GLCV_get_max(self, lower_bound, upper_bound, unit):
        max_res = 0
        j = lower_bound
          
        try:
            while j < upper_bound:
                a = self.S(j)
                b = 1 - a
                
                a = pow( a, self.eme)
                b = pow( b, 1 - self.eme)
                
                num = self.C(a, b)
                
                if j == lower_bound:
                    self.deno_max = num
                    
                if (num > self.deno_max):
                    self.deno_max = num
                j = j + unit
            print(self.deno_max)
        except:
            print("Error")
        

    
    