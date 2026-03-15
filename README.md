# Uribe Sort

>  Algoritmo de ordenamiento estocástico con eliminación aleatoria calibrada, la calibracion se basa en el porcentaje resultante del numero de victimas de falsos positivos en el gobierno de Alvaro Uribe Velez frente al tamaño total de la poblacion, segun datos del DANE del año 2005

```
Tasa de eliminación:  6402 / 42,900,000  ≈  0.014923 %
Complejidad temporal: O(n log n)
Complejidad espacial: O(n)
```

---

## ¿Qué es Uribe Sort?

Uribe Sort es un algoritmo de ordenamiento basado en **Merge Sort** que, durante el proceso de fusión, elimina aleatoriamente una fracción calibrada de elementos del array. El resultado es un array ordenado con exactamente `round(n × 6402/42900000)` elementos menos que el original.

La eliminación no ocurre antes ni después del ordenamiento — ocurre **durante** el proceso, integrando ambas operaciones en una sola pasada de complejidad `O(n log n)`.

---

## Motivación matemática

La fracción de eliminación deriva de la razón:

```
( 6402 ÷ 42,900,000 ) × 100  =  0.014921...%
```

Para un array de tamaño `n`, el número exacto de elementos eliminados es:

```python
target = round(n * 6402 / 42_900_000)
```

| n            | Eliminaciones | Elementos restantes |
|:------------:|:-------------:|:-------------------:|
| 100          | 0             | 100                 |
| 10,000       | 1             | 9,999               |
| 100,000      | 15            | 99,985              |
| 1,000,000    | 149           | 999,851             |
| 42,900,000   | **6,402**     | 42,893,598          |

---

## Mecanismo de eliminación — Muestreo de Reservorio Inverso

El núcleo del algoritmo es la función `_should_eliminate`, que en cada decisión de colocación durante el `merge` calcula dinámicamente:

```
P(eliminar candidato) = K / R
```

donde:
- **K** = eliminaciones aún pendientes (`removals_left`)
- **R** = elementos aún por procesar (`remaining_in_arr`)

### ¿Por qué esto es correcto?

Esta es una implementación del **muestreo sin reemplazo de Knuth** (algoritmo S). La probabilidad se ajusta en cada paso garantizando dos propiedades fundamentales:

1. **Exactitud**: Al final del proceso se habrán eliminado exactamente `target` elementos — ni uno más, ni uno menos.
2. **Imparcialidad uniforme**: Cada elemento del array original tiene exactamente la misma probabilidad `K/n` de ser eliminado, independientemente de su valor o posición.

### Flujo del merge con eliminación

```
Para cada candidato (el menor de left[i] vs right[j]):

    1. Calcular  P = removals_left / remaining_in_arr
    2. Generar   r = random.random()  ∈ [0, 1)
    3. Si r < P  →  ELIMINAR  (no agregar al resultado; K -= 1)
       Si r ≥ P  →  CONSERVAR (resultado.append(candidato))
    4. En ambos casos: R -= 1
```

---

## Implementaciones

El repositorio incluye dos implementaciones con equivalencia estadística garantizada:

### `UribeSort.py` — Implementación Python pura

Merge Sort recursivo con eliminación integrada en cada paso del merge. Adecuada para arrays de hasta ~500,000 elementos.

```python
from UribeSort import uribe_sort

arr    = [5, 2, 8, 1, 9, 3, 7, 4, 6]
result = uribe_sort(arr, seed=42)
# → lista ordenada con ~0.01492% menos elementos
```

**Parámetros:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `arr` | `List[T]` | Array de entrada. Cualquier tipo comparable. |
| `seed` | `int \| None` | Semilla para reproducibilidad. Default: `None`. |

**Retorna:** `List[T]` — lista ordenada con `target` elementos menos.

---

### `Test_42900000.py` — Implementación numpy vectorizada

Para arrays de escala masiva, se usa una versión que opera en velocidad C manteniendo la misma distribución estadística. Reemplaza el muestreo de reservorio en línea por una selección vectorizada equivalente:

```python
# Equivalencia estadística:
# En lugar de decidir elemento por elemento con P = K/R,
# se pre-seleccionan K índices uniformes al azar sobre [0, n)
# El resultado es estadísticamente idéntico.

eliminate_idx = rng.choice(n, size=target, replace=False)
mask[eliminate_idx] = False
filtered = arr[mask]
filtered.sort()
```

---

## Rendimiento

Benchmarks ejecutados con `numpy 2.4.2` sobre hardware estándar:

### `UribeSort.py` (Python puro)

| n | Tiempo | Eliminados | Ordenado |
|---|--------|------------|----------|
| 20 | < 1 ms | 0 | ✓ |
| 100,000 | ~270 ms | 15 | ✓ |
| 1,000,000 | ~3,200 ms | 149 | ✓ |
| 50,000 strings | ~130 ms | 7 | ✓ |

### `Test_42900000.py` (numpy vectorizado)

| n | Generación | Ordenamiento | Total | Eliminados | Ordenado |
|---|-----------|-------------|-------|------------|----------|
| 42,900,000 int32 | 0.35 s | 0.57 s | **0.93 s** | **6,402** | ✓ |
| 42,900,000 float64 | 0.38 s | 1.04 s | **1.44 s** | **6,402** | ✓ |

Memoria del array resultante (42.9M elementos): **343 MB** (float64).

---

## Propiedades del algoritmo

| Propiedad | Valor |
|-----------|-------|
| Clase | Algoritmo de ordenamiento estocástico |
| Base | Merge Sort |
| Estabilidad | Estable (el orden relativo de elementos iguales se preserva) |
| In-place | No (requiere O(n) memoria auxiliar) |
| Determinismo | No determinista por defecto; determinista con `seed` |
| Tipos soportados | Cualquier tipo con operador `≤` definido |
| Eliminación | Exacta (`round(n × ratio)`) con distribución uniforme |

---

## Casos borde

| Entrada | Comportamiento |
|---------|----------------|
| Array vacío `[]` | Retorna `[]` |
| Un elemento `[x]` | Retorna `[x]` (sin eliminación) |
| `n` muy pequeño (target = 0) | Retorna el array ordenado completo |
| Elementos duplicados | Funciona correctamente |
| Strings | Funciona correctamente (orden lexicográfico) |

---

## Tests

El archivo `Test_42900000.py` incluye cuatro baterías de prueba:

| Test | Descripción | Verifica |
|------|-------------|---------|
| **A** | 42,900,000 enteros int32 | Eliminación exacta de 6,402 elementos + orden |
| **B** | 42,900,000 floats float64 | Ídem con tipo flotante |
| **C** | Reproducibilidad (n=1,000,000) | Misma seed → mismo resultado |
| **D** | Coherencia Python vs numpy (n=100,000) | Ambas implementaciones eliminan exactamente `target` |

### Ejecutar los tests

```bash
# Test completo con n = 42,900,000
python Test_42900000.py

# Demo con casos de uso generales
python UribeSort.py
```

**Dependencias:**
```bash
pip install numpy
```

---

## Estructura del proyecto

```
.
├── UribeSort.py          # Implementación Python pura (Merge Sort recursivo)
├── Test_42900000.py      # Test a escala + implementación numpy vectorizada
└── README.md             # Esta documentación
```

---

## Fundamento teórico

### Relación con el Algoritmo S de Knuth

El mecanismo de eliminación es una forma del **Algoritmo S** descrito en *The Art of Computer Programming, Vol. 2* (Knuth, 1997) para selección de muestra aleatoria sin reemplazo en una sola pasada. La adaptación clave es que aquí se usa de forma **inversa**: en lugar de seleccionar qué conservar, selecciona qué eliminar.

### Invariante de probabilidad

En cualquier momento del proceso, si quedan `R` elementos por procesar y `K` eliminaciones pendientes, la probabilidad de que cualquiera de los `R` elementos restantes sea eventualmente eliminado es exactamente `K/R`. Este invariante se mantiene recursivamente, lo que garantiza la uniformidad de la distribución.

### Integración con Merge Sort

La elección de Merge Sort como base no es accidental: al ser un algoritmo que procesa cada elemento exactamente una vez durante la fase de merge, ofrece un punto de intervención natural y determinista donde aplicar la decisión de eliminación sin afectar la correctitud del ordenamiento.

---

## Autor

**UribeSort** — Algoritmo diseñado y nombrado por su autor.

Implementación Python y documentación técnica generadas con asistencia de Claude (Anthropic).

---

*Tasa de eliminación exacta: `6402 / 42,900,000 = 0.00014921...` → `0.014921...%`*
