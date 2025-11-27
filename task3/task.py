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


def main(raw_a: str, raw_b: str) -> list[list[int]]:
    data_a = parse_ranking(raw_a)
    data_b = parse_ranking(raw_b)

    all_ids = collect_ids([data_a, data_b])
    if not all_ids:
        return []

    total = max(all_ids)
    m_a = make_order_matrix(data_a, total)
    m_b = make_order_matrix(data_b, total)

    return contradiction_core(m_a, m_b)


def output(name1: str, name2: str, pairs: list[list[int]]):
    header = f"[ {name1} & {name2} ]"
    print(header)
    if not pairs:
        print("противоречий не обнаружено\n")
        return

    formatted = ", ".join(f"({a},{b})" for a, b in pairs)
    print(f" найденные пары: {formatted}\n")


if __name__ == "__main__":
    text_a = load_text("range_a.json")
    text_b = load_text("range_b.json")
    text_c = load_text("range_c.json")

    output("A", "B", main(text_a, text_b))
    output("A", "C", main(text_a, text_c))
    output("B", "C", main(text_b, text_c))
