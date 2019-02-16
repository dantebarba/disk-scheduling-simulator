'''
Este modulo contiene las clases necesarias para el funcio
namiento del simulador. El uso de la clase Simulator esta
especificado en el manual de usuario. El simulador procesa
una entrada, aplicandole uno de los algoritmos, y retornando
una lista con un formato predefinido. El formato esta espe
cificado en el manual de usuario

@author: Barba Dante
'''
from copy import copy
import cPickle as cp


class AlgorithmInputError(Exception):
    def __str__(self):
        return 'Algorithm Input Error : Could not set algorithm.'


class SimulatorActiveError(Exception):
    def __str__(self):
        return 'Simulator Active Error : Unable to access'


class SimulatorLoadingError(Exception):
    def __str__(self):
        return 'Simulator Loading Error : Unable to load data'


class InvalidInput(Exception):
    def __str__(self):
        return 'Invalid Input'


class SimulatorLoadedError(Exception):
    pass


class Algorithms():
    # TODO: quiza el contador deba ir dentro de esta clase?
    @classmethod
    def FCFS_algo(cls, input_list, pagefault_list=[],
                  start_pos=0, limit=512, direction=None):
        '''given a req list and a start position,
         this method will return a new processed list using FCFS algorithm'''
        _input_list = pagefault_list + input_list
        return _input_list

    @classmethod
    def SSTF_algo(cls, input_list, pagefault_list=[],
                  start_pos=0, limit=512, direction=None):
        '''given a req list and a start position,
         this method will return a new processed list using SSTF algorithm'''
        def _recu_run(val, l, result, length):
            if length == 0:
                return result
            else:
                index = l.index(val)
                slice1 = l[:index]
                slice2 = l[-1:index:-1]
                del l[index]
                if slice1 and slice2:
                    if abs(slice1[-1] - val) < abs(slice2[-1] - val):
                        result.append(slice1[-1])
                        return _recu_run(slice1[-1], l, result, length - 1)
                    else:
                        result.append(slice2[-1])
                        return _recu_run(slice2[-1], l, result, length - 1)
                elif slice1:
                    result.append(slice1[-1])
                    return _recu_run(slice1[-1], l, result, length - 1)
                elif slice2:
                    result.append(slice2[-1])
                    return _recu_run(slice2[-1], l, result, length - 1)
                else:
                    return _recu_run(val, l, result, length - 1)
        if pagefault_list:
                start_pos = pagefault_list[-1]
        _input = input_list[:]
        _input.insert(0, start_pos)
        _input.sort()
        return pagefault_list + _recu_run(start_pos, _input, [], len(_input))

    @classmethod
    def SCAN_algo(cls, input_list, pagefault_list=[], start_pos=0,
                  limit=512, direction='e'):
        '''given a req list a start position and a disk size limit,
        this method will return a new processed list using SCAN algorithm'''
        _input_list = copy(input_list)
        if pagefault_list:
            # if hay PF
            if len(pagefault_list) == 1:
                # si es de un elemento, start_pos es nuestro anterior
                if pagefault_list[-1] > start_pos:
                    # si es mayor al anterior, la direccion sera 'Este'
                    direction = 'e'
                else:
                    direction = 'w'
            else:
                if pagefault_list[-1] > pagefault_list[-2]:
                # comprar el PF con el PF anterior
                    direction = 'e'
                else:
                    direction = 'w'
            start_pos = pagefault_list[-1]
        _input_list.append(start_pos)
        _input_list.sort()
        index = _input_list.index(start_pos)
        del _input_list[index]
        slice1 = _input_list[:index]
        slice2 = _input_list[index:]
        if direction == 'w':
            # TODO: si no hay elementos en el lado
            # se continua escanenado igual?
            if slice2:
                slice1.insert(0, 0)
        if direction == 'e':
            if slice1:
                slice2.append(limit - 1)
        slice1.reverse()
        if direction == 'e':
            return pagefault_list + slice2 + slice1
        else:
            return pagefault_list + slice1 + slice2

    @classmethod
    def CSCAN_algo(cls, input_list, pagefault_list=[],
                   start_pos=0, limit=512, direction='e'):
        '''given a req list and a start position,
        this method will return a new processed list using C-SCAN algorithm'''
        #  TODO: Agregar descripciones detalladas
        _input_list = copy(input_list)
        dummy = [-1]
        if pagefault_list:
            start_pos = pagefault_list[-1]
        _input_list.append(start_pos)
        _input_list.sort()
        index = _input_list.index(start_pos)
        del _input_list[index]
        slice2 = _input_list[index:]  # upper (e)
        slice1 = _input_list[:index]  # lower (w)
        if slice2 and direction == 'w':
            slice2.append(limit - 1)
            slice1.insert(0, 0)
        if slice1 and direction == 'e':
            slice1.insert(0, 0)
            slice2.append(limit - 1)
        # no cambia el sentido
        if direction == 'w':
            slice1.reverse()
            slice2.reverse()
            if slice2:
                return pagefault_list + slice1 + dummy + slice2
            else:
                return pagefault_list + slice1
        else:
            if slice1:
                return pagefault_list + slice2 + dummy + slice1
            else:
                return pagefault_list + slice2

    @classmethod
    def LOOK_algo(cls, input_list, pagefault_list=[],
                  start_pos=0, limit=512, direction='e'):
        '''given a req list and a start position,
         this method will return a new processed list using LOOK algorithm'''
        _input_list = copy(input_list)
        if pagefault_list:
            #  TODO: revisar que pasa con el Start_pos en el caso len(1)
            if len(pagefault_list) == 1:
                # si es de un elemento, start_pos es nuestro anterior
                if pagefault_list[-1] > start_pos:
                    # si es mayor al anterior, la direccion sera 'Este'
                    direction = 'e'
                else:
                    direction = 'w'
            else:
                if pagefault_list[-1] > pagefault_list[-2]:
                # comprar el PF ultimo con el PF anterior
                    direction = 'e'
                else:
                    direction = 'w'
            # actualizo start_pos en el ultimo PageFault atendido
            start_pos = pagefault_list[-1]
        _input_list.append(start_pos)
        _input_list.sort()
        index = _input_list.index(start_pos)
        del _input_list[index]
        slice1 = _input_list[:index]
        slice2 = _input_list[index:]
        slice1.reverse()
        if direction == 'e':
            return pagefault_list + slice2 + slice1
        else:
            return pagefault_list + slice1 + slice2

    @classmethod
    def CLOOK_algo(cls, input_list,
                   pagefault_list=[], start_pos=0, limit=512, direction='e'):
        '''given a req list and a start position,
        this method will return a new processed list using C-LOOK algorithm'''
        _input_list = copy(input_list)
        dummy = [-1]
        if pagefault_list:
            start_pos = pagefault_list[-1]
        _input_list.append(start_pos)
        _input_list.sort()
        index = _input_list.index(start_pos)
        del _input_list[index]
        slice2 = _input_list[index:]
        # upper (e)
        slice1 = _input_list[:index]
        # lower (w)
        # no cambia el sentido luego de atender PF
        if direction == 'w':
            slice1.reverse()
            slice2.reverse()
            if slice2:
                return pagefault_list + slice1 + dummy + slice2
            else:
                return pagefault_list + slice1
        else:
            if slice1:
                return pagefault_list + slice2 + dummy + slice1
            else:
                return pagefault_list + slice2


class Simulator():
    _ALGO_KEY = {'fcfs': Algorithms.FCFS_algo, 'sstf': Algorithms.SSTF_algo,
                'scan': Algorithms.SCAN_algo, 'cscan': Algorithms.CSCAN_algo,
                'look': Algorithms.LOOK_algo, 'clook': Algorithms.CLOOK_algo}

    def __init__(self, disk_size):
        if isinstance(disk_size, int):
            self.disk_size = disk_size
        else:
            raise InvalidInput
        self._active = False
        self.algo = 'fcfs'
        self._pf_list = []
        self._req_list = []
        self._loaded = False
        self._start_pos = 0
        self._orientation = 'e'

    def simulate(self):
        if not(self._active) and self._loaded:
            try:
                # el diccionario devuelve la funcion,
                # dados los parametros se ejecuta
                self._output = self._ALGO_KEY[self.algo.lower()](
                                                  self._req_list,
                                                  self._pf_list,
                                                  self._start_pos,
                                                  self.disk_size,
                                                  self._orientation)
            except KeyError:
                raise SimulatorLoadingError
            else:
                self._active = True
        elif self._active:
            raise SimulatorActiveError
        else:
            raise SimulatorLoadedError

    def stop(self):
        self._active = False

    def get_disksize(self):
        return self.disk_size

    def is_active(self):
        return self._active

    def is_loaded(self):
        return self._loaded

    def reset(self):
        if not(self._active):
            return Simulator(self.disk_size)
        else:
            raise SimulatorActiveError

    @classmethod
    def _multi_delete(cls, list_, args):
        'multi-delete, delets n elements from list, runs on nlog(n)'
        indexes = sorted(args, reverse=True)
        for index in indexes:
            del list_[index]
        return list_

    def _get_pf(self, req_list):
        'get the pagefault list from the main req list, req_list is modified'
        l = []
        delete = []
        for i in range(len(req_list)):
            if req_list[i].startswith('pf'):
                l.append(req_list[i][2:])
                delete.append(i)
        self._multi_delete(req_list, delete)
        return l

    @classmethod
    def checklist(cls, l, limit):
        'checks if a requirement list is within range'
        for i in l:
            if i > limit or i < 0:
                return False
                break
        else:
            return True

    def data_input(self, req_list, orientation='e'):
        # TODO: data_input deberia adaptar todo el formato, el split deberia
        # ser hecho aca no afuera de esta funcion
        # deberia entrar un string y sin start_pos
        _req_list = req_list[:]
        _req_list = _req_list.split(',')
        start_pos = _req_list.pop(0)
        if start_pos.isdigit():
            start_pos = int(start_pos)
        else:
            raise InvalidInput
        if not(self._active):
            # validacion 1: posicion inicial
            if start_pos >= 0 and start_pos < self.disk_size and (
                (orientation.lower() == 'e' or orientation.lower() == 'w')):
                try:
                    # validacion 2: posiciones procesadas
                    # se genera un backup
                    _bup_pf_list = self._pf_list[:]
                    self._pf_list = map(int, self._get_pf(_req_list))
                    _bup_req_list = self._req_list[:]
                    self._req_list = map(int, _req_list)
                    if not(Simulator.checklist(self._pf_list + self._req_list,
                                               self.disk_size)):
                        # se actualizan las listas con el backup
                        self._pf_list = _bup_req_list
                        self._req_list = _bup_req_list
                        raise InvalidInput
                except TypeError:
                    raise
                self._start_pos = start_pos
                self._orientation = orientation
                self._loaded = True
            else:
                raise InvalidInput
        else:
            raise SimulatorActiveError

    def data_output(self):
        'returns the simulator output list if simulator is loaded and active'
        if self._active and self._loaded:
            self.__output = self._output[:]
            return self.__output
        elif not(self._active):
            raise SimulatorActiveError
        else:
            raise SimulatorLoadedError

    def algorithm(self, algo):
        'change algorithm'
        if not(self._active):
            if algo.lower() in self._ALGO_KEY.keys():
                self.algo = algo
            else:
                raise AlgorithmInputError
        else:
            raise SimulatorActiveError

    def save_environment(self, filename):
        'Saves the simulator environment (all instance atributes)'
        if not(self._active):
            try:
                f = open(filename, 'w')
                cp.dump(self, f)
                # pickle dump
                f.close()
            except IOError:
                raise
        else:
            raise SimulatorActiveError

    def load_environment(self, filename):
        'Loads an environment from file (all instance atributes)'
        if not(self._active):
            try:
                _bup = self
                # GENERO UN BACKUP POR SI HAY ERROR
                f = open(filename, 'r')
                self = cp.load(f)
                f.close()
                return self
            except EOFError:
                # CPICKLE ERROR
                self = _bup
                raise SimulatorLoadingError(EOFError)
            except IOError:
                raise SimulatorLoadingError(IOError)
        else:
            raise SimulatorActiveError

    def get_pagefault(self):
        return len(self._pf_list)

    def get_startpos(self):
        return self._start_pos

# TODO: Pasar esto a un unitest
# sim = Simulator(512)
#
# sim.algorithm('look')
#
# sim.data_input(['30','40','150'], '20', 'w')
#
# sim.simulate()
#
# print sim.data_output()
