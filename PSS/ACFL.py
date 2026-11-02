import math

class GLCV:
    """Valor de lógica compensatoria difusa (CFL) para un criterio.
    alfa: pendiente | gama: punto de indiferencia (S=0.5) | eme: 1 = maximizar, 0 = minimizar
    """

    def __init__(self, alfa, gama, eme):
        self.eme = eme
        self.alfa = alfa
        self.gama = gama

    # Sigmoide estable numéricamente
    def S(self, x):
        z = self.alfa * (x - self.gama)
        if z > 220:
            return 0.0
        if z < -220:
            return 1.0
        return 1.0 / (1.0 + math.exp(z))

    # Conjunción compensatoria (Media Geométrica entre los grados de verdad)
    def C(self, x, y):
        return math.sqrt(max(0.0, x * y))

    def GLCV_run(self, x):
        # Grado de cumplimiento para maximización (rendimiento) o minimización (riesgo)
        a = self.S(x)
        
        # Aplicación del parámetro m (eme = 1 para rendimiento, eme = 0 para riesgo)
        # GLCV para maximización o minimización
        a_val = pow(a, self.eme)
        b_val = pow(1 - a, 1 - self.eme)

        return a_val * b_val