import json


def mu_piecewise(x, pts):
    pts = sorted(pts, key=lambda p: p[0])

    if x <= pts[0][0]:
        return float(pts[0][1])
    if x >= pts[-1][0]:
        return float(pts[-1][1])

    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]

        if x1 <= x <= x2:
            x1 = float(x1)
            x2 = float(x2)
            y1 = float(y1)
            y2 = float(y2)

            if x2 == x1:
                return max(y1, y2)

            k = (y2 - y1) / (x2 - x1)
            return y1 + k * (x - x1)

    return 0.0


def fuzz_one(value, lv_terms):
    res = {}
    for term in lv_terms:
        name = term["id"]
        pts = term["points"]
        res[name] = mu_piecewise(value, pts)
    return res


def get_minmax_x(lv_terms):
    xs = []
    for term in lv_terms:
        for p in term["points"]:
            xs.append(float(p[0]))
    return min(xs), max(xs)


def mean_of_max(x_list, mu_list):
    if not mu_list:
        return 0.0

    m = max(mu_list)
    if m <= 0:
        return float(x_list[0])

    idxs = [i for i, v in enumerate(mu_list) if abs(v - m) <= 1e-12]
    left = x_list[idxs[0]]
    right = x_list[idxs[-1]]
    return (left + right) / 2.0


def main(temperature_terms_json: str, control_terms_json: str, rules_json: str, temperature: float) -> float:
    inp = json.loads(temperature_terms_json)
    out = json.loads(control_terms_json)
    rules = json.loads(rules_json)

    in_terms = inp["температура"]
    out_terms = out["нагрев"]

    in_mu = fuzz_one(float(temperature), in_terms)

    out_map = {t["id"]: t["points"] for t in out_terms}

    x_min, x_max = get_minmax_x(out_terms)
    n = 1001
    step = (x_max - x_min) / (n - 1) if n > 1 else 1.0
    xs = [x_min + i * step for i in range(n)]

    agg = [0.0] * n

    for pair in rules:
        in_name = pair[0]
        out_name = pair[1]

        act = float(in_mu.get(in_name, 0.0))
        pts = out_map.get(out_name)
        if not pts or act <= 0:
            continue

        for i, x in enumerate(xs):
            y = mu_piecewise(x, pts)
            clipped = act if act < y else y
            if clipped > agg[i]:
                agg[i] = clipped

    return float(mean_of_max(xs, agg))


if __name__ == "__main__":
    with open("temperature_terms.json", "r", encoding="utf-8") as f:
        a = f.read()
    with open("control_terms.json", "r", encoding="utf-8") as f:
        b = f.read()
    with open("rules.json", "r", encoding="utf-8") as f:
        c = f.read()
    temperature = 19.0

    print(f"Для температуры {temperature} значение оптимального управления: {main(a, b, c, temperature):.2f}")
