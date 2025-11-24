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


# --- Lógica de la IA (Markov) ---

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
    # Estrategia de arranque
    if not last_user_move or len(historial_usuario) < 4:
        if len(historial_usuario) < 3:
            return random.choice(OPCIONES)
        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
        return encontrar_movimiento_ganador(prediccion_usuario)

    # Estrategia Markov
    posibles_siguientes_movimientos = transition_matrix[last_user_move]
    suma_transiciones = sum(posibles_siguientes_movimientos.values())

    if suma_transiciones == 0:
        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
    else:
        prediccion_usuario = max(posibles_siguientes_movimientos,
                                 key=posibles_siguientes_movimientos.get)

    return encontrar_movimiento_ganador(prediccion_usuario)


# --- Guardado de CSV ---

def guardar_resultados_csv(historial_partidas):
    """
    Guarda los datos ronda a ronda en la misma carpeta del script.
    Los porcentajes se guardan como valores numéricos decimales (0-100).
    """
    if not historial_partidas:
        print("\nNo hay datos para guardar.")
        return

    try:
        # 1. Obtener ruta absoluta de la carpeta actual
        directorio_script = os.path.dirname(os.path.abspath(__file__))
        nombre_archivo = os.path.join(directorio_script, "resultados_partida.csv")

        # 2. Columnas
        columnas = [
            'numero_ronda',
            'jugador',
            'IA',
            'resultado',
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
        print(f" Error al guardar el archivo CSV: {e}")


# --- Función Principal ---

def jugar_partida():
    print("=== PIEDRA, PAPEL, TIJERA (IA MARKOV) ===")
    print("Escribe 'salir' para terminar.")

    datos_para_csv = []

    historial_movimientos_usuario = []
    historial_movimientos_ia = []

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

        print("-" * 50)
        jugada_j1 = input(f"Ronda {ronda_actual} >> Tu jugada: ").lower().strip()

        if jugada_j1 == 'salir':
            break

        if jugada_j1 not in OPCIONES:
            print("Error: Escribe 'piedra', 'papel' o 'tijera'.")
            continue

        # Turno IA
        jugada_j2 = obtener_eleccion_ia(historial_movimientos_usuario, last_user_move, transition_matrix)

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

        # --- MOSTRAR EFICIENCIA IA ---
        partidas_decisivas = victorias_usuario + victorias_ia
        if partidas_decisivas > 0:
            eficiencia = (victorias_ia / partidas_decisivas) * 100
            print(f" Eficiencia IA: {eficiencia:.2f}%")
        else:
            print(f" Eficiencia IA: 0.00%")
        # -----------------------------

        # Actualizar historial
        historial_movimientos_usuario.append(jugada_j1)
        historial_movimientos_ia.append(jugada_j2)

        # Calcular estadísticas evolutivas (acumulativas hasta esta ronda)
        total_jugados = len(historial_movimientos_usuario)
        c_user = Counter(historial_movimientos_usuario)
        c_ia = Counter(historial_movimientos_ia)

        # Función para calcular porcentaje acumulativo como número decimal
        def get_pct(counter, key, total):
            count = counter.get(key, 0)  # Obtener cantidad de veces que se jugó esa opción
            return round((count / total) * 100, 2) if total > 0 else 0.0

        # Guardar datos para CSV con porcentajes numéricos acumulativos
        datos_para_csv.append({
            'numero_ronda': ronda_actual,
            'jugador': jugada_j1,
            'IA': jugada_j2,
            'resultado': res_txt,
            'pct_piedra_jugador': get_pct(c_user, 'piedra', total_jugados),
            'pct_papel_jugador': get_pct(c_user, 'papel', total_jugados),
            'pct_tijera_jugador': get_pct(c_user, 'tijera', total_jugados),
            'pct_piedra_IA': get_pct(c_ia, 'piedra', total_jugados),
            'pct_papel_IA': get_pct(c_ia, 'papel', total_jugados),
            'pct_tijera_IA': get_pct(c_ia, 'tijera', total_jugados),
        })

        # IA Learning (Matriz de transición)
        if last_user_move is not None:
            transition_matrix[last_user_move][jugada_j1] += 1
        last_user_move = jugada_j1

        ronda_actual += 1

    # Guardar resultados al finalizar
    if datos_para_csv:
        print("\n--- Guardando partida ---")
        guardar_resultados_csv(datos_para_csv)
    else:
        print("No se generaron datos.")


if __name__ == "__main__":
    jugar_partida()