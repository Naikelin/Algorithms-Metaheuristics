import argparse
import numpy as np
import copy
from greedy import UAVManager as GreedyUAVManager

class UAVManager(GreedyUAVManager):
    def __init__(self, file_path,):
        super().__init__(file_path)
        print("Antes de Hill Climbing:")
        self.display_initial_solution()
        self.hill_climbing()


    def calculate_cost(self, uav_data):
        total_cost = 0
        for uav in uav_data:
            total_cost += uav['penalizacion']
        return total_cost

    def display_data(self):
        print("\nDespués de Hill Climbing:")
        for uav in self.uav_data:
            print(f"UAV {uav['orden']}: Tiempo de aterrizaje asignado: {uav['tiempo_aterrizaje_asignado']}")
        print("Costo total mejorado:", self.total_cost)


    def generate_neighbor_solution(self, uav_data):
        neighbor_uav_data = copy.deepcopy(uav_data)
        i, j = np.random.choice(len(neighbor_uav_data), size=2, replace=False)
        neighbor_uav_data[i], neighbor_uav_data[j] = neighbor_uav_data[j], neighbor_uav_data[i]
        return neighbor_uav_data


    def hill_climbing(self, num_neighbors=1000, max_iterations=1000):
        iteration = 0
        improvement_found = True

        while improvement_found and iteration < max_iterations:
            improvement_found = False
            iteration += 1

            for _ in range(num_neighbors):
                # Seleccionar dos UAVs al azar
                uav1, uav2 = np.random.choice(self.uav_data, 2, replace=False)

                # Intercambiar sus órdenes de aterrizaje
                uav1['orden'], uav2['orden'] = uav2['orden'], uav1['orden']

                # Calcular el nuevo costo total
                new_total_cost = self.calculate_cost(self.uav_data)

                # Si la nueva solución es mejor, actualizar el costo total y marcar la mejora
                if new_total_cost < self.total_cost:
                    self.total_cost = new_total_cost
                    improvement_found = True
                else:
                    # Si la nueva solución no es mejor, revertir el cambio
                    uav1['orden'], uav2['orden'] = uav2['orden'], uav1['orden']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs usando Hill Climbing.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    args = parser.parse_args()

    uav_manager = UAVManager(args.file_path)
    print("Costo total: {}".format(uav_manager.total_cost))
    uav_manager.display_data()
