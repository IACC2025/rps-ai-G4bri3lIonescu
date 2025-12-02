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


# --- Lógica de la IA (Markov de 2do Orden) ---

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


def obtener_eleccion_ia(historial_usuario, transition_matrix):
    # Rondas mínimas necesarias para usar el modelo de 2do orden
    MIN_MARKOV_ROUNDS = 4

    # 1. Estrategia de arranque
    if len(historial_usuario) < MIN_MARKOV_ROUNDS:
        if len(historial_usuario) < 3:
            return random.choice(OPCIONES)

        # Predecir el movimiento más común de las primeras rondas
        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
        print("   [IA: Estrategia de Arranque]", end="")
        return encontrar_movimiento_ganador(prediccion_usuario)

    # 2. Clave para el modelo de 2do orden: (jugada_n-2, jugada_n-1)
    move_n_minus_2 = historial_usuario[-2]
    move_n_minus_1 = historial_usuario[-1]
    key = (move_n_minus_2, move_n_minus_1)

    prediccion_usuario = None

    if key in transition_matrix:
        posibles_siguientes_movimientos = transition_matrix[key]
        suma_transiciones = sum(posibles_siguientes_movimientos.values())

        if suma_transiciones > 0:
            # Predicción Markov de 2do orden: Elegir el movimiento más probable después de la secuencia
            prediccion_usuario = max(posibles_siguientes_movimientos,
                                     key=posibles_siguientes_movimientos.get)
            print("   [IA: Predicción Markov 2do Orden]", end="")

    if prediccion_usuario is None:
        # 3. Fallback: Si la secuencia es nueva o no hay datos, usar el movimiento más común de todo el historial.
        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
        print("   [IA: Fallback Frecuencia]", end="")

    return encontrar_movimiento_ganador(prediccion_usuario)


# --- Guardado de CSV (Sin cambios funcionales) ---

def guardar_resultados_csv(historial_partidas):
    """
    Guarda los datos ronda a ronda en la carpeta data del proyecto.
    """
    if not historial_partidas:
        print("\nNo hay datos para guardar.")
        return

    try:
        # 1. Definir la ruta específica del proyecto
        ruta_proyecto = r"C:\Users\Alumno\PycharmProjects\rps-ai-G4bri3lIonescu\data"

        # Crear el directorio si no existe
        os.makedirs(ruta_proyecto, exist_ok=True)

        # Nombre del archivo
        # Se asume 'resultado_partidas.csv' es el nombre que el archivo 'modelo.py' espera
        nombre_archivo = os.path.join(ruta_proyecto, "resultado_partidas.csv")

        # 2. Columnas
        columnas = [
            'numero_ronda',
            'jugador',
            'IA',
            'resultado',
            'racha_victorias_jugador',
            'racha_derrotas_jugador',
            'racha_victorias_IA',
            'racha_derrotas_IA',
            'pct_piedra_jugador',
            'pct_papel_jugador',
            'pct_tijera_jugador',
            'pct_piedra_IA',
            'pct_papel_IA',
            'pct_tijera_IA'
        ]

        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.DictWriter(archivo_csv, fieldnames=columnas)
            writer.writeheader()

            for fila in historial_partidas:
                writer.writerow(fila)

        print(f"\n Archivo guardado correctamente en:\n{nombre_archivo}")

    except IOError as e:
        print(f"Error al guardar el archivo CSV: {e}")


# --- Función Principal ---

def jugar_partida():
    print("=== PIEDRA, PAPEL, TIJERA (IA MARKOV 2DO ORDEN) ===")
    print("Escribe 'salir' para terminar.")

    datos_para_csv = []

    historial_movimientos_usuario = []
    historial_movimientos_ia = []

    # Matriz de Transición de 2do orden: Clave = (Jugada_n-2, Jugada_n-1)
    transition_matrix = {}

    # last_user_move ya no es necesario, el historial completo se usa para la predicción
    # last_user_move = None

    victorias_usuario = 0
    victorias_ia = 0
    ronda_actual = 1
    limite_rondas = 50

    # Variables para racha
    racha_actual_jugador = 0
    racha_actual_ia = 0
    ultimo_ganador = None

    while True:
        if ronda_actual > limite_rondas:
            print(f"\n Límite de {limite_rondas} rondas alcanzado.")
            break

        print("-" * 50)
        jugada_j1 = input(f"Ronda {ronda_actual} >> Tu jugada: ").lower().strip()

        if jugada_j1 == 'salir':
            break

        if jugada_j1 not in OPCIONES:
            print("Error: Escribe 'piedra', 'papel' o 'tijera'.")
            continue

        # Turno IA: Solo se pasa el historial y la matriz de transición
        jugada_j2 = obtener_eleccion_ia(historial_movimientos_usuario, transition_matrix)

        # Ganador
        ganador = determinar_ganador(jugada_j1, jugada_j2)

        res_txt = "Empate"
        if ganador == 'usuario':
            res_txt = "Victoria"
            victorias_usuario += 1
        elif ganador == 'ia':
            res_txt = "Derrota"
            victorias_ia += 1

        print(f"   Jugador: {jugada_j1} | IA: {jugada_j2} => {res_txt.upper()}")

        # --- ACTUALIZAR RACHAS (Lógica sin cambios) ---
        if ganador == 'empate':
            racha_actual_jugador = 0
            racha_actual_ia = 0
            ultimo_ganador = 'empate'
        elif ganador == 'usuario':
            if ultimo_ganador == 'usuario':
                racha_actual_jugador += 1
            else:
                racha_actual_jugador = 1
            racha_actual_ia = 0
            ultimo_ganador = 'usuario'
        else:
            if ultimo_ganador == 'ia':
                racha_actual_ia += 1
            else:
                racha_actual_ia = 1
            racha_actual_jugador = 0
            ultimo_ganador = 'ia'

        racha_derrotas_jugador = racha_actual_ia if ultimo_ganador == 'ia' else 0
        racha_derrotas_ia = racha_actual_jugador if ultimo_ganador == 'usuario' else 0
        # -------------------------

        # --- MOSTRAR EFICIENCIA IA ---
        partidas_decisivas = victorias_usuario + victorias_ia
        if partidas_decisivas > 0:
            eficiencia = (victorias_ia / partidas_decisivas) * 100
            print(f" Eficiencia IA: {eficiencia:.2f}%")
        else:
            print(f" Eficiencia IA: 0.00%")
        # -----------------------------

        # Actualizar historial ANTES de aprender
        historial_movimientos_usuario.append(jugada_j1)
        historial_movimientos_ia.append(jugada_j2)

        # --- IA Learning (Matriz de transición de 2do orden) ---
        if len(historial_movimientos_usuario) >= 3:
            # La clave es la secuencia que lleva a la jugada actual
            move_n_minus_2 = historial_movimientos_usuario[-3]
            move_n_minus_1 = historial_movimientos_usuario[-2]
            next_move = historial_movimientos_usuario[-1]  # jugada_j1

            key = (move_n_minus_2, move_n_minus_1)

            if key not in transition_matrix:
                transition_matrix[key] = {'piedra': 0, 'papel': 0, 'tijera': 0}

            transition_matrix[key][next_move] += 1
        # ----------------------------------------------------

        # Calcular estadísticas evolutivas (acumulativas hasta esta ronda)
        total_jugados = len(historial_movimientos_usuario)
        c_user = Counter(historial_movimientos_usuario)
        c_ia = Counter(historial_movimientos_ia)

        def get_pct(counter, key, total):
            count = counter.get(key, 0)
            return round((count / total) * 100, 2) if total > 0 else 0.0

        datos_para_csv.append({
            'numero_ronda': ronda_actual,
            'jugador': jugada_j1,
            'IA': jugada_j2,
            'resultado': res_txt,
            'racha_victorias_jugador': racha_actual_jugador,
            'racha_derrotas_jugador': racha_derrotas_jugador,
            'racha_victorias_IA': racha_actual_ia,
            'racha_derrotas_IA': racha_derrotas_ia,
            'pct_piedra_jugador': get_pct(c_user, 'piedra', total_jugados),
            'pct_papel_jugador': get_pct(c_user, 'papel', total_jugados),
            'pct_tijera_jugador': get_pct(c_user, 'tijera', total_jugados),
            'pct_piedra_IA': get_pct(c_ia, 'piedra', total_jugados),
            'pct_papel_IA': get_pct(c_ia, 'papel', total_jugados),
            'pct_tijera_IA': get_pct(c_ia, 'tijera', total_jugados),
        })

        ronda_actual += 1

    # Guardar resultados al finalizar
    if datos_para_csv:
        print("\n--- Guardando partida ---")
        guardar_resultados_csv(datos_para_csv)
    else:
        print("No se generaron datos.")


if __name__ == "__main__":
    jugar_partida()