import os
import numpy as np

def main(data: str, eroot: str) -> tuple[list[list[int]], list[list[int]], list[list[int]], list[list[int]], list[list[int]]]:
    rows = data.strip().split('\n')
    edges = []
    verts = set()

    for row in rows:
        if row.strip():
            v1, v2 = row.split(',')
            v1 = v1.strip()
            v2 = v2.strip()
            verts.add(v1)
            verts.add(v2)
            edges.append((v1, v2))

    other_verts = sorted(v for v in verts if v != eroot)
    verts = [eroot] + other_verts
    n = len(verts)
    vert_index = {v: i for i, v in enumerate(verts)}

    adj = np.zeros((n, n), dtype=bool)
    for v1, v2 in edges:
        i = vert_index[v1]
        j = vert_index[v2]
        adj[i, j] = True
    r1 = adj.astype(int)
    r2 = r1.T

    transit_r = adj.copy()
    for _ in range(1, n):
        transit_r = transit_r | (transit_r @ adj)
    r3 = (transit_r & ~adj).astype(int)
    r3 = r3.T

    r2_b = r2.astype(bool)
    r5 = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if np.any(r2_b[i] & r2_b[j]):
                r5[i, j] = 1
                r5[j, i] = 1
    return (r1.tolist(), r2.tolist(), r3.tolist(), r4.tolist(), r5.tolist())

if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(curr_dir, "task1.csv")
    with open(csv_path, "r") as file:
        inp_data = file.read()

    eroot = input("Значение корневой вершины: ").strip()
    matrices = main(inp_data, eroot)
    relations = ["r1 - управление", "r2 - подчинение", "r3 - опосредованное управление", "r4 - опосредованное подчинение", "r5 - соподчинение"]

    for rel_name, matrix in zip(relations, matrices):
        print(f"\nМатрица для {rel_name}:")
        for row in matrix:
            print(row)
