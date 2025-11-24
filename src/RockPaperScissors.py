import random
import csv
import os
from collections import Counter

# --- Constantes y Lógica del Juego ---

OPCIONES = ['piedra', 'papel', 'tijera']
REGLAS_VICTORIA = {
    'piedra': 'tijera',
    'papel': 'piedra',
    'tijera': 'papel'
}


# --- Lógica de la IA (Eficiencia > 40%) ---

def determinar_ganador(jugada_j1, jugada_j2):
    if jugada_j1 == jugada_j2:
        return 'empate'
    if REGLAS_VICTORIA[jugada_j1] == jugada_j2:
        return 'usuario'
    return 'ia'


def encontrar_movimiento_ganador(movimiento_a_vencer):
    if movimiento_a_vencer == 'piedra':
        return 'papel'
    elif movimiento_a_vencer == 'papel':
        return 'tijera'
    else:
        return 'piedra'


def obtener_eleccion_ia(historial_usuario, last_user_move, transition_matrix):
    """
    IA basada en Cadenas de Markov (Patrones).
    """
    # 1. Estrategia de arranque (pocos datos)
    if not last_user_move or len(historial_usuario) < 4:
        if len(historial_usuario) < 3:
            return random.choice(OPCIONES)

        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
        return encontrar_movimiento_ganador(prediccion_usuario)

    # 2. Estrategia Markov (Predicción basada en última jugada)
    posibles_siguientes_movimientos = transition_matrix[last_user_move]
    suma_transiciones = sum(posibles_siguientes_movimientos.values())

    if suma_transiciones == 0:
        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
    else:
        prediccion_usuario = max(posibles_siguientes_movimientos,
                                 key=posibles_siguientes_movimientos.get)

    return encontrar_movimiento_ganador(prediccion_usuario)


# --- Guardado de CSV (Formato Extendido) ---

def guardar_resultados_csv(historial_partidas, nombre_archivo):
    """
    Guarda los datos respetando el nuevo formato solicitado.
    """
    if not historial_partidas:
        print("\nNo hay datos para guardar.")
        return

    try:
        # Asegurarse de que la carpeta existe
        directorio = os.path.dirname(nombre_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f" Carpeta '{directorio}' creada.")

        # Definimos las columnas con los nuevos requisitos
        columnas = [
            'numero_ronda',
            'jugador',  # Antes jugada_j1
            'IA',  # Antes jugada_j2
            'resultado',  # Nueva: Victoria/Derrota/Empate
            'pct_piedra_jugador',  # % Piedra Jugador
            'pct_papel_jugador',  # % Papel Jugador
            'pct_tijera_jugador',  # % Tijera Jugador
            'pct_piedra_IA',  # % Piedra IA
            'pct_papel_IA',  # % Papel IA
            'pct_tijera_IA'  # % Tijera IA
        ]

        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.DictWriter(archivo_csv, fieldnames=columnas)

            writer.writeheader()

            for partida in historial_partidas:
                writer.writerow(partida)

        ruta_absoluta = os.path.abspath(nombre_archivo)
        print(f"\n Archivo guardado correctamente en:\n{ruta_absoluta}")

    except IOError as e:
        print(f" Error al guardar el archivo CSV: {e}")


# --- Función Principal ---

def jugar_partida():
    print("=== PIEDRA, PAPEL, TIJERA (IA MARKOV + ESTADÍSTICAS) ===")
    print("Escribe tu jugada manualmente: 'piedra', 'papel' o 'tijera'.")
    print("Escribe 'salir' para terminar y guardar.")

    datos_para_csv = []

    # Historiales
    historial_movimientos_usuario = []
    historial_movimientos_ia = []  # Nuevo historial para calcular % de la IA

    transition_matrix = {
        'piedra': {'piedra': 0, 'papel': 0, 'tijera': 0},
        'papel': {'piedra': 0, 'papel': 0, 'tijera': 0},
        'tijera': {'piedra': 0, 'papel': 0, 'tijera': 0}
    }
    last_user_move = None

    victorias_usuario = 0
    victorias_ia = 0

    ronda_actual = 1
    limite_rondas = 50

    while True:
        if ronda_actual > limite_rondas:
            print(f"\n Límite de {limite_rondas} rondas alcanzado.")
            break

        print("-" * 40)

        # 1. Entrada Manual
        jugada_j1 = input(f"Ronda {ronda_actual} >> Tu jugada: ").lower().strip()

        if jugada_j1 == 'salir':
            break

        if jugada_j1 not in OPCIONES:
            print("Error: Escribe 'piedra', 'papel' o 'tijera'.")
            continue

        # 2. IA decide (J2)
        jugada_j2 = obtener_eleccion_ia(
            historial_movimientos_usuario,
            last_user_move,
            transition_matrix
        )

        # 3. Resultado
        ganador = determinar_ganador(jugada_j1, jugada_j2)

        resultado_texto = ""
        if ganador == 'usuario':
            resultado_texto = "Victoria"
            print(f"   Jugador: {jugada_j1}  vs  IA: {jugada_j2} => ¡GANASTE!")
            victorias_usuario += 1
        elif ganador == 'ia':
            resultado_texto = "Derrota"
            print(f"   Jugador: {jugada_j1}  vs  IA: {jugada_j2} => Gana la IA")
            victorias_ia += 1
        else:
            resultado_texto = "Empate"
            print(f"   Jugador: {jugada_j1}  vs  IA: {jugada_j2} => Empate")

        # 4. Actualizar historiales (necesario antes de calcular porcentajes)
        historial_movimientos_usuario.append(jugada_j1)
        historial_movimientos_ia.append(jugada_j2)

        # 5. Cálculo de porcentajes acumulados
        total_rondas = len(historial_movimientos_usuario)
        counts_user = Counter(historial_movimientos_usuario)
        counts_ia = Counter(historial_movimientos_ia)

        # Helper lambda para calcular y formatear porcentaje
        calc_pct = lambda counts, key: "{:.2f}%".format((counts[key] / total_rondas) * 100)

        # 6. Almacenar datos para el CSV (Diccionario con nuevas claves)
        datos_para_csv.append({
            'numero_ronda': ronda_actual,
            'jugador': jugada_j1,
            'IA': jugada_j2,
            'resultado': resultado_texto,

            # Estadísticas Jugador
            'pct_piedra_jugador': calc_pct(counts_user, 'piedra'),
            'pct_papel_jugador': calc_pct(counts_user, 'papel'),
            'pct_tijera_jugador': calc_pct(counts_user, 'tijera'),

            # Estadísticas IA
            'pct_piedra_IA': calc_pct(counts_ia, 'piedra'),
            'pct_papel_IA': calc_pct(counts_ia, 'papel'),
            'pct_tijera_IA': calc_pct(counts_ia, 'tijera'),
        })

        # 7. Aprendizaje IA (Matriz de transición)
        if last_user_move is not None:
            transition_matrix[last_user_move][jugada_j1] += 1
        last_user_move = jugada_j1

        # Eficiencia en tiempo real
        total_decisivas = victorias_usuario + victorias_ia
        if total_decisivas > 0:
            eficiencia = (victorias_ia / total_decisivas) * 100
            print(f"   [Eficiencia IA: {eficiencia:.1f}%]")

        ronda_actual += 1

    # --- Fin del Juego ---
    if datos_para_csv:
        print("\n--- Guardar Resultados ---")
        ruta_input = input("Nombre del archivo (Enter para 'data/partidas.csv'): ").strip()

        if not ruta_input:
            nombre_final = "data/partidas.csv"
        else:
            nombre_final = ruta_input
            if not nombre_final.lower().endswith('.csv'):
                nombre_final += ".csv"

        guardar_resultados_csv(datos_para_csv, nombre_final)
    else:
        print("No se generaron datos.")


if __name__ == "__main__":
    jugar_partida()