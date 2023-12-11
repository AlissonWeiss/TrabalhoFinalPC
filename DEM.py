import numpy as np
import matplotlib.pyplot as plt
import json


def read_json_file(_file):
    with open(_file, "r") as file:
        data = json.load(file)
        number_of_elements = len(data["coordinates"])
        coordinates_x = np.zeros((number_of_elements, 1))
        coordinates_y = np.zeros((number_of_elements, 1))

        for i in range(number_of_elements):
            coordinates_x[i] = float(data["coordinates"][i][0])
            coordinates_y[i] = float(data["coordinates"][i][1])

        connect = np.array(data["connect"])
        forces = np.array(data["forces"]).reshape(-1, 1)
        restrictions = np.array(data["restrictions"]).reshape(-1, 1)

    return number_of_elements, coordinates_x, coordinates_y, connect, forces, restrictions


def output_response(_result):
    result = {"resultado": _result.tolist()}
    with open("output_python.json", "w") as f:
        json.dump(result, f)


def main(_file_name):
    N = 600  # Steps
    h = 0.00004  # Step size
    number_of_elements, coordinates_x, coordinates_y, connections, forces, restrictions = read_json_file(_file_name)
    ndofs = 2 * number_of_elements

    forces = np.reshape(np.transpose(forces), (ndofs, 1))
    restrictions = np.reshape(np.transpose(restrictions), (ndofs, 1))

    raio = 1.0
    mass = 7850.0
    kspr = 210000000000.0

    u = np.zeros((ndofs, 1), dtype=np.float64)
    v = np.zeros((ndofs, 1), dtype=np.float64)
    a = np.zeros((ndofs, 1), dtype=np.float64)
    res = np.zeros((N, 1), dtype=np.float64)

    fi = np.zeros((ndofs, 1), dtype=np.float64)
    a[:] = (forces - fi) / mass

    for i in range(N):
        v += a * (0.5 * h)
        u += v * h

        fi = [0.0] * len(fi)
        for j in range(number_of_elements):
            if restrictions[2 * j] == 1:
                u[2 * j] = 0.0
            if restrictions[2 * j + 1] == 1:
                u[2 * j + 1] = 0.0
            xj = coordinates_x[j] + u[2 * j]
            yj = coordinates_y[j] + u[2 * j + 1]
            for index in range(1, connections[j, 0] + 1):
                k = connections[j, index]
                xk = coordinates_x[k-1] + u[2 * k - 2]
                yk = coordinates_y[k-1] + u[2 * k - 1]
                d_x = xj - xk
                d_y = yj - yk
                di = np.sqrt(d_x * d_x + d_y * d_y)
                d2 = (di - 2 * raio)
                dx = d2 * d_x / di
                dy = d2 * d_y / di
                fi[2 * j] += kspr * dx
                fi[2 * j + 1] += kspr * dy
        # Cálculo da aceleração
        a = (forces - fi) / mass
        # Cálculo da velocidade
        v += a * (0.5 * h)
        # plot
        res[i] = u[32]

    output_response(res.flatten())
    x = np.arange(1, N + 1)
    plt.plot(x, res)
    plt.show()


if __name__ == '__main__':
    main("pvi.json")
