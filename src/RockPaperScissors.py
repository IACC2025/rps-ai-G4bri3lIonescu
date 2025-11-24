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
    # 1. Estrategia de arranque
    if not last_user_move or len(historial_usuario) < 4:
        if len(historial_usuario) < 3:
            return random.choice(OPCIONES)

        conteo_movimientos = Counter(historial_usuario)
        prediccion_usuario = conteo_movimientos.most_common(1)[0][0]
        return encontrar_movimiento_ganador(prediccion_usuario)

    # 2. Estrategia Markov
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

def guardar_resultados_csv(historial_partidas, contadores_finales):
    """
    Guarda:
    1. Las rondas jugadas.
    2. Las columnas de porcentaje (iguales para todas las filas, ya que es el total).
    3. Se guarda en la MISMA carpeta donde está este script.
    """
    if not historial_partidas:
        print("\nNo hay datos para guardar.")
        return

    try:
        # 1. Obtener la ruta del directorio donde está ESTE archivo .py
        directorio_script = os.path.dirname(os.path.abspath(__file__))
        nombre_archivo = os.path.join(directorio_script, "resultados_finales.csv")

        # 2. Definir columnas
        columnas = [
            'numero_ronda',
            'jugador',
            'IA',
            'resultado',
            # Estadísticas finales (Total de la partida)
            'total_pct_piedra_jugador',
            'total_pct_papel_jugador',
            'total_pct_tijera_jugador',
            'total_pct_piedra_IA',
            'total_pct_papel_IA',
            'total_pct_tijera_IA'
        ]

        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.DictWriter(archivo_csv, fieldnames=columnas)
            writer.writeheader()

            # 3. Inyectar los porcentajes finales en cada fila
            for partida in historial_partidas:
                # Copiamos el diccionario de la ronda y le añadimos los totales
                fila_completa = partida.copy()
                fila_completa.update(contadores_finales)

                writer.writerow(fila_completa)

        print(f"\n Archivo guardado correctamente en:\n{nombre_archivo}")

    except IOError as e:
        print(f"Error al guardar el archivo CSV: {e}")


# --- Función Principal ---

def jugar_partida():
    print("=== PIEDRA, PAPEL, TIJERA (IA MARKOV) ===")
    print("Las estadísticas se calcularán al finalizar la partida.")

    # Listas de historial
    datos_rondas = []  # Guardará ronda, jugada y resultado
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

    # --- BUCLE DE JUEGO ---
    while True:
        if ronda_actual > limite_rondas:
            print(f"\n Límite de {limite_rondas} rondas alcanzado.")
            break

        print("-" * 40)
        jugada_j1 = input(f"Ronda {ronda_actual} >> Tu jugada (o 'salir'): ").lower().strip()

        if jugada_j1 == 'salir':
            break

        if jugada_j1 not in OPCIONES:
            print(" Error: Escribe 'piedra', 'papel' o 'tijera'.")
            continue

        # Turno IA
        jugada_j2 = obtener_eleccion_ia(historial_movimientos_usuario, last_user_move, transition_matrix)

        # Determinar ganador
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

        # Guardar datos básicos de la ronda (SIN porcentajes todavía)
        datos_rondas.append({
            'numero_ronda': ronda_actual,
            'jugador': jugada_j1,
            'IA': jugada_j2,
            'resultado': resultado_texto
        })

        # Actualizar memoria IA
        historial_movimientos_usuario.append(jugada_j1)
        historial_movimientos_ia.append(jugada_j2)

        if last_user_move is not None:
            transition_matrix[last_user_move][jugada_j1] += 1
        last_user_move = jugada_j1

        ronda_actual += 1

    # --- FIN DEL JUEGO: CÁLCULO DE ESTADÍSTICAS FINALES ---

    if datos_rondas:
        total_partidas = len(historial_movimientos_usuario)

        # Contadores
        c_user = Counter(historial_movimientos_usuario)
        c_ia = Counter(historial_movimientos_ia)

        # Función auxiliar para %
        def get_pct(counter, key, total):
            if total == 0: return "0.00%"
            return "{:.2f}%".format((counter[key] / total) * 100)

        # Diccionario con los totales finales
        stats_finales = {
            'total_pct_piedra_jugador': get_pct(c_user, 'piedra', total_partidas),
            'total_pct_papel_jugador': get_pct(c_user, 'papel', total_partidas),
            'total_pct_tijera_jugador': get_pct(c_user, 'tijera', total_partidas),
            'total_pct_piedra_IA': get_pct(c_ia, 'piedra', total_partidas),
            'total_pct_papel_IA': get_pct(c_ia, 'papel', total_partidas),
            'total_pct_tijera_IA': get_pct(c_ia, 'tijera', total_partidas),
        }

        print("\n--- Guardando Resultados ---")
        guardar_resultados_csv(datos_rondas, stats_finales)

        # Imprimir resumen en consola
        print("\n--- RESUMEN FINAL ---")
        print(f"Total Partidas: {total_partidas}")
        print(f"Victorias Jugador: {victorias_usuario}")
        print(f"Victorias IA: {victorias_ia}")
        print("Selección Jugador: ", dict(c_user))
        print("Selección IA: ", dict(c_ia))

    else:
        print("No se generaron datos.")


if __name__ == "__main__":
    jugar_partida()