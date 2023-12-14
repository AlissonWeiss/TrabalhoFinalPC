import json

import numpy as np


def read_json(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return np.array(data['connect']), np.array(data['temperatures']), int(data['rows']), int(data['columns'])


def solve_temperatures(connections, temperatures):
    nn = len(temperatures)

    # Inicializa a matriz A e o vetor b para o sistema linear Ax = b
    A = np.zeros((nn, nn))
    b = np.zeros((nn, 1))

    # Itera sobre cada ponto na placa
    for e in range(nn):
        if temperatures[e, 0] == 1:
            # Para pontos com temperaturas conhecidas, define a equação Ti = valor conhecido
            A[e, e] = 1
            b[e, 0] = temperatures[e, 1]
        else:
            # Para pontos com temperaturas desconhecidas, aplica a discretização da equação de
            # Laplace usando o método das diferenças finitas.
            # A equação de Laplace é: ∇²T = 0
            # Quando discretizada em uma grade regular, isso leva a -4 * Ti + T(i+1) + T(i-1) + T(i+n) + T(i-n) = 0
            A[e, e] = -4
            for j in connections[e][1:len(connections[e])]:
                if j != 0:
                    A[e, j - 1] += 1

    # Resolve o sistema para encontrar as temperaturas desconhecidas
    return np.linalg.solve(A, b)


def save_into_json_file(m_temperatures, rows, columns):

    temperatures = []

    for row in m_temperatures:
        temp = []
        for item in row:
            temp.append(float(item))
        temperatures.append(temp)

    file_data = {
        "temperatures": temperatures,
        "rows": rows,
        "columns": columns
    }

    with open("output_pvc.json", "w") as f:
        f.write(json.dumps(file_data))


if __name__ == '__main__':
    connections, temperatures, n_rows, n_columns = read_json("pvc3.json")

    calculated_temperatures = solve_temperatures(connections, temperatures)

    save_into_json_file(np.reshape(calculated_temperatures, (n_rows, n_columns)), n_rows, n_columns)
