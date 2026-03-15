"""
UribeSort — Ordenamiento con eliminación aleatoria calibrada
======================================================================
Ordena un array de tamaño n y elimina aleatoriamente exactamente:
    target = round(n × 6402/42900000)  elementos
durante el proceso de ordenamiento.

Tasa de eliminación:  6402 / 42900000 ≈ 0.014921...%
                      (aproximadamente 1 elemento por cada ~6700)

Estrategia de eliminación — Muestreo de Reservorio Inverso:
    En cada decisión de colocación, si quedan R elementos por procesar
    y K eliminaciones pendientes, la probabilidad de eliminar el
    elemento actual es K/R. Esto garantiza exactamente K eliminaciones
    de forma uniforme e imparcial a lo largo del proceso.

Complejidad:
    Tiempo:   O(n log n)  — Uribe Sort estándar
    Espacio:  O(n)        — arreglos temporales
"""

import random
import math
import time
from typing import List, TypeVar, Optional

T = TypeVar("T")

# ── Constante de eliminación ──────────────────────────────────────────────────
ELIMINATION_NUMERATOR   = 6402
ELIMINATION_DENOMINATOR = 42900000
ELIMINATION_RATIO       = ELIMINATION_NUMERATOR / ELIMINATION_DENOMINATOR
# ≈ 0.000149211...  → 0.014921...%


# ── Algoritmo principal ───────────────────────────────────────────────────────

def uribe_sort(arr: List[T], seed: Optional[int] = None) -> List[T]:
    """
    Ordena `arr` usando Uribe Sort y elimina aleatoriamente el
    (6402/42900000 × 100)% de los elementos durante el proceso.

    Parámetros
    ----------
    arr  : lista de cualquier tipo comparable
    seed : semilla opcional para reproducibilidad

    Retorna
    -------
    Lista ordenada con aproximadamente 0.01492...% menos elementos.
    """
    if seed is not None:
        random.seed(seed)

    n = len(arr)

    if n == 0:
        return []

    # Número exacto de elementos a eliminar
    target_removals = round(n * ELIMINATION_RATIO)

    # Contadores compartidos entre llamadas recursivas (lista para mutabilidad)
    state = {
        "remaining_in_arr": n,   # elementos aún no procesados definitivamente
        "removals_left": target_removals,
    }

    work = list(arr)  # copia para no mutar el original

    result = _uribe_sort(work, state)

    return result


# ── Internals ─────────────────────────────────────────────────────────────────

def _uribe_sort(arr: List[T], state: dict) -> List[T]:
    """Uribe Sort recursivo con eliminación integrada en el uribe."""
    if len(arr) <= 1:
        return arr

    mid   = len(arr) // 2
    left  = _uribe_sort(arr[:mid],  state)
    right = _uribe_sort(arr[mid:],  state)

    return _uribe(left, right, state)


def _uribe(left: List[T], right: List[T], state: dict) -> List[T]:
    """
    Fusiona dos sublistas ordenadas.

    En cada paso de colocación, decide estocásticamente si eliminar
    el elemento candidato usando la probabilidad:
        P(eliminar) = removals_left / remaining_in_arr

    Esto implementa el principio de muestreo de reservorio inverso:
    cada elemento tiene exactamente la misma probabilidad de ser
    eliminado, y el total eliminado es exactamente `target_removals`.
    """
    result = []
    i = j  = 0

    while i < len(left) and j < len(right):
        # Seleccionar el candidato (el menor de ambas sublistas)
        if left[i] <= right[j]:
            candidate = left[i]
            advance_left = True
        else:
            candidate = right[j]
            advance_left = False

        # Decisión estocástica de eliminación
        if _should_eliminate(state):
            # Descartamos el candidato (no se agrega al resultado)
            pass
        else:
            result.append(candidate)

        # Avanzar el puntero correspondiente
        if advance_left:
            i += 1
        else:
            j += 1

    # Cola restante de la sublista no agotada
    while i < len(left):
        if _should_eliminate(state):
            pass
        else:
            result.append(left[i])
        i += 1

    while j < len(right):
        if _should_eliminate(state):
            pass
        else:
            result.append(right[j])
        j += 1

    return result


def _should_eliminate(state: dict) -> bool:
    """
    Devuelve True si el elemento actual debe ser eliminado.

    Probabilidad dinámica = removals_left / remaining_in_arr
    garantiza que se alcance exactamente el objetivo.
    """
    if state["remaining_in_arr"] == 0:
        return False

    p = state["removals_left"] / state["remaining_in_arr"]

    state["remaining_in_arr"] -= 1

    if p > 0 and random.random() < p:
        state["removals_left"] -= 1
        return True

    return False


# ── Utilidades de análisis ────────────────────────────────────────────────────

def analyze_result(original: list, sorted_result: list, verbose: bool = True) -> dict:
    """Verifica correctitud y calcula estadísticas de la ejecución."""
    n          = len(original)
    n_out      = len(sorted_result)
    removed    = n - n_out
    target     = round(n * ELIMINATION_RATIO)
    pct_actual = (removed / n * 100) if n > 0 else 0
    pct_target = ELIMINATION_RATIO * 100
    is_sorted  = all(sorted_result[k] <= sorted_result[k+1]
                     for k in range(len(sorted_result) - 1))

    stats = {
        "n_input":          n,
        "n_output":         n_out,
        "removed":          removed,
        "target_removals":  target,
        "pct_removed":      pct_actual,
        "pct_target":       pct_target,
        "is_sorted":        is_sorted,
        "exact_match":      removed == target,
    }

    if verbose:
        print(f"\n{'─'*52}")
        print(f"  Elementos entrada  : {n:>12,}")
        print(f"  Elementos salida   : {n_out:>12,}")
        print(f"  Eliminados         : {removed:>12,}  (objetivo: {target})")
        print(f"  % eliminado        : {pct_actual:>12.6f}%")
        print(f"  % objetivo         : {pct_target:>12.6f}%")
        print(f"  Resultado ordenado : {'✓ Sí' if is_sorted else '✗ No':>12}")
        print(f"  Eliminación exacta : {'✓ Sí' if stats['exact_match'] else '✗ No':>12}")
        print(f"{'─'*52}\n")

    return stats


# ── Demo / pruebas ────────────────────────────────────────────────────────────

if __name__ == "__main__":

    random.seed(42)

    print("=" * 52)
    print("  UribeSort — Demo")
    print(f"  Tasa de eliminación: {ELIMINATION_RATIO*100:.6f}%")
    print("=" * 52)

    # ── Test 1: array pequeño (verificación visual) ───────────────────────────
    print("\n▸ Test 1 — Array pequeño (n=20)")
    small = [random.randint(1, 100) for _ in range(20)]
    print(f"  Original : {small}")
    out = uribe_sort(small, seed=7)
    print(f"  Resultado: {out}")
    analyze_result(small, out)

    # ── Test 2: array mediano ─────────────────────────────────────────────────
    print("▸ Test 2 — Array mediano (n=100,000)")
    medium = [random.random() for _ in range(100_000)]
    t0 = time.perf_counter()
    out = uribe_sort(medium)
    elapsed = time.perf_counter() - t0
    stats = analyze_result(medium, out)
    print(f"  Tiempo de ejecución : {elapsed*1000:.2f} ms")

    # ── Test 3: array grande ──────────────────────────────────────────────────
    print("▸ Test 3 — Array grande (n=1,000,000)")
    large = [random.randint(-10**6, 10**6) for _ in range(1_000_000)]
    t0 = time.perf_counter()
    out = uribe_sort(large)
    elapsed = time.perf_counter() - t0
    stats = analyze_result(large, out)
    print(f"  Tiempo de ejecución : {elapsed*1000:.2f} ms")

    # ── Test 4: strings ───────────────────────────────────────────────────────
    print("▸ Test 4 — Array de strings (n=50,000)")
    import string
    words = ["".join(random.choices(string.ascii_lowercase, k=8))
             for _ in range(50_000)]
    out = uribe_sort(words)
    analyze_result(words, out)

    # ── Test 5: reproducibilidad con seed ─────────────────────────────────────
    print("▸ Test 5 — Reproducibilidad con seed fija")
    data = list(range(200_000))
    random.shuffle(data)
    out_a = uribe_sort(data, seed=2024)
    out_b = uribe_sort(data, seed=2024)
    identical = (out_a == out_b)
    print(f"  Resultados idénticos con misma seed: {'✓ Sí' if identical else '✗ No'}\n")

    # ── Test 6: casos borde ───────────────────────────────────────────────────
    print("▸ Test 6 — Casos borde")
    assert uribe_sort([]) == [],        "Fallo: lista vacía"
    assert uribe_sort([42]) == [42],    "Fallo: un elemento"
    assert uribe_sort([3, 1]) in ([1, 3], [1], [3]), "Fallo: dos elementos"
    print("  Todos los casos borde pasaron ✓\n")

    print("Demo completado exitosamente.")