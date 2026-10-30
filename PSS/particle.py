import random

class Particle:

    def __init__(self):
        self.Position = []
        self.Best_Personal_Position = []
        self.Best_Personal_fitness = 0
        self.Best_Personal_retorno = 0
        self.Best_Personal_riesgo = 0
        self.grado_retorno = None
        self.grado_riesgo = None
        self.fitness = 0
        self.retorno = 0
        self.riesgo = 0
        self.id = 0

    def Move_Particle(self, solution, moves, lower_bound, upper_bound):
        """Búsqueda local: transfiere peso entre activos. Trabaja sobre una COPIA
        (antes mutaba la lista original y cada partícula partía de la anterior)."""
        new = list(solution)
        n = len(new)
        for _ in range(moves):
            pos1, pos2 = random.sample(range(n), 2)
            if new[pos1] != 0:
                change = round(new[pos1] / random.randint(lower_bound, upper_bound), 1)
                new[pos1] = round(new[pos1] - change, 2)
                new[pos2] = round(new[pos2] + change, 2)
        return new

    def Copy_Position(self, new_position, is_best, is_new):
        # is_best: 0 = posición actual, 1 = mejor personal (is_new se conserva por compatibilidad)
        if is_best == 0:
            self.Position = list(new_position)
        else:
            self.Best_Personal_Position = list(new_position)

    def get_position(self, flag_best):
        return list(self.Best_Personal_Position if flag_best else self.Position)
    