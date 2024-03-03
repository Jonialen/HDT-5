import random
import simpy
import csv
import os

# random.seed(11)

MAX_PROCESS = 3  # Ajustado para permitir múltiples instrucciones por proceso


class Proceso:
    def __init__(self, name, env, ram, cpu, data, interval):
        self.env = env
        self.name = name
        self.instrucciones = data[0]
        self.ram = ram
        self.cpu = cpu
        self.memoria = data[1]
        self.hora_inicio = None
        self.hora_fin = None
        self.interval = interval

    def run(self):
        print(f"{self.env.now}: [NEW] {self.name}")
        self.to_String()
        # Solicita memoria
        ram = self.get_ram()
        # espera por memoria
        yield ram
        print(f"{self.env.now}: [READY] {self.name}")
        while self.instrucciones > 0:
            # solicita cpu
            with self.cpu.request() as cpu:
                yield cpu
                if self.hora_inicio is None:
                    self.hora_inicio = self.env.now
                # ejecuta sus instrucciones
                print(f"{self.env.now}: [RUNNING] {self.name}")
                for _ in range(MAX_PROCESS):
                    self.instrucciones -= 1
                    if self.instrucciones == 0:
                        break
                if self.instrucciones > 0:
                    if random.randint(1, 2) == 1:
                        print(f"{self.env.now}: [WAITING] {self.name}")
                        yield self.env.timeout(random.expovariate(1.0 / self.interval))
                    elif random.randint(1, 2) == 2:
                        print(f"{self.env.now}: [READY] {self.name}")
        self.put_ram()
        self.hora_fin = self.env.now
        print(f"{self.env.now}: [TERMINATED] {self.name}")

    def get_ram(self):
        return self.ram.get(self.memoria)

    def put_ram(self):
        self.ram.put(self.memoria)

    def to_String(self):
        print("Name", self.name)
        print("Instrucciones", self.instrucciones)
        print("RAM", self.memoria)


class Driver:
    def __init__(self, MAX_RAM, MAX_CPU, INTERVAL):
        self.MAX_RAM = MAX_RAM
        self.MAX_CPU = MAX_CPU
        self.INTERVAL = INTERVAL
        self.procesos = (25, 50, 100, 150, 200)
        self.lista_tiempos = []

    def crear_procesos(self, env, ram, cpu, max_num, lista_procesos):
        for i in range(max_num):
            name = f"Proceso({i+1})"
            # ram/processos
            data = [random.randint(1, 10), random.randint(1, 10)]
            new_process = Proceso(name, env, ram, cpu, data, self.INTERVAL)
            lista_procesos.append(new_process)
            env.process(new_process.run())

    def ejecutar(self):
        for num_procesos in self.procesos:
            lista_procesos = []
            env = simpy.Environment()
            ram_total = simpy.Container(
                env, capacity=self.MAX_RAM, init=self.MAX_RAM)
            cpu_total = simpy.Resource(env, capacity=self.MAX_CPU)
            self.crear_procesos(env, ram_total, cpu_total,
                                num_procesos, lista_procesos)
            env.run()
            self.lista_tiempos.append(lista_procesos)

    def exportar_resultados(self, nombre_archivo):
        with open(nombre_archivo, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['Cantidad de Procesos', 'Nombre', 'Hora de Inicio', 'Hora de Fin', 'Tiempo Total'])
            for i, lista_procesos in enumerate(self.lista_tiempos):
                for proceso in lista_procesos:
                    writer.writerow(
                        [self.procesos[i], proceso.name, proceso.hora_inicio, proceso.hora_fin, proceso.hora_fin - proceso.hora_inicio])

        print(
            f"Los datos se han exportado correctamente en '{nombre_archivo}'.")

    def generar_nombre_archivo(self, nombre_base_archivo):
        contador = 0
        nombre_archivo = nombre_base_archivo
        while os.path.exists(nombre_archivo):
            contador += 1
            nombre_archivo = f"{nombre_base_archivo.split('.')[0]}_{contador}.csv"
        return nombre_archivo

    def ejecutar_y_exportar(self, nombre_base_archivo):
        self.ejecutar()
        nombre_archivo = self.generar_nombre_archivo(nombre_base_archivo)
        self.exportar_resultados(nombre_archivo)


if __name__ == "__main__":
    MAX_RAM = 100
    MAX_CPU = 2
    INTERVAL = 1
    nombre_base_archivo = 'tiempos_procesos.csv'

    driver = Driver(MAX_RAM, MAX_CPU, INTERVAL)
    driver.ejecutar_y_exportar(nombre_base_archivo)
