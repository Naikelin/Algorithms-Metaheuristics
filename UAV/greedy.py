import argparse
import matplotlib.pyplot as plt
import time

class UAVManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.uav_data = []
        self.total_cost = 0
        self.read_file()
        self.solve_greedy()

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

    def display_data(self):
        print("Costo total:", self.total_cost)
        sorted_uav_data = sorted(self.uav_data, key=lambda uav: uav['orden'])
        print("Orden de aterrizaje:", [uav['index'] for uav in sorted_uav_data])
        
    def display_initial_solution(self):
        print("Solución inicial:")
        for uav in self.uav_data:
            print(f"UAV {uav['orden']}: Tiempo de aterrizaje asignado: {uav['tiempo_aterrizaje_asignado']}")
        print("Costo total inicial:", self.total_cost)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    args = parser.parse_args()

    start_time = time.time()
    uav_manager = UAVManager(args.file_path)
    end_time = time.time()
    print(f"Tiempo de ejecución completa: {end_time - start_time:.4f} segundos")

    uav_manager.display_data()
    uav_manager.plot_schedule()
