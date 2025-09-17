def main(data: str) -> list[list[int]]:
    rows = data.strip().split('\n')
    edges = []
    verts = set()

    for row in rows:
        v_1, v_2 = row.split(",")
        edges.append((v_1, v_2))
        verts.add(v_1)
        verts.add(v_2)

    verts = sorted(verts)
    num_verts = len(verts)
    matrix = [ [0] * num_verts for _ in range(num_verts)]

    for v1, v2 in edges:
        i , j = verts.index(v1), verts.index(v2)
        matrix[i][j] = matrix[j][i] = 1
    return matrix


if __name__ == "__main__":
    data_path = ('task0.csv')
    with open(data_path, "r") as file:
        input_data = file.read()
    result = main(input_data)

    for row in result:
        print(row)
