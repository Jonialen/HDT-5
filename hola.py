import main
import pandas as pd
import matplotlib.pyplot as plt


class Analysis:
    def __init__(self, driver):
        self.driver = driver

    def analizar_tiempos(self):
        data = pd.DataFrame(columns=['Cantidad de Procesos', 'Tiempo Total'])

        for lista_procesos in self.driver.lista_tiempos:
            for proceso in lista_procesos:
                data = pd.concat([data, pd.DataFrame({'Cantidad de Procesos': [len(lista_procesos)], 'Tiempo Total': [
                                 proceso.hora_fin - proceso.hora_inicio]})], ignore_index=True)

        media_por_cantidad = data.groupby('Cantidad de Procesos')[
            'Tiempo Total'].mean()
        desviacion_por_cantidad = data.groupby('Cantidad de Procesos')[
            'Tiempo Total'].std()

        print("\nMedia de Tiempos por Cantidad de Procesos:")
        print(media_por_cantidad)
        print("\nDesviación Estándar de Tiempos por Cantidad de Procesos:")
        print(desviacion_por_cantidad)

        media_por_cantidad.plot(
            kind='bar', yerr=desviacion_por_cantidad, capsize=5)
        plt.xlabel('Cantidad de Procesos')
        plt.ylabel('Tiempo Promedio')
        plt.title('Media y Desviación Estándar de Tiempos por Cantidad de Procesos')
        plt.show()


if __name__ == "__main__":
    MAX_RAM = 100
    MAX_CPU = 1
    INTERVAL = 10
    nombre_base_archivo = 'tiempos_procesos.csv'

    driver = main.Driver(MAX_RAM, MAX_CPU, INTERVAL)
    driver.ejecutar()
    driver.exportar_resultados(nombre_base_archivo)

    analysis = Analysis(driver)
    analysis.analizar_tiempos()
