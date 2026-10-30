import math

class preferencia:
    """Construcción progresiva e interactiva de las preferencias del inversionista
    mediante lógica difusa compensatoria (CFL)."""

    K_ALFA = 2 * math.log(9)

    def __init__(self, target_satisfaction=0.85, max_display=15, factor_enfoque=0.7):
        self.iteracion = 1
        self.historial = []
        self.terminar = False
        self.target_satisfaction = target_satisfaction
        self.max_display = max_display
        self.factor_enfoque = factor_enfoque     # cuánto se estrecha la sigmoide en cada ciclo
        self.rango_ref = None                    # (rango_retorno, rango_riesgo) del frente inicial
        # [alfa_ret, gama_ret, m_ret, alfa_risk, gama_risk, m_risk]; se calculan tras la 1ª elección
        self.current_fuzzy_params = None

        # Información sobre la primera vez que se alcanza la meta
        self.interaccion_meta = None
        self.fase_meta = None
        self.satisfaccion_meta = None
        self.satisfaccion_promedio = 0.0
        self.meta_promedio_alcanzada = False

    # --------------------------------- soluciones no dominadas
    def select_non_dominated(self, population):
        non_dominated = []

        for p1 in population:
            dominated = False

            for p2 in population:
                if (
                    p1.id != p2.id
                    and p2.retorno >= p1.retorno
                    and p2.riesgo <= p1.riesgo
                    and (p2.retorno > p1.retorno or p2.riesgo < p1.riesgo)):
                    dominated = True
                    break

            if not dominated:
                non_dominated.append(p1)

        unique = []
        seen = set()

        for s in non_dominated:
            key = (round(s.retorno, 8), round(s.riesgo, 8))

            if key not in seen:
                seen.add(key)
                unique.append(s)

        # Ordenar de mayor a menor retorno
        unique.sort(key=lambda s: s.retorno, reverse=True)
        return unique

    def get_diverse_sample(self, solutions, max_display=None):
        """Selecciona hasta max_display soluciones del frente de Pareto."""
        if max_display is None:
            max_display = self.max_display

        n = len(solutions)

        if max_display <= 0 or n == 0:
            return []

        if n <= max_display:
            return solutions

        if max_display == 1:
            return [solutions[0]]

        idx = [int(i * (n - 1) / (max_display - 1)) for i in range(max_display)]

        return [solutions[i] for i in idx]

    def determine_investor_profile(self, selected_sol, all_solutions):
        """Perfil informativo según la posición de la solución en el frente."""
        lo = min(s.riesgo for s in all_solutions)
        hi = max(s.riesgo for s in all_solutions)

        if hi == lo:
            return "Moderado / Medio"

        ratio = (selected_sol.riesgo - lo) / (hi - lo)

        if ratio <= 0.33:
            return "Conservador"
        elif ratio <= 0.66:
            return "Moderado / Medio"

        return "Agresivo"

    # --------------------------------------- interacción
    def obtener_seleccion(self, muestra, frente):
        print("\n" + "=" * 78)
        print(f" OPCIONES NO DOMINADAS "
            f"(muestra de {len(muestra)} soluciones)")
        print("Ordenadas de mayor a menor retorno esperado.")
        print("=" * 78)

        for i, s in enumerate(muestra, start=1):
            perfil = self.determine_investor_profile(s, frente)

            print(f" Opción [{i}]: Retorno = {s.retorno:.6f} | " f"Riesgo = {s.riesgo:.6f} ({perfil})")

        print("=" * 78)

        while True:
            try:
                c = int(input(f" Seleccione su opción preferida " f"(1 - {len(muestra)}): "))

                if 1 <= c <= len(muestra):
                    return muestra[c - 1]

            except ValueError:
                pass

            print(" Entrada no válida, intente de nuevo.")

    def pedir_satisfaccion(self):
        while True:
            try:
                v = float(
                    input(" ¿Qué tan satisfecho está con esta solución? "
                        "(0-100): "))

                if 0 <= v <= 100:
                    return v / 100

            except ValueError:
                pass

            print(" Ingrese un número entre 0 y 100.")

    def guardar_seleccion(self, sol, perfil, satisfaccion, fase):
        self.historial.append({
            "fase": fase,
            "iteracion": self.iteracion,
            "retorno": sol.retorno,
            "riesgo": sol.riesgo,
            "fitness_modelo": sol.fitness,
            "satisfaccion_usuario": satisfaccion,
            "perfil": perfil,
            "pesos": list(sol.Position),
            "fuzzy_params": (list(self.current_fuzzy_params)
                if self.current_fuzzy_params
                else None)
        })

    # ----------------------------------- construcción de preferencias
    def actualizar_preferencias(self, sol, frente, satisfaccion):
        """Actualiza los parámetros de preferencia a partir de la elección."""
        #sat = 0.5
        #sat = 0.9999 
        if self.rango_ref is None:
            r_ret = max(s.retorno for s in frente) - min(s.retorno for s in frente)
            r_rsk = max(s.riesgo for s in frente) - min(s.riesgo for s in frente)

            self.rango_ref = (max(r_ret, 1e-12), max(r_rsk, 1e-12))

        escala = self.factor_enfoque ** (self.iteracion - 1)
        """
            gama es que punto de x satisfaccion = 0.5
            alfga el punto de x donde satisfaccion = 0.9999
            
        """
        r_ret = self.rango_ref[0] * escala
        r_rsk = self.rango_ref[1] * escala

        desplaz = 0.25 * (1 - satisfaccion) 

        gama_ret = sol.retorno + desplaz * r_ret
        gama_rsk = max(sol.riesgo - desplaz * r_rsk, 0.0)

        """
            
            if sat == 0.5:
                gama = sol.retorno
            elif sat == 1:
                alfa = (math.log(1/0.999) - 1 ) / (sol.retorno - self.current_param[1])
        """
        
        self.current_fuzzy_params = [
            self.K_ALFA / r_ret,
            gama_ret,
            1,
            self.K_ALFA / r_rsk,
            gama_rsk,
            0
        ]

        self.iteracion += 1
        p = self.current_fuzzy_params

        print(f" Preferencias actualizadas: "
            f"gama_ret={p[1]:.6f} alfa_ret={p[0]:.2f} | "
            f"gama_riesgo={p[4]:.6f} alfa_riesgo={p[3]:.2f}")

    # ----------------------------------- criterio de parada
    def evaluar_parada(self, satisfaccion, fase, puede_continuar=True):
        """Evalúa la parada según la satisfacción promedio acumulada."""

        # Calcular el promedio de todas las interacciones registradas
        self.satisfaccion_promedio = sum(registro["satisfaccion_usuario"]
            for registro in self.historial ) / len(self.historial)
        
        # Registrar la primera vez que el promedio alcanza el umbral
        if (self.satisfaccion_promedio >= self.target_satisfaction and not self.meta_promedio_alcanzada):
            self.meta_promedio_alcanzada = True
            self.interaccion_meta = len(self.historial)
            self.fase_meta = fase
            self.satisfaccion_meta = self.satisfaccion_promedio
            
            print(f"\n [META ALCANZADA] Satisfacción promedio: "
                f"{self.satisfaccion_promedio * 100:.2f}% "
                f">= meta {self.target_satisfaction * 100:.0f}%.")
            print(f" Se alcanzó la meta en la fase {fase}, "
                f"interacción {self.interaccion_meta}.")

        else:
            print(f"\n Satisfacción promedio acumulada: "
                f"{self.satisfaccion_promedio * 100:.2f}%")
            
            if self.meta_promedio_alcanzada:
                print(f" La meta del {self.target_satisfaction * 100:.0f}% "
                      "ya se había alcanzado anteriormente.")
            else: print(f" Aún no se alcanza la meta del " f"{self.target_satisfaction * 100:.0f}%.")

        # Aviso de convergencia entre elecciones consecutivas
        if len(self.historial) >= 2 and self.rango_ref:
            a, b = self.historial[-2], self.historial[-1]
            
            if (abs(a["retorno"] - b["retorno"]) < 0.01 * self.rango_ref[0] and 
                abs(a["riesgo"] - b["riesgo"]) < 0.01 * self.rango_ref[1]):
                print(" Aviso: su elección casi no cambió ""respecto a la anterior (convergencia).")

        # El usuario puede seguir explorando hasta el máximo de fases
        if not puede_continuar:
            print(" Se alcanzó el máximo de fases configurado. ""El experimento finalizará.")
            return True

        respuesta = input(" ¿Desea seguir construyendo su preferencia? (si/no): " ).strip().lower()

        return respuesta in ("no", "n")
    
    # ----------------------------------- interacción completa
    def user_interaction(self, swarm, fase=1, puede_continuar=True):
        frente = self.select_non_dominated(swarm)
        muestra = self.get_diverse_sample(frente, self.max_display)
        elegida = self.obtener_seleccion(muestra, frente)
        perfil = self.determine_investor_profile(elegida, frente)

        print(f"\n Seleccionada: Retorno = {elegida.retorno:.6f}, "
            f"Riesgo = {elegida.riesgo:.6f} "
            f"| Perfil: {perfil.upper()}")

        sat = self.pedir_satisfaccion()

        self.guardar_seleccion(elegida, perfil, sat, fase)
        self.actualizar_preferencias(elegida, frente, sat)
        self.terminar = self.evaluar_parada(sat, fase, puede_continuar)

        return elegida, perfil, sat