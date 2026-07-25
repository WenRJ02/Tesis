# Intente hacer algo pero no se si este bien lo que intente implementar :-:
# Aunque me parecería muy bien si pudiera implemertar mi mejora aparte
# para que mi aporte se notara un poco más :-:

# Bueno igual creo que no funciono lo que hice ;-;

# Intente hacer un nuevo modulo por así decirlo, en el cual se mostrara especificamente
# mi aportacion, realmente no se si lo estoy haciendo bien :-:
"""Cree algunos atributos según lo que creo que se usarían al momento 
de construir la preferencia del inversionista"""
class Preferencia:

    def __init__(self):
        # Número de interacciones que el usuario tiene con el sistema
        self.iteracion = 1

        # Aqui se almacenarian las selecciones del usuario
        self.historial = []

        # Aqui es donde se construiria el perfil del inversionista
        self.preferencias = None

        # Indica si el usuario desea terminar
        self.terminar = False

# Aqui intente definir algunos metodos para que me ayudaran  
# con la construcción de la preferencia

# Se obtienen las soluciones elegidas por el usuario 
    def obtener_seleccion(self, soluciones):
        
        print("\n=========== Soluciones Generadas ==============\n")
        
        for i, p in enumerate(soluciones):
            
            print(f"""
Solucion {i+1}

Retorno : {p.retorno:.4f}
Riesgo  : {p.riesgo:.4f}
Fitness : {p.fitness:.4f}

 ------------------------                  
""")

        seleccion = input(
            "\nseleccione una o varias soluciones (ejemplo: 1,5,8): "
        )
            
        return seleccion

# Se guardan las selecciones hechas por el usuario
    def guardar_seleccion(self, seleccion):

        self.historial.append(seleccion)

# Aqui se construiría el perfil del inversionista usando el historial de sus elecciones
    def actualizar_preferencias(self):
        """
        (Por el momento esta vacio ;-;)
        """
        pass

