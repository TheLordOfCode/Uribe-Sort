"""
Test UribeSort con n = 42,900,000
============================================
Para arrays de esta escala se usa una versión vectorizada con numpy
que mantiene exactamente la misma distribución estadística que el
algoritmo recursivo, pero opera a velocidad C en lugar de Python.

Equivalencia estadística garantizada:
    En el Uribe Sort recursivo, cada elemento tiene la misma
    probabilidad de ser eliminado (muestreo uniforme sin reemplazo).
    Pre-seleccionar K=6402 índices aleatorios uniformes sobre [0, n)
    y luego hacer argsort produce el resultado idéntico en distribución:
    mismo orden, misma tasa de eliminación, misma imparcialidad.

Eliminación objetivo exacta:
    target = round(42_900_000 × 6402/42_900_000) = 6402 elementos
"""

import numpy as np
import random
import time
import sys
import os

# ── Constantes ────────────────────────────────────────────────────────────────
N                       = 42_900_000
ELIMINATION_NUMERATOR   = 6402
ELIMINATION_DENOMINATOR = 42_900_000
ELIMINATION_RATIO       = ELIMINATION_NUMERATOR / ELIMINATION_DENOMINATOR
TARGET_REMOVALS         = round(N * ELIMINATION_RATIO)   # = 6402 exacto


# ── Versión numpy-optimizada (equivalente estadístico) ────────────────────────

def stochastic_sort_numpy(arr: np.ndarray, seed: int = None,
                          target: int = None) -> np.ndarray:
    """
    Ordena `arr` y elimina exactamente `target` elementos de forma
    uniforme aleatoria.  Si `target` es None, se calcula con la razón
    global (6402/42900000) sobre el tamaño real del array.

    Pasos:
      1. Seleccionar `target` índices únicos al azar  (O(n))
      2. Crear máscara booleana para conservar los demás (O(n))
      3. Ordenar el sub-array resultante con numpy sort   (O(n log n), C)

    La selección de índices es equivalente al muestreo de reservorio
    del Uribe Sort recursivo: cada elemento tiene la misma probabilidad
    K/n de ser eliminado.
    """
    rng = np.random.default_rng(seed)
    n   = len(arr)

    if target is None:
        target = round(n * ELIMINATION_RATIO)

    # Índices a ELIMINAR (muestra uniforme sin reemplazo)
    eliminate_idx = rng.choice(n, size=target, replace=False)

    # Máscara: True = conservar
    mask = np.ones(n, dtype=bool)
    mask[eliminate_idx] = False

    # Sub-array filtrado → ordenar
    filtered = arr[mask]
    filtered.sort()          # in-place, usa IntroSort (O(n log n))

    return filtered


# ── Verificaciones ────────────────────────────────────────────────────────────

def verify(original: np.ndarray, result: np.ndarray) -> dict:
    n_in     = len(original)
    n_out    = len(result)
    removed  = n_in - n_out
    pct      = removed / n_in * 100
    is_sorted = bool(np.all(result[:-1] <= result[1:]))

    return {
        "n_input":         n_in,
        "n_output":        n_out,
        "removed":         removed,
        "target":          TARGET_REMOVALS,
        "exact_match":     removed == TARGET_REMOVALS,
        "pct_removed":     pct,
        "pct_target":      ELIMINATION_RATIO * 100,
        "is_sorted":       is_sorted,
    }


def print_banner(title: str):
    print("\n" + "═" * 58)
    print(f"  {title}")
    print("═" * 58)


def print_stats(stats: dict, elapsed_gen: float, elapsed_sort: float):
    total = elapsed_gen + elapsed_sort
    print(f"  Elementos entrada   : {stats['n_input']:>14,}")
    print(f"  Elementos salida    : {stats['n_output']:>14,}")
    print(f"  Eliminados          : {stats['removed']:>14,}  (objetivo: {stats['target']:,})")
    print(f"  % eliminado         : {stats['pct_removed']:>14.6f}%")
    print(f"  % objetivo          : {stats['pct_target']:>14.6f}%")
    print(f"  Eliminación exacta  : {'✓ Sí' if stats['exact_match'] else '✗ No':>14}")
    print(f"  Resultado ordenado  : {'✓ Sí' if stats['is_sorted'] else '✗ No':>14}")
    print("  ─────────────────────────────────────────────────")
    print(f"  Tiempo generación   : {elapsed_gen:>11.3f} s")
    print(f"  Tiempo ordenamiento : {elapsed_sort:>11.3f} s")
    print(f"  Tiempo total        : {total:>11.3f} s")
    mem_mb = stats['n_output'] * 8 / 1e6
    print(f"  Memoria resultado   : {mem_mb:>11.1f} MB  (float64)")


# ── Tests ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Test A: n = 42,900,000 enteros aleatorios ─────────────────────────────
    print_banner(f"Test A — Enteros aleatorios  (n = {N:,})")

    print(f"\n  Generando {N:,} enteros int32 aleatorios...")
    t0  = time.perf_counter()
    rng = np.random.default_rng(42)
    arr = rng.integers(-10_000_000, 10_000_000, size=N, dtype=np.int32)
    t_gen = time.perf_counter() - t0
    print(f"  Generación completada en {t_gen:.3f} s")
    print(f"  Memoria del array: {arr.nbytes / 1e6:.1f} MB")

    print(f"\n  Ejecutando UribeSort (target = {TARGET_REMOVALS:,} eliminaciones)...")
    t0     = time.perf_counter()
    result = stochastic_sort_numpy(arr, seed=2024)
    t_sort = time.perf_counter() - t0

    stats = verify(arr, result)
    print()
    print_stats(stats, t_gen, t_sort)

    # ── Test B: n = 42,900,000 floats ─────────────────────────────────────────
    print_banner(f"Test B — Floats aleatorios  (n = {N:,})")

    print(f"\n  Generando {N:,} floats float64 aleatorios...")
    t0    = time.perf_counter()
    arr_f = rng.random(size=N, dtype=np.float64)
    t_gen = time.perf_counter() - t0
    print(f"  Generación completada en {t_gen:.3f} s")

    print("\n  Ejecutando UribeSort...")
    t0     = time.perf_counter()
    res_f  = stochastic_sort_numpy(arr_f, seed=777)
    t_sort = time.perf_counter() - t0

    stats_f = verify(arr_f, res_f)
    print()
    print_stats(stats_f, t_gen, t_sort)

    # ── Test C: reproducibilidad ───────────────────────────────────────────────
    print_banner("Test C — Reproducibilidad con seed fija")
    arr_small = rng.integers(0, 1_000_000, size=1_000_000, dtype=np.int32)
    r1 = stochastic_sort_numpy(arr_small, seed=9999)
    r2 = stochastic_sort_numpy(arr_small, seed=9999)
    identical = np.array_equal(r1, r2)
    print(f"\n  Misma seed → resultados idénticos: {'✓ Sí' if identical else '✗ No'}")

    # ── Test D: coherencia con versión Python (n pequeño) ─────────────────────
    print_banner("Test D — Coherencia algoritmo Python vs numpy (n = 100,000)")
    sys.path.insert(0, os.path.dirname(__file__))
    from UribeSort import stochastic_uribe_sort, ELIMINATION_RATIO as ER

    arr_py      = list(rng.integers(0, 10000, size=100_000).tolist())
    target_100k = round(100_000 * ER)
    out_py = stochastic_uribe_sort(arr_py, seed=123)
    out_np = stochastic_sort_numpy(np.array(arr_py, dtype=np.int64), seed=123,
                                   target=target_100k)
    py_removed  = len(arr_py) - len(out_py)
    np_removed  = len(arr_py) - len(out_np)

    py_sorted = all(out_py[i] <= out_py[i+1] for i in range(len(out_py)-1))
    np_sorted = bool(np.all(out_np[:-1] <= out_np[1:]))

    print(f"\n  Objetivo eliminaciones (n=100k) : {target_100k}")
    print(f"  Versión Python  — eliminados    : {py_removed}  | ordenado: {'✓' if py_sorted else '✗'}")
    print(f"  Versión numpy   — eliminados    : {np_removed}  | ordenado: {'✓' if np_sorted else '✗'}")
    print(f"  Ambas versiones correctas       : {'✓ Sí' if (py_removed == target_100k == np_removed) else '✗ No'}")

    # ── Resumen final ──────────────────────────────────────────────────────────
    print_banner("Resumen final")
    all_ok = (
        stats["exact_match"] and stats["is_sorted"] and
        stats_f["exact_match"] and stats_f["is_sorted"] and
        identical and
        py_removed == target_100k == np_removed
    )
    print(f"\n  Todos los tests pasaron: {'✓ Sí' if all_ok else '✗ No'}\n")