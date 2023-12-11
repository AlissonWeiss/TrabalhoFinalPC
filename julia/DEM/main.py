import json
import numpy as np
import matplotlib.pyplot as plt

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

def output_res(res):
    dict_res = {"resultado": res}
    with open("output.json", "w") as f:
        json.dump(dict_res, f)

def main(_file_name):
    print(".DEM")
    # read input file
    N = 600
    h = 0.00004
    number_of_elements, coordinates_x, coordinates_y, connections, forces, restrictions = read_json_file(_file_name)
    ndofs = 2 * number_of_elements
    raio = 1.0
    mass = 7850.0
    kspr = 210000000000.0
    # [Your connectivity matrix, F and restrs arrays should be converted to Python numpy arrays here]

    F = np.reshape(np.transpose(forces), (ndofs, 1))
    restrs = np.reshape(np.transpose(restrictions), (ndofs, 1))

    u = np.zeros((ndofs, 1))
    v = np.zeros((ndofs, 1))
    a = np.zeros((ndofs, 1))
    res = np.zeros(N)

    fi = np.zeros((ndofs, 1))
    a = (F - fi) / mass
    for i in range(N):
        v += a * (0.5 * h)
        u += v * h
        # contact
        fi.fill(0.0)
        for j in range(number_of_elements):
            if restrs[2*j] == 1:
                u[2*j] = 0.0
            if restrs[2*j + 1] == 1:
                u[2*j + 1] = 0.0
            xj = coordinates_x[j] + u[2*j]
            yj = coordinates_y[j] + u[2*j + 1]
            for index in range(connections[j, 0]):
                k = connections[j, index + 1]
                xk = coordinates_x[k] + u[2*k]
                yk = coordinates_y[k] + u[2*k + 1]
                dX = xj - xk
                dY = yj - yk
                di = np.sqrt(dX**2 + dY**2)
                d2 = (di - 2*raio)
                dx = d2 * dX / di
                dy = d2 * dY / di
                fi[2*j] += kspr * dx
                fi[2*j + 1] += kspr * dy
        a = (F - fi) / mass
        v += a * (0.5 * h)
        res[i] = u[33]

    output_res(res.tolist())
    x = range(1, N + 1)
    plt.plot(x, res)
    plt.show()

# Call the main function with your JSON file
main("pvi.json")
