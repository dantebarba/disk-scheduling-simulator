'''
Modulo que contiene todas las clases necesarias para graficar
una salida del simulador. Requiere matplotlib para funcionar
Se puede invocar por consola directamente, utilizando el formato
descripto en el manual de usuario

@author: Barba Dante
'''
import sys
import argparse
import matplotlib.pyplot as mplt
from matplotlib.ticker import FixedLocator
import simulator
import data


class PlottingError(Exception):
    pass


class Plotter():
    ''' Clase necesaria para manipular el graficador
    '''
    fig = mplt
    axis = fig.gca()  # get axes
    axis.xaxis.set_ticks_position('top')
    axis.xaxis.set_label_position('top')
    axis.invert_yaxis()
    fig.minorticks_off()  # necesario para que funcione

    @classmethod
    def auto_plot(cls, argv=sys.argv):
        '''Class method. Used to graph an input from
        console'''
        # TODO: se puede reubicar?
        parser = argparse.ArgumentParser(description='Simularor command line')
        parser.add_argument('Data_Input', metavar='Input_List', type=str,
                            help='set the simulator data input list')
        parser.add_argument('Algorithm', metavar='Algorithm', type=str,
                            help='''set simulator algorithm. Valid options:
                            fcfs,sstf,scan,cscan,look,clook''')
        parser.add_argument('Disk_Size', metavar='Disk_Size', type=int,
                            help='set the simulator data input list')
        parser.add_argument('-o', metavar='Orientation', type=str, default='e',
                            help='set simulator starting orientation')
        parser.add_argument('-p', action='store_true',
                            help='plot simulator data output')
        parser.add_argument('-s', type=str, metavar='output_filename',
                            help='save the simulator data output plot as png image')
        # TODO: deberia pasar toda la informacion del parser a un diccionario
        try:
            sim = simulator.Simulator(parser.parse_args().Disk_Size)
            sim.algorithm(parser.parse_args().Algorithm)
            if data.DataFormat.list_format(parser.parse_args().Data_Input,
                                           parser.parse_args().Disk_Size):
                sim.data_input(parser.parse_args().Data_Input,
                               parser.parse_args().o)
                sim.simulate()
                if parser.parse_args().p or parser.parse_args().s:
                    p = Plotter()
                    try:
                        cls.format_plot(p, sim.data_output(),
                                        sim.get_startpos(),
                                        sim.get_pagefault(),
                                        sim.disk_size)
                    except Exception as err:
                        # TODO: Agregar excepciones a manejar
                        print 'Unable to Plot'
                        sys.stderr.write('Error ' + str(err) +
                                         ' Unable to Plot')
                        sys.exit(1)
                    if parser.parse_args().p:
                        p.show()
                    if parser.parse_args().s:
                        try:
                            cls.save_plot(p, parser.parse_args().s)
                        except IOError as err:
                            sys.stderr.write('Error' + str(err) + 'Invalid input')
                sim.stop()
        except simulator.AlgorithmInputError as err:
            print 'Incorrect command format, -h for help'
            sys.stderr.write('Error ' + str(err) + ' Wrong Algorithm')
            sys.exit(1)
        except simulator.InvalidInput as err:
            # FIXME: Modificar, esta invertido
            print 'Incorrect command format, -h for help'
            sys.stderr.write('Error ' + str(err) + ' Invalid input')
            sys.exit(1)
        except KeyError as Kwarg_err:
            sys.stderr.write('Incorrect keyword argument: ' +
                             str(Kwarg_err))
            sys.exit(1)

    def __init__(self, input_list=[]):
        self.input_list = input_list
        self.fig.xlabel('Posiciones')
        self.axis.grid(True)

    def format_plot(self, data_list, start_pos, pf_count=0,
                    disk_size=512):
        '''returns a plot using the Simulator dataformat.
        Format style is explained
        in the Simulator user manual'''
        #  TODO: quiza sea recomendable que en el eje
        # X esten los accesos.
        _data = data_list[:]  # copiamos la lista para no modificarla
        try:
            index = _data.index(-1)
        except ValueError:
            _data = (list((i, 'red') for i in _data[:pf_count]) +
                     list((i, 'green') for i in _data[pf_count:]))
        else:
            del _data[index]
            _data = (list((i, 'red') for i in _data[:pf_count]) +
                     list((i, 'green') for i in _data[pf_count:index]) +
                     list((i, 'blue') for i in _data[index:index + 1]) +
                     list((i, 'green') for i in _data[index + 1:]))
        if len(_data[0]) > 1:
            # TODO: falta contador, hacer en otra clase
            self.fig.ylabel('Cantidad de movimientos: ' +
                            str(data.DataFormat.calc_difference(*data_list)))
            self.axis.xaxis.set_major_locator(
                FixedLocator([start_pos] +
                             list(i[0] for i in _data)))
            self.axis.yaxis.set_major_locator(
                FixedLocator(range(len([start_pos] + _data))))
            ant = start_pos
            iant = 0
            try:
                #self.fig.plot([ant,_data[1][0]], [iant, iant+1],
                #color=_data[0][1])
                for i in (_data):
                    self.fig.plot([ant, i[0]], [iant, iant + 1], color=i[1])
                    iant += 1
                    ant = i[0]
                #self.add_text(1, len(_data)-1, 'Movimalpsfakls')
            except IndexError:
                raise PlottingError

    def save_plot(self, filename):
        'Saves the current plot as "filename.png"'
        self.fig.savefig(filename, dpi=150)

    def add_text(self, x, y, text=''):
        # TODO: falta ver como implementar
        # el texto de forma correcta
        self.fig.text(x, y, text)

    def show(self):
        self.fig.show()

if __name__ == '__main__':
    Plotter.auto_plot()
