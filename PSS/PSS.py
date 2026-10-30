import os
import math
import random
import numpy as np
import pandas as pd
from ACFL import GLCV
from particle import Particle


def domina(r1, k1, r2, k2):
    """True si (retorno r1, riesgo k1) domina a (r2, k2): maximiza retorno, minimiza riesgo."""
    return (r1 >= r2 and k1 <= k2) and (r1 > r2 or k1 < k2)


class PSO:
    _cache = None  # el Excel se lee una sola vez

    def __init__(self, size, maxgen, assets, acl, acg, v, max_archive=150):
        self.swarm_size = size
        self.max_gen = maxgen
        self.assets = assets
        self.swarm = []
        self.archive = []              # archivo externo de soluciones no dominadas
        self.max_archive = max_archive
        self.Best_Swarm_Position = []
        self.Worst_Swarm_Position = []
        self.Best_Swarm_fitness = 0
        self.Worst_Swarm_fitness = 0
        self.best_return = self.best_risk = 0
        self.worst_return = self.worst_risk = 0
        self.acc_local = acl
        self.acc_global = acg
        self.velocity = v
        self.glcv_ret = None
        self.glcv_risk = None

    # ------------------------------------------------------------------ datos
    # Si es False se replica el modelo original (sin varianzas); True = riesgo de Markowitz completo w'Σw
    INCLUIR_VARIANZAS = True

    def read_data(self):
        """Hoja COV: matriz de covarianzas en las columnas 0-13 (diagonal en 0) y 'Returns' (retorno medio
        diario en %). Las varianzas de la diagonal se recuperan de la hoja 'Returns' (252 días)."""
        if PSO._cache is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
            ruta = os.path.join(base_path, 'Instance.xlsx')
            df = pd.read_excel(ruta, sheet_name='COV')
            hist = pd.read_excel(ruta, sheet_name='Returns')
            PSO._cache = (df['Returns'].to_numpy(float), df.to_numpy(float)[:, :14],
                          hist.iloc[:, :14].var().to_numpy(float))   # var ignora NaN, ddof=1 (igual que cov)
        returns, cov, var = PSO._cache
        n = self.assets
        self.asset_return = returns[:n]
        self.asset_cov = cov[:n, :n].copy()
        if self.INCLUIR_VARIANZAS:
            np.fill_diagonal(self.asset_cov, var[:n])

    # Los pesos viajan como porcentajes (suman ~100); se normalizan a [0,1] para evaluar
    def _pesos(self, position):
        w = np.asarray(position, dtype=float)
        return w / w.sum()

    def get_return(self, particle):
        return float(self._pesos(particle.Position) @ self.asset_return)

    def get_risk(self, particle):
        w = self._pesos(particle.Position)
        return float(w @ self.asset_cov @ w)   # incluye la diagonal (varianzas)

    # ---------------------------------------------------------------- fitness
    def evaluar(self, particle, fuzzy):
        particle.retorno = self.get_return(particle)
        particle.riesgo = self.get_risk(particle)
        if fuzzy == 0:
            return particle.retorno - particle.riesgo
        fr = self.glcv_ret.GLCV_run(particle.retorno)
        fk = self.glcv_risk.GLCV_run(particle.riesgo)
        return math.sqrt(fr * fk)

    # ------------------------------------------------------ archivo no dominado
    def actualizar_archivo(self, pos, ret, risk):
        for a in self.archive:
            if domina(a['ret'], a['risk'], ret, risk) or \
               (abs(a['ret'] - ret) < 1e-14 and abs(a['risk'] - risk) < 1e-14):
                return
        self.archive = [a for a in self.archive if not domina(ret, risk, a['ret'], a['risk'])]
        self.archive.append({'pos': list(pos), 'ret': ret, 'risk': risk})
        while len(self.archive) > self.max_archive:
            self._podar()

    def _podar(self):
        """Elimina la solución más 'apretada' (crowding) para conservar diversidad."""
        a = sorted(self.archive, key=lambda r: r['risk'])
        rr = (max(r['ret'] for r in a) - min(r['ret'] for r in a)) or 1.0
        rk = (max(r['risk'] for r in a) - min(r['risk'] for r in a)) or 1.0
        best_i, best_d = 1, float('inf')
        for i in range(1, len(a) - 1):
            d = abs(a[i + 1]['ret'] - a[i - 1]['ret']) / rr + abs(a[i + 1]['risk'] - a[i - 1]['risk']) / rk
            if d < best_d:
                best_i, best_d = i, d
        a.pop(best_i)
        self.archive = a

    def _archivo_a_particulas(self, fuzzy):
        out = []
        for i, rec in enumerate(self.archive):
            p = Particle()
            p.id = i
            p.Position = list(rec['pos'])
            p.Best_Personal_Position = list(rec['pos'])
            p.fitness = self.evaluar(p, fuzzy)
            out.append(p)
        return out

    # ------------------------------------------------------------------- PSO
    def run(self, fuzzy, Fuzzy_parameters):
        self.read_data()
        if fuzzy == 1:
            self.glcv_ret = GLCV(*Fuzzy_parameters[0:3])
            self.glcv_risk = GLCV(*Fuzzy_parameters[3:6])

        self.create_initial_swarm(fuzzy)
        c1, c2, velocidad = self.acc_local, self.acc_global, self.velocity

        for _ in range(self.max_gen):
            for p in self.swarm:
                mov_local = random.randint(1, 10) * c1
                mov_global = random.randint(1, 10) * c2

                if mov_local >= mov_global:
                    guia = p.get_position(1)
                elif fuzzy == 0 and self.archive:
                    guia = list(random.choice(self.archive)['pos'])   # líder del archivo (MOPSO)
                else:
                    guia = list(self.Best_Swarm_Position)

                pos = p.Move_Particle(guia, velocidad, 1, 100)
                p.Copy_Position(pos, 0, 0)
                p.fitness = self.evaluar(p, fuzzy)
                self.actualizar_archivo(pos, p.retorno, p.riesgo)

                if fuzzy == 0:
                    # Mejor personal por dominancia (multiobjetivo real)
                    if domina(p.retorno, p.riesgo, p.Best_Personal_retorno, p.Best_Personal_riesgo) or \
                       (not domina(p.Best_Personal_retorno, p.Best_Personal_riesgo, p.retorno, p.riesgo)
                            and random.random() < 0.5):
                        self._set_mejor_personal(p)
                else:
                    if p.fitness > p.Best_Personal_fitness:
                        self._set_mejor_personal(p)
                    if p.fitness > self.Best_Swarm_fitness:
                        self.Best_Swarm_fitness = p.fitness
                        self.Best_Swarm_Position = p.get_position(0)
                        self.best_return, self.best_risk = p.retorno, p.riesgo
                    if p.fitness < self.Worst_Swarm_fitness:
                        self.Worst_Swarm_fitness = p.fitness
                        self.Worst_Swarm_Position = p.get_position(0)
                        self.worst_return, self.worst_risk = p.retorno, p.riesgo

        # Se devuelve el frente no dominado acumulado, no el estado final del enjambre
        return self._archivo_a_particulas(fuzzy)

    def _set_mejor_personal(self, p):
        p.Best_Personal_fitness = p.fitness
        p.Best_Personal_Position = p.get_position(0)
        p.Best_Personal_retorno = p.retorno
        p.Best_Personal_riesgo = p.riesgo

    def create_initial_swarm(self, fuzzy):
        weight = math.trunc(100 / self.assets)
        base = [weight] * self.assets
        base[0] += 100 - weight * self.assets

        for id_part in range(self.swarm_size):
            p = Particle()
            p.id = id_part
            pos = p.Move_Particle(base, 50, 1, 100)    # parte siempre de la solución equitativa
            p.Copy_Position(pos, 0, 1)
            p.Copy_Position(pos, 1, 1)
            p.fitness = self.evaluar(p, fuzzy)
            self._set_mejor_personal(p)
            self.swarm.append(p)
            self.actualizar_archivo(pos, p.retorno, p.riesgo)

        best = max(self.swarm, key=lambda s: s.fitness)
        worst = min(self.swarm, key=lambda s: s.fitness)
        self.Best_Swarm_fitness, self.Best_Swarm_Position = best.fitness, best.get_position(0)
        self.best_return, self.best_risk = best.retorno, best.riesgo
        self.Worst_Swarm_fitness, self.Worst_Swarm_Position = worst.fitness, worst.get_position(0)
        self.worst_return, self.worst_risk = worst.retorno, worst.riesgo

    def print_sol(self, sol, fuzzy, parametros):
        p = Particle()
        p.Position = list(sol)
        if fuzzy == 1:
            self.glcv_ret = GLCV(*parametros[0:3])
            self.glcv_risk = GLCV(*parametros[3:6])
        fit = self.evaluar(p, fuzzy)   # misma fórmula que en la optimización
        print(f"fitness={fit:.6f} retorno={p.retorno:.6f} riesgo={p.riesgo:.6f}")