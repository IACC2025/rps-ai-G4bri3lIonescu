# Documentacion de Recogida de Datos

**Alumno:** Alin Gabriel Ionescu

## Formato del CSV

Tu archivo `data/partidas.csv` debe tener **minimo** estas columnas:

| Columna | Descripcion | Ejemplo |
|---------|-------------|---------|
| `numero_ronda` | Numero de la ronda (1, 2, 3...) | 1 |
| `jugada_j1` | Jugada del jugador 1 | piedra |
| `jugada_j2` | Jugada del jugador 2 (oponente) | papel |

### Ejemplo de CSV minimo:

```csv
numero_ronda,jugada_j1,jugada_j2
1,piedra,papel
2,tijera,piedra
3,papel,papel
4,piedra,tijera
...
```

---

## Como recogiste los datos?

Marca con [x] el metodo usado y describe brevemente:

### Metodo de recogida:

- [x] **Programa propio**: Cree un programa para jugar y guardar datos
- [ ] **Manual**: Jugue partidas y apunte los resultados a mano
- [ ] **Aplicacion/Web externa**: Use una app y exporte los datos
- [ ] **Otro**: _________________

### Descripcion del proceso:

```
(Explica aqui como recogiste los datos. Si usaste un programa,
describe brevemente como funciona. Si fue manual, explica el proceso.)

Los datos han sido recogidos mediante 3 registros:

1 - Entrada Manual del Usuario.
El programa solicita al usuario introducir una de las 3 opciones disponibles (piedra, papel o tijera).

2 - Respuesta de la IA.
La IA utiliza un algoritmo basado en Cadenas de Markov para predecir el próximo movimiento del oponente, a su vez
analiza al historial de jugadas del usuario y construye una matriz de transición que registra el tipo de jugada
que realiza el oponente despues de cada movimiento.

3 - Registro Automático.
Cada ronda se guarda en memoria y al terminar la partida (ya sea al llegar a la partida Nº50 o escribiendo "salir"),
el programa exporta los datos a un archivo .csv.



```
---

## Datos adicionales capturados

Si capturaste datos extra ademas de los basicos, marcalos aqui:

- [ ] `tiempo_reaccion_ms` - Tiempo que tardo el jugador en responder
- [ ] `timestamp` - Fecha/hora de cada jugada
- [ ] `sesion` - ID de sesion de juego
- [x] `resultado` - victoria/derrota/empate
- [x] Otro: racha de victorias/derrotas y porcentaje de uso de cada elemento.

### Descripcion de datos adicionales:

```
(Si capturaste datos extra, explica aqui por que y como los usas)

El procentaje de uso de cada elemento se guarda mediante actualizaciones de historial añadiendo cada
movimiento a la lista donde se acumulan. Lo siguiente es utilizar un Counter para contar la cantidad de 
veces que aparece cada elemento, se calculan los porcentajes y por último se almacenan en un .csv.


```

---

## Estadisticas del dataset

- **Total de rondas:** _____
- **Numero de sesiones/partidas:** 6
- **Contra cuantas personas diferentes:** 1

### Tipo de IA:

- [ ] **IA Especifica**: Entrenada para ganar a UNA persona concreta
  - Nombre/identificador del oponente: _________________
- [x] **IA General**: Entrenada para ganar a cualquier oponente
