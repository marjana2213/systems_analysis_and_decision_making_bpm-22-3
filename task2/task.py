import os
import numpy as np
import math
from typing import Tuple, List


def compute_entropy(matrices: List[np.ndarray]) -> Tuple[float, float]:
    n = len(matrices[0])
    k = len(matrices)
    full_entropy = 0.0

    for matrix in matrices:
        for i in range(n):
            for j in range(n):
                if i != j:
                    p_ij = matrix[i, j] / (n - 1)
                    if p_ij > 0:
                        full_entropy += p_ij * math.log2(p_ij)

    H = -full_entropy
    H_max = (1 / math.e) * n * k
    h = H / H_max if H_max > 0 else 0
    return H, h

def build_edge_variants(edges: List[Tuple[str, str]], verts: List[str]) -> List[List[Tuple[str, str]]]:
    available_edges = []
    n = len(verts)
    for i in range(n):
        for j in range(n):
            if i != j:
                available_edges.append((verts[i], verts[j]))

    existing_edges = set(edges)
    new_p_edges = []
    for edge in available_edges:
        if edge not in existing_edges:
            new_p_edges.append(edge)

    variants = []
    for r_i in range(len(edges)):
        for new_edge in new_p_edges:
            new_edges = edges.copy()
            new_edges[r_i] = new_edge
            variants.append(new_edges)
    return variants


def main(s: str, e: str) -> Tuple[float, float]:
    rows = s.strip().split('\n')
    edges = []
    verts = set()

    for line in rows:
        if line.strip():
            v1, v2 = line.split(',')
            v1 = v1.strip()
            v2 = v2.strip()
            verts.add(v1)
            verts.add(v2)
            edges.append((v1, v2))

    other_verts = sorted(v for v in verts if v != e)
    verts = [e] + other_verts
    n = len(verts)
    vert_index = {v: i for i, v in enumerate(verts)}
    all_variants = build_edge_variants(edges, verts)
    best_H, best_h = -float('inf'), 0.0

    for perm_edges in all_variants:
        adj = np.zeros((n, n), dtype=bool)
        for v1, v2 in perm_edges:
            i = vert_index[v1]
            j = vert_index[v2]
            adj[i, j] = True

        r1 = adj.astype(int)
        r2 = r1.T

        t_r = adj.copy()
        for _ in range(1, n):
            t_r = t_r | (t_r @ adj)
        r3 = (t_r & ~adj).astype(int)
        r4 = r3.T

        r2_b = r2.astype(bool)
        r5 = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(i + 1, n):
                if np.any(r2_b[i] & r2_b[j]):
                    r5[i, j] = 1
                    r5[j, i] = 1
        matrices = [r1, r2, r3, r4, r5]
        H, h = compute_entropy(matrices)

        if H > best_H:
            best_H, best_h = H, h
    return best_H, best_h


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(curr_dir, "task2.csv")
    with open(csv_path, "r") as file:
        input_data = file.read()
    eroot = input("Значение корневой вершины: ").strip()
    H, h = main(input_data, eroot)

    print(f"\nРезультат:")
    print(f"H(M,R) = {H:.4f}")
    print(f"h(M,R) = {h:.4f}")
