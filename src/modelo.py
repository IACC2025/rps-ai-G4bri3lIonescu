"""
RPSAI - Modelo de IA para Piedra, Papel o Tijera
=================================================

Implementación completa del modelo de IA basado en Machine Learning
para predecir y ganar en Piedra, Papel o Tijera.
"""

import os
import pickle
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore", message="X does not have valid feature names")

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Configuracion de rutas
RUTA_PROYECTO = Path(__file__).parent.parent
RUTA_DATOS = RUTA_PROYECTO / "data" / "resultado_partidas.csv"
RUTA_MODELO = RUTA_PROYECTO / "models" / "modelo_entrenado.pkl"

# Mapeo de jugadas a numeros
JUGADA_A_NUM = {"piedra": 0, "papel": 1, "tijera": 2}
NUM_A_JUGADA = {0: "piedra", 1: "papel", 2: "tijera"}

# Que jugada gana a cual
GANA_A = {"piedra": "tijera", "papel": "piedra", "tijera": "papel"}
PIERDE_CONTRA = {"piedra": "papel", "papel": "tijera", "tijera": "piedra"}


# =============================================================================
# PARTE 1: EXTRACCION DE DATOS
# =============================================================================

def cargar_datos(ruta_csv: str = None) -> pd.DataFrame:
    """
    Carga los datos del CSV de partidas.
    """
    if ruta_csv is None:
        ruta_csv = RUTA_DATOS

    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    df = pd.read_csv(ruta_csv)

    # Verificar columnas necesarias
    columnas_requeridas = ['numero_ronda', 'jugador', 'IA']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"El CSV debe contener la columna: {col}")

    print(f"✓ Datos cargados: {len(df)} rondas")
    return df


def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara los datos para el modelo.
    """
    df = df.copy()

    # Convertir jugadas de texto a números
    df['jugador_num'] = df['jugador'].map(JUGADA_A_NUM)
    df['IA_num'] = df['IA'].map(JUGADA_A_NUM)

    # Crear la columna target: próxima jugada del jugador (predecir al oponente)
    df['proxima_jugada_jugador'] = df['jugador_num'].shift(-1)

    # Eliminar la última fila (no tiene próxima jugada)
    df = df.dropna(subset=['proxima_jugada_jugador'])

    print(f"✓ Datos preparados: {len(df)} rondas válidas")
    return df


# =============================================================================
# PARTE 2: FEATURE ENGINEERING
# =============================================================================

def crear_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea las features para el modelo.
    """
    df = df.copy()

    # Feature 1: Frecuencias acumuladas del jugador
    df['freq_piedra_jugador'] = (df['jugador'] == 'piedra').expanding().mean()
    df['freq_papel_jugador'] = (df['jugador'] == 'papel').expanding().mean()
    df['freq_tijera_jugador'] = (df['jugador'] == 'tijera').expanding().mean()

    # Feature 2: Lag features - jugadas anteriores
    df['jugada_anterior_1'] = df['jugador_num'].shift(1)
    df['jugada_anterior_2'] = df['jugador_num'].shift(2)
    df['jugada_anterior_3'] = df['jugador_num'].shift(3)

    # Feature 3: Resultado anterior (si existe la columna)
    if 'resultado' in df.columns:
        resultado_a_num = {'Victoria': 1, 'Derrota': -1, 'Empate': 0}
        df['resultado_anterior'] = df['resultado'].map(resultado_a_num).shift(1)

    # Feature 4: Racha actual (si existe)
    if 'racha_victorias_jugador' in df.columns:
        df['racha_victorias'] = df['racha_victorias_jugador'].shift(1)

    if 'racha_derrotas_jugador' in df.columns:
        df['racha_derrotas'] = df['racha_derrotas_jugador'].shift(1)

    # Feature 5: Fase del juego
    df['fase_juego'] = pd.cut(df['numero_ronda'], bins=3, labels=[0, 1, 2])
    df['fase_juego'] = df['fase_juego'].astype(float)

    # Feature 6: Diferencia de jugadas IA vs Jugador
    df['diff_ia_jugador'] = df['IA_num'] - df['jugador_num']

    print(f"✓ Features creadas: {len([col for col in df.columns if col.startswith(('freq_', 'jugada_', 'resultado_', 'racha_', 'fase_', 'diff_'))])} features")

    return df


def seleccionar_features(df: pd.DataFrame) -> tuple:
    """
    Selecciona las features para entrenar y el target.
    """
    # Definir columnas de features
    feature_cols = [
        'freq_piedra_jugador',
        'freq_papel_jugador',
        'freq_tijera_jugador',
        'jugada_anterior_1',
        'jugada_anterior_2',
        'jugada_anterior_3',
        'fase_juego',
        'diff_ia_jugador'
    ]

    # Agregar features opcionales si existen
    if 'resultado_anterior' in df.columns:
        feature_cols.append('resultado_anterior')
    if 'racha_victorias' in df.columns:
        feature_cols.append('racha_victorias')
    if 'racha_derrotas' in df.columns:
        feature_cols.append('racha_derrotas')

    # Eliminar filas con NaN en las features o en el target
    df_clean = df[feature_cols + ['proxima_jugada_jugador']].dropna()

    X = df_clean[feature_cols].values
    y = df_clean['proxima_jugada_jugador'].values.astype(int)

    print(f"✓ Features seleccionadas: {len(feature_cols)}")
    print(f"✓ Datos finales: {len(X)} muestras")

    return X, y


# =============================================================================
# PARTE 3: ENTRENAMIENTO Y FUNCIONAMIENTO
# =============================================================================

def entrenar_modelo(X, y, test_size: float = 0.2):
    """
    Entrena el modelo de prediccion.
    """
    print("\n" + "="*50)
    print("   ENTRENAMIENTO DE MODELOS")
    print("="*50)

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, shuffle=False
    )

    print(f"\nDatos de entrenamiento: {len(X_train)}")
    print(f"Datos de prueba: {len(X_test)}")

    # Entrenar varios modelos
    modelos = {
        'KNN': KNeighborsClassifier(n_neighbors=5),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    }

    resultados = {}

    for nombre, modelo in modelos.items():
        print(f"\n--- {nombre} ---")

        # Entrenar
        modelo.fit(X_train, y_train)

        # Predecir
        y_pred = modelo.predict(X_test)

        # Evaluar
        accuracy = accuracy_score(y_test, y_pred)
        resultados[nombre] = (modelo, accuracy)

        print(f"Accuracy: {accuracy:.2%}")
        print("\nReporte de clasificación:")
        print(classification_report(y_test, y_pred,
                                    target_names=['Piedra', 'Papel', 'Tijera'],
                                    zero_division=0))

    # Seleccionar el mejor modelo
    mejor_nombre = max(resultados, key=lambda k: resultados[k][1])
    mejor_modelo, mejor_accuracy = resultados[mejor_nombre]

    print("\n" + "="*50)
    print(f"✓ MEJOR MODELO: {mejor_nombre}")
    print(f"✓ ACCURACY: {mejor_accuracy:.2%}")
    print("="*50)

    return mejor_modelo


def guardar_modelo(modelo, ruta: str = None):
    """Guarda el modelo entrenado en un archivo."""
    if ruta is None:
        ruta = RUTA_MODELO

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "wb") as f:
        pickle.dump(modelo, f)
    print(f"\n✓ Modelo guardado en: {ruta}")


def cargar_modelo(ruta: str = None):
    """Carga un modelo previamente entrenado."""
    if ruta is None:
        ruta = RUTA_MODELO

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el modelo en: {ruta}")

    with open(ruta, "rb") as f:
        return pickle.load(f)


# =============================================================================
# PARTE 4: PREDICCION Y JUEGO
# =============================================================================

class JugadorIA:
    """
    Clase que encapsula el modelo para jugar.
    """

    def __init__(self, ruta_modelo: str = None):
        """Inicializa el jugador IA."""
        self.modelo = None
        self.historial = []  # Lista de (jugada_j1, jugada_j2)

        # Intentar cargar el modelo
        try:
            self.modelo = cargar_modelo(ruta_modelo)
            print("✓ Modelo cargado correctamente")
        except FileNotFoundError:
            print("⚠ Modelo no encontrado. La IA jugará aleatoriamente.")

    def registrar_ronda(self, jugada_j1: str, jugada_j2: str):
        """
        Registra una ronda jugada para actualizar el historial.
        """
        self.historial.append((jugada_j1, jugada_j2))

    def obtener_features_actuales(self) -> np.ndarray:
        """
        Genera las features basadas en el historial actual.
        """
        if len(self.historial) < 3:
            # No hay suficiente historial, devolver features por defecto
            return np.array([0.33, 0.33, 0.33, 0, 0, 0, 0, 0, 0, 0, 0])

        # Extraer solo las jugadas del jugador (j1)
        jugadas_j1 = [JUGADA_A_NUM[j1] for j1, j2 in self.historial]

        # Feature 1-3: Frecuencias
        total = len(jugadas_j1)
        freq_piedra = jugadas_j1.count(0) / total
        freq_papel = jugadas_j1.count(1) / total
        freq_tijera = jugadas_j1.count(2) / total

        # Feature 4-6: Lag features (últimas 3 jugadas)
        lag1 = jugadas_j1[-1] if len(jugadas_j1) >= 1 else 0
        lag2 = jugadas_j1[-2] if len(jugadas_j1) >= 2 else 0
        lag3 = jugadas_j1[-3] if len(jugadas_j1) >= 3 else 0

        # Feature 7: Fase del juego (inicio=0, medio=1, final=2)
        fase = min(2, len(self.historial) // 17)  # Asumiendo 50 rondas

        # Feature 8: Diferencia IA vs Jugador (última ronda)
        if len(self.historial) > 0:
            ultima_j1, ultima_j2 = self.historial[-1]
            diff = JUGADA_A_NUM[ultima_j2] - JUGADA_A_NUM[ultima_j1]
        else:
            diff = 0

        # Features opcionales (usar 0 si no disponibles)
        resultado_anterior = 0
        racha_victorias = 0
        racha_derrotas = 0

        features = np.array([
            freq_piedra,
            freq_papel,
            freq_tijera,
            lag1,
            lag2,
            lag3,
            fase,
            diff,
            resultado_anterior,
            racha_victorias,
            racha_derrotas
        ])

        return features

    def predecir_jugada_oponente(self) -> str:
        """
        Predice la próxima jugada del oponente.
        """
        if self.modelo is None:
            # Si no hay modelo, jugar aleatorio
            return np.random.choice(["piedra", "papel", "tijera"])

        try:
            features = self.obtener_features_actuales()
            prediccion = self.modelo.predict([features])[0]
            return NUM_A_JUGADA[int(prediccion)]
        except Exception as e:
            print(f"Error en predicción: {e}")
            return np.random.choice(["piedra", "papel", "tijera"])

    def decidir_jugada(self) -> str:
        """
        Decide qué jugada hacer para ganar al oponente.
        """
        prediccion_oponente = self.predecir_jugada_oponente()

        # Jugar lo que le gana a la predicción
        return PIERDE_CONTRA[prediccion_oponente]


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================

def main():
    """
    Función principal para entrenar el modelo.
    """
    print("="*50)
    print("   RPSAI - Entrenamiento del Modelo")
    print("="*50)

    try:
        # 1. Cargar datos
        print("\n[1/6] Cargando datos...")
        df = cargar_datos()

        # 2. Preparar datos
        print("\n[2/6] Preparando datos...")
        df = preparar_datos(df)

        # 3. Crear features
        print("\n[3/6] Creando features...")
        df = crear_features(df)

        # 4. Seleccionar features
        print("\n[4/6] Seleccionando features...")
        X, y = seleccionar_features(df)

        # 5. Entrenar modelo
        print("\n[5/6] Entrenando modelos...")
        modelo = entrenar_modelo(X, y)

        # 6. Guardar modelo
        print("\n[6/6] Guardando modelo...")
        guardar_modelo(modelo)

        print("\n" + "="*50)
        print("✓ ENTRENAMIENTO COMPLETADO")
        print("="*50)
        print("\nAhora puedes evaluar tu modelo con:")
        print("  python src/evaluador.py")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrate de:")
        print("1. Haber jugado partidas con RockPaperScissors.py")
        print("2. Que el archivo CSV esté en: data/resultado_partidas.csv")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()