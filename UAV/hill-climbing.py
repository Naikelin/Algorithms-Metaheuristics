import argparse
import random
import matplotlib.pyplot as plt

class UAVManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.uav_data = []
        self.total_cost = 0
        self.read_file()
        self.solve_greedy()

    '''
        Utils
    '''

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
                    'tiempo_aterrizaje_maximo': aterrizaje_info[2],
                    'tiempos_aterrizaje': [],
                    'orden': None 
                }
                current_line += 1
                
                tiempos_aterrizaje = []
                while len(tiempos_aterrizaje) < D:
                    tiempos = list(map(float, lines[current_line].strip().split()))
                    tiempos_aterrizaje.extend(tiempos)
                    current_line += 1
                    
                uav['tiempos_aterrizaje'] = tiempos_aterrizaje
                self.uav_data.append(uav)

    def display_data(self):
        print("Costo total:", self.total_cost)
        sorted_uav_data = sorted(self.uav_data, key=lambda uav: uav['orden'])
        print("Orden de aterrizaje:", [uav['index'] for uav in sorted_uav_data])
        
    def calculate_cost(self, order):
        total_cost = 0
        time = 0
        for i in order:
            uav = self.uav_data[i]
            closest_time = max(uav['tiempo_aterrizaje_menor'], min(uav['tiempo_aterrizaje_maximo'], max(time, uav['tiempo_aterrizaje_ideal'])))
            penalty = abs(closest_time - uav['tiempo_aterrizaje_ideal'])
            total_cost += penalty
            time = closest_time + uav['tiempos_aterrizaje'][i]
        return total_cost


    def plot_schedule(self):
        fig, ax = plt.subplots()

        for uav in self.uav_data:
            y = uav['orden']
            
            # Dibujar puntos en el tiempo minimo, tiempo ideal, tiempo maximo y tiempo de aterrizaje asignado
            ax.plot(uav['tiempo_aterrizaje_menor'], y, marker='o', markersize=6, color='red')
            ax.plot(uav['tiempo_aterrizaje_ideal'], y, marker='o', markersize=6, color='green')
            ax.plot(uav['tiempo_aterrizaje_maximo'], y, marker='o', markersize=6, color='blue')
            ax.plot(uav['tiempo_aterrizaje_asignado'], y, marker='o', markersize=8, color='black')
            
            # Mostrar los valores del tiempo minimo, tiempo ideal, tiempo maximo y tiempo de aterrizaje asignado
            ax.text(uav['tiempo_aterrizaje_menor'], y, f"{uav['tiempo_aterrizaje_menor']:.1f}", ha='right', va='bottom', color='red')
            ax.text(uav['tiempo_aterrizaje_ideal'], y, f"{uav['tiempo_aterrizaje_ideal']:.1f}", ha='right', va='bottom', color='green')
            ax.text(uav['tiempo_aterrizaje_maximo'], y, f"{uav['tiempo_aterrizaje_maximo']:.1f}", ha='left', va='bottom', color='blue')
            ax.text(uav['tiempo_aterrizaje_asignado'], y, f"{uav['tiempo_aterrizaje_asignado']:.1f}", ha='left', va='bottom', color='black')

        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Orden de aterrizaje')
        ax.set_title('Programacion de aterrizaje de UAVs')
        plt.tight_layout()
        plt.show()

    def get_random_neighbor(self, order):
        neighbor = order[:]
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor

    """ 
    Ordenar los UAVs por su tiempo de aterrizaje preferente (tiempo_aterrizaje_ideal) en orden ascendente. De esta manera, nos aseguramos de que los UAVs con tiempos preferentes más cortos sean atendidos primero.
    Para cada UAV, intentar asignar el tiempo de aterrizaje lo más cercano posible al tiempo preferente sin violar los límites de tiempo mínimo y máximo. Al hacer esto, minimizamos las penalizaciones por unidad de tiempo sobre o bajo el tiempo preferente.
    Calcular el costo total sumando las penalizaciones por unidad de tiempo sobre o bajo el tiempo preferente para todos los UAVs.
    """

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

    def is_feasible(self, order):
        time = 0
        for i in order:
            uav = self.uav_data[i]
            closest_time = max(uav['tiempo_aterrizaje_menor'], min(uav['tiempo_aterrizaje_maximo'], max(time, uav['tiempo_aterrizaje_ideal'])))
            if closest_time < uav['tiempo_aterrizaje_menor'] or closest_time > uav['tiempo_aterrizaje_maximo']:
                return False
            time = closest_time + uav['tiempos_aterrizaje'][i]
        return True

    def solve_hill_climbing(self, max_iterations=1000, max_no_improvement=100, max_attempts=10):
        current_order = [uav['orden'] for uav in self.uav_data]
        current_cost = self.total_cost

        best_order = current_order[:]
        best_cost = current_cost

        no_improvement_counter = 0

        for iteration in range(max_iterations):
            if no_improvement_counter >= max_no_improvement:
                break

            # Generar soluciones vecinas factibles
            feasible_neighbor_found = False
            attempts = 0
            while not feasible_neighbor_found and attempts < max_attempts:
                neighbor_order = self.get_random_neighbor(current_order)
                feasible_neighbor_found = self.is_feasible(neighbor_order)
                attempts += 1

            if not feasible_neighbor_found:
                no_improvement_counter += 1
                continue

            neighbor_cost = self.calculate_cost(neighbor_order)

            if neighbor_cost < current_cost:
                current_order = neighbor_order
                current_cost = neighbor_cost
                no_improvement_counter = 0

                if current_cost < best_cost:
                    best_order = current_order[:]
                    best_cost = current_cost
            else:
                no_improvement_counter += 1

        for i, uav in enumerate(self.uav_data):
            uav_index = best_order.index(i)
            uav['orden'] = uav_index

            closest_time = max(uav['tiempo_aterrizaje_menor'],
                            min(uav['tiempo_aterrizaje_maximo'],
                                max(uav['tiempos_aterrizaje'][uav_index], uav['tiempo_aterrizaje_ideal'])))
            uav['tiempo_aterrizaje_asignado'] = closest_time
            uav['penalizacion'] = abs(closest_time - uav['tiempo_aterrizaje_ideal'])

        
        # Actualizar el costo total
        self.total_cost = best_cost

    def run_hill_climbing(self, max_iterations=1000, max_no_improvement=100):
        self.solve_hill_climbing(max_iterations=max_iterations, max_no_improvement=max_no_improvement)
        self.display_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    args = parser.parse_args()

    uav_manager = UAVManager(args.file_path)
    print("Solución Greedy:")
    uav_manager.display_data()
    uav_manager.plot_schedule()

    print("\nSolución Hill Climbing:")
    uav_manager.run_hill_climbing()
    uav_manager.plot_schedule()