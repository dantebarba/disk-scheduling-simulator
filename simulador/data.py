'''
Created on 13/06/2013

@author: DANTE
'''
''' Clases estaticas con metodos de clase utilizadas
para adecuar datos a un formato especifico. La clase
DataFormat contiene metodos que validan el formato
de un dato. la clase Options contiene todo lo referido
a la carga de las opciones del programa.
La clase Lang tiene todo lo referido al manejo del lenguaje
de la interfaz.

@author BarbaDante
'''
import sys


class DataFormat:
    'Data format class, contains data validation class methods'
    @classmethod
    def list_format(cls, data_list, limit):
        '''Evaluates a "data_list". Returns True if it fits with
        the simulator data format'''
        if data_list:
            eval_list = data_list.split(',')
            for item in eval_list:
                if not(item.isdigit()):
                    if not(item.startswith('pf')):
                        return False
                        break
                    elif not(item[2:].isdigit()) or (
                         (int(item[2:]) > limit) or (int(item[2:]) < 0)):
                        return False
                        break
                elif int(item) > limit or int(item) < 0:
                    return False
            return True
        else:
            return False

    @classmethod
    def relative_position(cls, coorX, coorY, rel1, rel2):
        'Calculates percent of coordinates'
        return coorX * rel1, coorY * rel2

    @classmethod
    def calc_difference(cls, *args):
        'returns a sumatory of the difference on list items'
        ant = args[0]
        acum = 0
        for i in args:
            acum += abs((ant - i))
            ant = i
        return acum


class Config:
    options = {'disk_size': 512, 'display_size': (640, 480),
               'speed': 1, 'plotter': 1, 'lang': 'eng', 'ratio': 0.85,
               'separator': 2}
    version = '1.01'
    sys.stderr = open('error_log.txt', 'w')

    @classmethod
    def  load_config(cls):
        # TODO: No hay una forma de saber si un modulo existe o no?
        ok = True
        OPTIONS = Config.options
        #  importamos las opciones predet
        try:
            config = open('config.ini', 'r')
        except IOError as err:
            ok = False
            sys.stderr.write('Configuration file not found: ' + str(err))
            print 'Creating new default configuration file'
        else:
            cont = 0
            # leemos archivo de configuracion
            for line in config:
                cont += 1  # contador auxiliar
                # cantidad de lineas de config debe ser igual a las opciones
                # de config por defecto, sino hay un error de formato
                for i in OPTIONS.keys():
                    if line.startswith(i):  # buscamos la clave k
                        #para la opcion k
                        try:
                            option = line.split(':')
                            try:
                                Config.options[option[0]] = eval(option[1][:-1])
                                # pasamos el valor leido a la config actual
                                #  TODO: Es mejor usar string para todo no?
                            except NameError:
                                Config.options[option[0]] = (option[1][:-1])
                        except KeyError as err:
                            print 'Error: Unable to load ' + i, err
                            ok = False
            if cont != len(OPTIONS.keys()):
                ok = False
            config.close()
        if not(ok):
            # cargamos las opciones default
            f = open('config.ini', 'w')
            for i in OPTIONS.keys():
                f.write(i + ':' + str(OPTIONS[i]) + '\n')
            f.close()
        try:
            import matplotlib
            OPTIONS['plotter'] = 1
        except ImportError:
            OPTIONS['plotter'] = 0


class Lang:
    active_lang = ''

    @classmethod
    def load_lang(cls):
        div = '#'
        try:
            f = open('lang/' + Config.options['lang'] + '.lang', 'r')
            if Config.options['lang'] == 'eng':
                eng_dict = dict((line.split(div)[0],
                                 line.split(div)[1][:-1]) for line in f)
                lang = {'eng': eng_dict}
            else:
                esp_dict = dict((line.split(div)[0],
                                 line.split(div)[1][:-1]) for line in f)
                lang = {'esp': esp_dict}
            active_lang = lang[Config.options['lang']]
            f.close()
        except (IOError, EOFError) as err:
            sys.stderr.write('Error while loading language pack: ' + str(err))
            print 'Language pack not found'
            sys.exit(1)
        else:
            return active_lang
