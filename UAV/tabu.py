import argparse
import numpy as np
import matplotlib.pyplot as plt
import time


class UAVManager:
    def __init__(self, file_path, seed):
        self.file_path = file_path
        self.seed = seed
        self.uav_data = []
        self.total_cost = 0
        self.read_file()
       

    def read_file(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            D = int(lines[0].strip())
            current_line = 1

            for i in range(D):
                aterrizaje_info = list(map(float, lines[current_line].strip().split()))
                uav = {
                    'index': i,
                    'tiempo_aterrizaje_menor': aterrizaje_info[0],
                    'tiempo_aterrizaje_ideal': aterrizaje_info[1],
                    'tiempo_aterrizaje_maximo' : aterrizaje_info[2],
                    'tiempos_aterrizaje': [],
                    'orden': None,
                    'penalizacion': 0,
                    'tiempo_aterrizaje_asignado': 0
                }
                current_line += 1

                tiempos_aterrizaje = []
                while len(tiempos_aterrizaje) < D:
                    tiempos = list(map(float, lines[current_line].strip().split()))
                    tiempos_aterrizaje.extend(tiempos)
                    current_line += 1

                uav['tiempos_aterrizaje'] = tiempos_aterrizaje
                self.uav_data.append(uav)

    def solve_greedy(self):
            # Ordenar los UAVs por su tiempo de aterrizaje ideal en orden ascendente
            sorted_uav_data = sorted(self.uav_data, key=lambda x: x['tiempo_aterrizaje_ideal'])

            # Inicializar variables
            self.total_cost = 0
            time = 0

            # Iterar sobre los UAVs ordenados
            for i, uav in enumerate(sorted_uav_data):
                # Encontrar el tiempo de aterrizaje mas cercano al tiempo ideal sin violar los limites de tiempo minimo y maximo
                closest_time = max(uav['tiempo_aterrizaje_menor'], min(uav['tiempo_aterrizaje_maximo'], max(time, uav['tiempo_aterrizaje_ideal'])))
                
                # Calcular la penalizacion asociada a este tiempo de aterrizaje
                penalty = abs(closest_time - uav['tiempo_aterrizaje_ideal'])

                # Actualizar el tiempo de aterrizaje asignado y la penalizacion para este UAV
                uav['tiempo_aterrizaje_asignado'] = closest_time
                uav['penalizacion'] = penalty

                # Actualizar el costo total y el tiempo actual
                self.total_cost += penalty
                time = closest_time + uav['tiempos_aterrizaje'][i]

                # Asignar el orden de aterrizaje
                uav['orden'] = i

    def solve_greedy_stochastic(self):
        # Establecer la semilla para la generación de números aleatorios
        rng = np.random.default_rng(self.seed)

        # Ordenar los UAVs por su tiempo de aterrizaje ideal en orden ascendente
        sorted_uav_data = sorted(self.uav_data, key=lambda x: x['tiempo_aterrizaje_ideal'])

        # Inicializar variables
        self.total_cost = 0
        time = 0

        # Iterar sobre los UAVs
        for i in range(len(self.uav_data)):
            # Obtener el valor mínimo entre la longitud de la lista ordenada y un número fijo (p. ej., 3)
            k = min(len(sorted_uav_data), 3)

            # Crear una distribución de probabilidad exponencial para favorecer a los primeros UAVs
            probabilities = [np.exp(-0.5 * j) for j in range(k)]
            probabilities = [p / sum(probabilities) for p in probabilities]

            # Seleccionar uno de los k UAVs más cercanos al tiempo ideal actual
            idx = rng.choice(range(k), p=probabilities)
            selected_uav = sorted_uav_data.pop(idx)

            # Encontrar el tiempo de aterrizaje más cercano al tiempo ideal sin violar los límites de tiempo mínimo y máximo
            closest_time = max(selected_uav['tiempo_aterrizaje_menor'], min(selected_uav['tiempo_aterrizaje_maximo'], max(time, selected_uav['tiempo_aterrizaje_ideal'])))

            # Calcular la penalización asociada a este tiempo de aterrizaje
            penalty = abs(closest_time - selected_uav['tiempo_aterrizaje_ideal'])

            # Actualizar el tiempo de aterrizaje asignado y la penalización para este UAV
            selected_uav['tiempo_aterrizaje_asignado'] = closest_time
            selected_uav['penalizacion'] = penalty

            # Actualizar el costo total y el tiempo actual
            self.total_cost += penalty
            time = closest_time + selected_uav['tiempos_aterrizaje'][i]

            # Asignar el orden de aterrizaje
            selected_uav['orden'] = i

    def solve_tabu_search(self, initial_solution):
        tabu_list = []
        best_solution = initial_solution.copy()
        best_cost = self.calculate_total_cost(initial_solution)

        # Set the Tabu Search parameters (you can modify these values)
        tabu_list_size = 10
        iterations = 100

        for _ in range(iterations):
            best_neighbor = None

            # Iterate over all neighbor solutions
            for i in range(len(best_solution)):
                for j in range(i + 1, len(best_solution)):
                    neighbor_solution = best_solution.copy()
                    neighbor_solution[i]['tiempo_aterrizaje_asignado'], neighbor_solution[j]['tiempo_aterrizaje_asignado'] = (
                        neighbor_solution[j]['tiempo_aterrizaje_asignado'],
                        neighbor_solution[i]['tiempo_aterrizaje_asignado']
                    )
                    neighbor_cost = self.calculate_total_cost(neighbor_solution)

                    # Check if the neighbor solution is not in the tabu list and has a lower cost
                    if neighbor_solution not in tabu_list and neighbor_cost < best_cost:
                        best_neighbor = neighbor_solution
                        best_cost = neighbor_cost

            # Update the current solution with the best neighbor solution
            if best_neighbor is not None:
                best_solution = best_neighbor

            # Add the current solution to the tabu list
            tabu_list.append(best_solution)

            # Remove the oldest solution from the tabu list if it exceeds the size limit
            if len(tabu_list) > tabu_list_size:
                tabu_list.pop(0)

        return best_solution


    def calculate_total_cost(self, solution):
        total_cost = 0

        for uav in solution:
            total_cost += uav['penalizacion']

        return total_cost

    def display_data(self):
        print("Costo total:", self.total_cost)
        sorted_uav_data = sorted(self.uav_data, key=lambda uav: uav['orden'])
        print("Orden de aterrizaje:", [uav['index'] for uav in sorted_uav_data])


    def get_sorted_data(self):
        sorted_uav_data = sorted(self.uav_data, key=lambda uav: uav['orden'])
        return list([uav['index'] for uav in sorted_uav_data])
    
    def plot_schedule(self):
        fig, ax = plt.subplots()

        for uav in self.uav_data:
            y = uav['orden']

            # Draw points at the minimum, ideal, maximum, and assigned landing times
            ax.plot(uav['tiempo_aterrizaje_menor'], y, marker='o', markersize=6, color='red')
            ax.plot(uav['tiempo_aterrizaje_ideal'], y, marker='o', markersize=6, color='green')
            ax.plot(uav['tiempo_aterrizaje_maximo'], y, marker='o', markersize=6, color='blue')
            ax.plot(uav['tiempo_aterrizaje_asignado'], y, marker='o', markersize=8, color='black')

            # Show the values of the minimum, ideal, maximum, and assigned landing times
            ax.text(uav['tiempo_aterrizaje_menor'], y, f"{uav['tiempo_aterrizaje_menor']:.1f}", ha='right', va='bottom',
                    color='red')
            ax.text(uav['tiempo_aterrizaje_ideal'], y, f"{uav['tiempo_aterrizaje_ideal']:.1f}", ha='right', va='bottom',
                    color='green')
            ax.text(uav['tiempo_aterrizaje_maximo'], y, f"{uav['tiempo_aterrizaje_maximo']:.1f}", ha='left', va='bottom',
                    color='blue')
            ax.text(uav['tiempo_aterrizaje_asignado'], y, f"{uav['tiempo_aterrizaje_asignado']:.1f}", ha='left', va='bottom',
                    color='black')

        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Orden de aterrizaje')
        ax.set_title('Programacion de aterrizaje de UAVs')
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    parser.add_argument("--seed", type=int, default=0, help="Semilla para la generacion de numeros aleatorios")
    args = parser.parse_args()

    """
    Spoilers (rango 0 al 5000):
        - Titan.txt: La mejor semilla es 291 con un costo total de 165.0
        - Deimos.txt: La mejor semilla es 3556 con un costo total de 14190.0
        - Europa.txt La mejor semilla es 1072 con un costo total de 2547.0
    """

    uav_manager = UAVManager(args.file_path, args.seed)
    initial_solution_greedy = uav_manager.uav_data.copy()

    # Generate the initial solution using the greedy algorithm
    uav_manager.solve_greedy()

    start_time = time.time()
    best_solution_greedy = uav_manager.solve_tabu_search(initial_solution_greedy)
    end_time = time.time()

    # Update the UAV manager with the best solution found
    uav_manager.uav_data = best_solution_greedy
    uav_manager.total_cost = uav_manager.calculate_total_cost(best_solution_greedy)

    print(f"Tiempo de ejecucion tabu search usando solución greedy como inicial: {end_time - start_time:.4f} segundos")
    uav_manager.display_data()
    #uav_manager.plot_schedule()

    uav_manager = UAVManager(args.file_path, args.seed)
    initial_solution_greedy_stochastic = uav_manager.uav_data.copy()

    # Generate the initial solution using the greedy-stochastic algorithm
    uav_manager.solve_greedy_stochastic()

    start_time = time.time()
    best_solution_greedy_stochastic = uav_manager.solve_tabu_search(initial_solution_greedy_stochastic)
    end_time = time.time()

    # Update the UAV manager with the best solution found
    uav_manager.uav_data = best_solution_greedy_stochastic
    uav_manager.total_cost = uav_manager.calculate_total_cost(best_solution_greedy_stochastic)
    print("-------------------------------------------------------------------------------------------------")
    print(f"Tiempo de ejecucion tabu search usando solución greedy-stochastic como inicial : {end_time - start_time:.4f} segundos")
    uav_manager.display_data()
    #uav_manager.plot_schedule()


