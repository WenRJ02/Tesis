from PSS import PSO
from ACFL import GLCV


# alfa gama m
Fuzzy_parametros_agresivo =  [ 16.2831, 17.6299, 1, 
    0.003769, 90.9431, 0 ]

Fuzzy_parametros_medio =  [ 10.4677, 17.3157, 1, 
    0.0078, -1173, 0 ]

Fuzzy_parametros_conservador =  [ 5.05337, 16.373, 1, 
    0.01214, -1594.3, 0  ]

############################################

# alfa gama m
Fuzzy_parametros_agresivo1 =  [ 2.67705, 21.636, 1, 
                               0.00518675, -4128.5, 0 ]

Fuzzy_parametros_medio1 =  [ 3.0615, 21.204, 1, 
                            0.004177, -4557.2, 0 ]

Fuzzy_parametros_conservador1 =  [5.3784, 19.908, 1, 
                                  0.003923, -4700.2, 0  ]

v1 = [1,1.5,2]
v2 = [1,1.5,2]
v3 = [1,5,10]

for i in range(30):
    Fuzzy = PSO(50, 120, 14, 1.5, 2, 5)
    Fuzzy.run(1, Fuzzy_parametros_conservador1)


"""
for vel in range(3):
    
    print("\n Corrida "+ str(vel) + "\n")
    
    for run2 in range(30):
        #size, maxgen, assets, acl,acg,v
        Fuzzy_PSO = PSO(50, 120, 14, 1.5, 1,  v3[vel])
        Fuzzy_PSO.run(1, Fuzzy_parametros_conservador1)
    


    """
"""
for run in range(20):
    print("\n Corrida "+ str(run) + "\n")
    for ac_l in range(3):  
        ac_l = v1[ac_l]
        
        for ac_g in range(3):   
            ac_g = v1[ac_g]
            
            for v in range(3):
                v = v3[v]
                #size, maxgen, assets
                #print(str(v) + " " + str(ac_g) + " " + str(ac_l))
                
                Fuzzy_PSO = PSO(50, 120, 14, ac_l, ac_g, v)
                Fuzzy_PSO.run(1, Fuzzy_parametros_conservador1)

"""