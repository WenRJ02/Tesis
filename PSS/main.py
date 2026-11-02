import random
import pandas as pd
from PSS import PSO
from preferencia import preferencia

num_aleatorio = None  #si quiero reproducir las mismas opciones iniciales usar 42
fases = 6
activos = 14

def main():
    if num_aleatorio is not None:
        random.seed(num_aleatorio)

    modulo_pref = preferencia(target_satisfaction=0.85, max_display=15)
    fase = 1

    print("\n" + "=" * 60)
    print(f" FASE {fase}/{fases}: PSO multiobjetivo (sin CFL)")
    print("=" * 60)

    frente = PSO(50, 120, activos, 1.5, 2, 5).run(0, [])

    sol, perfil, sat = modulo_pref.user_interaction(
        frente,
        fase=fase,
        puede_continuar=(fase < fases))

    while not modulo_pref.terminar and fase < fases:
        fase += 1

        print("\n" + "=" * 60)
        print(f" FASE {fase}/{fases}: PSO con CFL")
        print(f" Perfil actual: {perfil}")
        print("=" * 60)

        poblacion = PSO(50, 120, activos, 1.5, 2, 5).run(1, modulo_pref.current_fuzzy_params)

        sol, perfil, sat = modulo_pref.user_interaction(
            poblacion,
            fase=fase,
            puede_continuar=(fase < fases))

        print(f" Fitness CFL de la solución elegida: "
            f"{sol.fitness * 100:.2f}%")

    # ----------------------------------- resultados de satisfacción
    historial = modulo_pref.historial

    satisfaccion_promedio = (
        sum(registro["satisfaccion_usuario"]
            for registro in historial
        ) / len(historial)
        if historial else 0
    )

    # ----------------------------------- resumen final
    print("\n" + "=" * 48)
    print(" RESUMEN DEL EXPERIMENTO")
    print("=" * 48)

    print(f" Retorno esperado final : {sol.retorno:.6f}")
    print(f" Riesgo asociado final  : {sol.riesgo:.6f}")
    print(f" Satisfacción final     : {sat * 100:.2f}%")
    print(f" Satisfacción promedio  : "
        f"{satisfaccion_promedio * 100:.2f}%")
    print(f" Perfil informativo     : {perfil}")
    print(f" Interacciones realizadas: {len(historial)}")

    if modulo_pref.meta_promedio_alcanzada:
        print(" Umbral de satisfacción : ALCANZADO")
        print(f" Meta configurada       : "
            f"{modulo_pref.target_satisfaction * 100:.0f}%")
        print(f" Primera fase con meta  : "
            f"{modulo_pref.fase_meta}")
        print(f" Primera interacción    : "
            f"{modulo_pref.interaccion_meta}")
        print(f" Satisfacción promedio al alcanzar la meta: "
              f"{modulo_pref.satisfaccion_meta * 100:.2f}%")
    else:
        print(" Umbral de satisfacción : NO ALCANZADO")
        print(f" Meta configurada       : "
            f"{modulo_pref.target_satisfaction * 100:.0f}%")

    print("=" * 48)

    # ----------------------------------- guardar historial
    pd.DataFrame(historial).to_csv("historial_preferencias.csv", index=False)

    print(" Historial guardado en historial_preferencias.csv\n")


if __name__ == "__main__":
    main()
