import json
import numpy as np


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_ranking(raw: str):
    return json.loads(raw)


def collect_ids(rankings: list) -> set[int]:
    items = set()
    for r in rankings:
        for group in r:
            if not isinstance(group, list):
                group = [group]
            items.update(group)
    return items


def make_order_matrix(structure: list, size: int) -> np.ndarray:
    levels = [0] * size
    level_index = 0

    for group in structure:
        if not isinstance(group, list):
            group = [group]
        for obj in group:
            levels[obj - 1] = level_index
        level_index += 1

    result = np.zeros((size, size), dtype=int)
    for i in range(size):
        for j in range(size):
            if levels[i] >= levels[j]:
                result[i, j] = 1
    return result


def contradiction_core(mat1: np.ndarray, mat2: np.ndarray) -> list[list[int]]:
    combined = mat1 * mat2
    combined_t = mat1.T * mat2.T

    n = combined.shape[0]
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            if combined[i, j] == 0 and combined_t[i, j] == 0:
                pairs.append([i + 1, j + 1])

    return pairs


def transitive_closure(matrix: np.ndarray) -> np.ndarray:
    n = matrix.shape[0]
    closure = matrix.copy().astype(int)
    for k in range(n):
        for i in range(n):
            if closure[i, k]:
                for j in range(n):
                    if closure[k, j]:
                        closure[i, j] = 1
    return closure


def build_consistent_ranking_from_matrices(YA: np.ndarray,
                                           YB: np.ndarray,
                                           kernel: list[list[int]]) -> list:
    n = YA.shape[0]

    C = YA * YB

    for a, b in kernel:
        i = a - 1
        j = b - 1
        C[i, j] = 1
        C[j, i] = 1

    E = (C * C.T).astype(int)
    for i in range(n):
        E[i, i] = 1

    E_star = transitive_closure(E)

    visited = [False] * n
    clusters: list[list[int]] = []

    for i in range(n):
        if not visited[i]:
            current = []
            for j in range(n):
                if E_star[i, j] and E_star[j, i]:
                    visited[j] = True
                    current.append(j + 1)
            current.sort()
            clusters.append(current)

    m = len(clusters)
    adj = [[] for _ in range(m)]
    indegree = [0] * m

    for idx_a in range(m):
        for idx_b in range(m):
            if idx_a == idx_b:
                continue
            A = clusters[idx_a]
            B = clusters[idx_b]

            a_ge_b = all(C[a - 1, b - 1] == 1 for a in A for b in B)
            b_ge_a = all(C[b - 1, a - 1] == 1 for a in A for b in B)

            if a_ge_b and not b_ge_a:
                adj[idx_a].append(idx_b)
                indegree[idx_b] += 1

    from collections import deque

    queue = deque(i for i in range(m) if indegree[i] == 0)
    order: list[int] = []

    while queue:
        v = queue.popleft()
        order.append(v)
        for to in adj[v]:
            indegree[to] -= 1
            if indegree[to] == 0:
                queue.append(to)

    consistent_ranking: list = []
    for idx in order:
        cluster = clusters[idx]
        if len(cluster) == 1:
            consistent_ranking.append(cluster[0])
        else:
            consistent_ranking.append(cluster)

    return consistent_ranking


def main(raw_a: str, raw_b: str) -> dict:
    data_a = parse_ranking(raw_a)
    data_b = parse_ranking(raw_b)

    all_ids = collect_ids([data_a, data_b])
    if not all_ids:
        return {"kernel": [], "consistent_ranking": []}

    total = max(all_ids)
    YA = make_order_matrix(data_a, total)
    YB = make_order_matrix(data_b, total)

    kernel = contradiction_core(YA, YB)
    consistent = build_consistent_ranking_from_matrices(YA, YB, kernel)

    return {
        "kernel": kernel,
        "consistent_ranking": consistent,
    }


def output(name1: str, name2: str, result: dict):
    header = f"[ {name1} & {name2} ]"
    print(header)
    print(" ядро противоречий:", result["kernel"])
    print(" согласованная ранжировка:", result["consistent_ranking"][::-1], "\n")


if __name__ == "__main__":
    text_a = load_text("range_a.json")
    text_b = load_text("range_b.json")
    text_c = load_text("range_c.json")

    result_ab = main(text_a, text_b)
    result_ac = main(text_a, text_c)
    result_bc = main(text_b, text_c)

    output("A", "B", result_ab)
    output("A", "C", result_ac)
    output("B", "C", result_bc)
