import json

import matplotlib.pyplot as plt
import numpy as np


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


def choose_particle_to_follow(forces: np.ndarray, restrictions: np.ndarray, choice: str):
    if choice == "with_force":
        for i in range(len(forces)):
            if forces[i] != 0:
                return i

    if choice == "fixed":
        for i in range(len(restrictions) - 1):
            if restrictions[i] != 0 and restrictions[i + 1] == 1:
                return i

    return 0, 0


def main(_file_name):
    N = 600  # Número de passos na simulação
    h = 0.00004  # Tamanho do passo na simulação
    # Leitura do arquivo JSON e extração de elementos, coordenadas, conexões, forças e restrições
    number_of_elements, coordinates_x, coordinates_y, connections, forces, restrictions = read_json_file(_file_name)
    ndofs = 2 * number_of_elements  # Número de graus de liberdade

    # Reorganização dos vetores de forças e restrições para o formato correto
    forces = np.reshape(np.transpose(forces), (ndofs, 1))
    restrictions = np.reshape(np.transpose(restrictions), (ndofs, 1))

    raio = 1.0  # Raio das partículas
    mass = 7850.0  # Massa das partículas
    kspr = 210000000000.0  # Constante de rigidez da mola

    # Inicialização dos vetores de deslocamento, velocidade e aceleração das partículas
    u = np.zeros((ndofs, 1), dtype=np.float64)  # Deslocamento
    v = np.zeros((ndofs, 1), dtype=np.float64)  # Velocidade
    a = np.zeros((ndofs, 1), dtype=np.float64)  # Aceleração

    # Vetor para armazenar resultados para plotagem
    res = np.zeros((N, 1), dtype=np.float64)

    fi = np.zeros((ndofs, 1), dtype=np.float64)  # Vetor de força interna
    a[:] = (forces - fi) / mass  # Cálculo inicial da aceleração

    # Escolha de uma partícula específica para acompanhar durante a simulação
    particle_to_follow = choose_particle_to_follow(forces=forces, restrictions=restrictions, choice="with_force")
    # Loop principal da simulação
    for i in range(N):
        v += a * (0.5 * h)  # Atualização da velocidade
        u += v * h  # Atualização do deslocamento

        fi = [0.0] * len(fi)  # Reinicialização do vetor de força interna
        # Cálculo das forças entre as partículas
        for j in range(number_of_elements):
            # Aplicação de restrições, se for particula fixa, a variação é zero
            if restrictions[2 * j] == 1:
                u[2 * j] = 0.0
            if restrictions[2 * j + 1] == 1:
                u[2 * j + 1] = 0.0
            # Cálculo de posição e força para cada conexão
            xj = coordinates_x[j] + u[2 * j]
            yj = coordinates_y[j] + u[2 * j + 1]
            for index in range(1, len(connections[j])):
                k = connections[j, index]
                if k == 0:
                    continue
                # Calcula a posição atual no eixo x da partícula k
                xk = coordinates_x[k - 1] + u[2 * k - 2]
                # Calcula a posição atual no eixo y da partícula k
                yk = coordinates_y[k - 1] + u[2 * k - 1]
                # Determina a diferença no eixo x entre as partículas j e k
                d_x = xj - xk
                # Determina a diferença no eixo y entre as partículas j e k
                d_y = yj - yk
                # Calcula a distância entre as partículas j e k
                di = np.sqrt(d_x * d_x + d_y * d_y)
                # Calcula o quanto as partículas estão se sobrepondo ou afastadas, descontando seus diâmetros
                d2 = (di - 2 * raio)
                # Ajusta a diferença de posição no eixo x, mantendo a direção da força
                dx = d2 * d_x / di
                # Ajusta a diferença de posição no eixo y, mantendo a direção da força
                dy = d2 * d_y / di
                # Atualiza a força interna no eixo x para a partícula j
                fi[2 * j] += kspr * dx
                # Atualiza a força interna no eixo y para a partícula j
                fi[2 * j + 1] += kspr * dy

        # Atualização da aceleração
        a = (forces - fi) / mass
        # Atualização da velocidade
        v += a * (0.5 * h)
        # Armazenamento do deslocamento da partícula específica para plotagem
        res[i] = u[particle_to_follow]

    # Salva os resultados em um arquivo JSON
    output_response(res.flatten())
    x = np.arange(1, N + 1)
    # Plotagem das variações de posição da partícula escolhida ao longo do tempo
    plt.plot(x, res)
    plt.show()
