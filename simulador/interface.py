'''
    Este modulo se encarga de administrar toda la interfaz
    de usuario del programa. Utiliza dos clases base que se
    encargan de administrar la entrada y salida de datos.
    Ambas se conectan con el simulador para poder procesar
    los datos recibidos y emitidos.

    @author Barba Dante
'''
try:
    # SYSTEM IMPORTS
    import sys
    import os
    # BASE LIBRARY IMPORTS
    import math
    # PYGAME IMPORTS
    import pygame as pg
    from pygame.locals import *
    # GUI IMPORTS
    from Tkinter import *
    import tkFileDialog
    import tkMessageBox
    import ttk
    # PROYECT IMPORTS
    import simulator
    import data
except ImportError as err:
    print 'Dependencies are missing'
    sys.stderr.write('Missing Dependencies: ' + str(err))
    sys.exit(1)
# OPTIONAL
try:
    import plotter
except ImportError as perr:
    print 'Could not load plotter'
    sys.stderr.write(str(perr))
try:
    # para uso futuro
    import datetime
except ImportError:
    pass


class PyGameHandler():
    ''' Clase que controla todos los componentes
    de PyGame necesarios para mostrar el grafico
    en pantalla y poder utilizarlo
    Consta de 3 superficies, una primaria
    y dos secundarias (las cuales se acoplan a
    la primaria). Una de las superficies
    secundarias representa el fondo estatico
    que se genera una unica vez mediante el metodo
    'generate_figure'. La segunda representa
    la parte activa (contador y conexiones de
    sectores). El grafico del disco estatico
    se escala automaticamente a la pantalla
    segun el valor del "ratio".'''
    _BACKGROUND_COLOR = 255, 255, 255
    COLOR_KEY = {'white': (255, 255, 255), 'black': (0, 0, 0),
                 'null': (255, 0, 255), 'blue': (0, 0, 255),
                 'green': (0, 255, 0), 'red': (255, 0, 0)}
    NULL_COLOR = 255, 0, 255  # valor del color transparente
    _dot_map = {}  # mapa de puntos (x,y) para cada sector
    counter = 0  # Contador de accesos

    def __init__(self, display_size=(640, 480), figure_size=512):
        self.init()
        # Config Loading
        self.w = display_size[0]
        self.h = display_size[1]
        self.separator = data.Config.options['separator']
        self.screen_rate = data.Config.options['ratio']
        # Main display
        self._display = pg.display.set_mode(display_size)
        self._display.fill(pg.Color(255, 255, 255))
        # Static Display
        self._background = pg.Surface((self.w, self.h))
        self._background.fill(self.COLOR_KEY['white'])
        # Active Display
        self._active_surface = pg.Surface((self.w, self.h))
        self._active_surface.set_colorkey(self.COLOR_KEY['null'])
        self._active_surface.fill(self.COLOR_KEY['null'])
        self.display_size = display_size[:]
        font = self.font = pg.font.Font(None, 16)
        counter_text = font.render(data.Lang.active_lang['pygamehandler_movement'],
                                   1, (0, 0, 0))
        self._background.blit(counter_text, (self.w * 0.01, self.h * 0.03))
        self.figure_start = (self.w / 2), (self.h / 2)
        self.figure_size = figure_size
        # se genera el mapa de puntos
        self._dot_map = self.generate_figure(self.figure_size,
                                            self.figure_start)

    def generate_figure(self, figure_size, figure_start):
        'Generates a disk figure if allowed, returns a Sector : (x,y) dictionary'
        def figure_dimension(size):
            ''' given a figure_size, this module will return the best divisor match'''
#             El modulo permite dividir la figura en partes acordes para optimizar
#             la calidad grafica de la figura. Se busca que la cantidad de divisiones
#             por pista sea de una a cuatro veces mayor que la cantidad de pistas.
#             Si el modulo no encuentra un valor optimo, no se podra generar la figura
            # TODO: buscando divisores, se que hay metodos mejores :)
            divisor = []
            for div in range(1, size + 1):
                # evitamos el 0
                if size % div == 0:
                    divisor.append(div)
            for i in divisor:
                # evitamos el 1
                if (i * 2 in divisor) and ((i ** 2) * 2 == size):
                    return i
                    break
                elif (i * 3 in divisor) and ((i ** 2) * 3 == size):
                    return i
                    break
                elif (i * i == size):
                    return i
                    break
                elif (i * 4 in divisor and (i ** 2) * 4 == size):
                    return i
                    break
            else:
                return None

        def scale_circle(qty, screen_w=self.w, screen_h=self.h,
                         p=self.screen_rate):
            'Scaling the image radius to fit on the screen'
            # p = ajuste de la proporcion de pantalla usada, recomendado < 90%
            margin = (int((screen_w * p) - (screen_w / 2)),
                      int((screen_h * p) - (screen_h / 2)))
            # se establecen los margenes de la pantalla
            return (int(margin[0] / qty),
                    int(margin[1] / qty))
            # devuelve la relacion entre el margen y la cantidad a representar (espacio)

        def convert_rad(deg):
            'Given a degree, returns it as radians'
            radians = math.pi * deg / 180
            return radians

        def map_figure(track_qty, sector_qty, figure_start, r,
                       start_circle=0):
            '''Maps a disk figure, sector_qty must be a multiple of track_qty, 
            start_circle is the center circle separator'''
            # generamos la figura del disco
            # el parametro r es el radio del circulo
            # el paramentro start_circle es el circulo ubicando en el centro 
            # que funciona de separador, sin este circulo no podremos graficar
            # correctamente, ya que no tendremos espacio para unir los sectores
            # mas internos del disco. Es recomendable que el circulo interno sea
            # del tamanio del radio como minimo
            division = round(sector_qty / track_qty)  # cantidad de divisiones
            # de la circunferencia, debe ser entero
            pg.draw.circle(self._background, self.COLOR_KEY['black'],
                           figure_start, start_circle, 2)  # dibuja el primer 
            # circulo de espacio
            for i in range(track_qty):
                # Dibujando n circulos
                pg.draw.circle(self._background, self.COLOR_KEY['black'],
                               figure_start,
                               r * (i + 1) + start_circle, 2)  # dibuja el resto de los circulos
            a_step = (360 / division)  # salto en grados de cada zona
            acum = 0  # acumulador de grados
            while acum <= 360:
                start = ((self.w / 2) + start_circle *
                         math.sin(convert_rad(acum)),  # puntos de partida de la linea a trazar
                         (self.h / 2) + start_circle *
                         math.cos(convert_rad(acum)))
                end = ((self.w / 2) + (r * track_qty + start_circle) *
                       math.sin(convert_rad(acum)),  # puntos de llegada de la linea a trazar
                       (self.h / 2) + (r * track_qty + start_circle) *
                       math.cos(convert_rad(acum)))
                pg.draw.line(self._background, self.COLOR_KEY['black'],
                             start, end)  # trazado
                acum += a_step  # se aumenta el acumulador en un salto de grado
            self._display.blit(self._background, (0, 0))

        def generate_dot_map(track_qty, sector_qty, figure_start,
                             r, start_circle=0):
            'Returns a dictionary containing sector : (x,y)'
#           Este modulo nos permite generar un mapa de puntos (x,y) para cada sector
#           del circulo. Gracias a este mapa de puntos podemos luego unir sectores con
#           facilidad
            div = round(sector_qty / track_qty)
            # cantidad divisiones por pista
            a_step = (360 / div)
            # grados por cada division
            map_dictionary = {}
            # dict a devolver
            acum = 0
            # acumulador simple
            i = 0
            # contador de sectores por pista
            while acum < 360:
                acum += a_step
                for j in range(track_qty):
                    radio1 = start_circle + r * j
                    # radio anterior
                    radio2 = start_circle + r * (j + 1)
                    # radio siguiente
                    avrg_x = (((radio1 + radio2) / 2) *
                        math.sin(convert_rad((acum + (acum - a_step)) / 2)))
                    # promedio en (x,y) entre
                    # el radio anterior y el siguiente
                    avrg_y = (((radio1 + radio2) / 2) *
                              math.cos(convert_rad(
                              (acum + (acum - a_step)) / 2)))
                    map_dictionary[i + div * j] = ((self.w / 2) + avrg_x,
                                                   (self.h / 2) + avrg_y)
                    # se agrega el elemento al diccionario sector : (x,y)
                i += 1
            return map_dictionary
        division_qty = figure_dimension(self.figure_size)
        margin = scale_circle(division_qty + self.separator,
                              self.w, self.h)
        # se genera un margen ( se escala el circulo a la pantalla)
        if margin[1] > margin[0]:
            # se busca cual de los dos
            # ejes tiene peor margen
            # (mas grande)
            r = margin[1]
        else:
            r = margin[0]
        map_figure(division_qty, figure_size,
                   figure_start, r, r * self.separator)
        # se mapea la figura
        return generate_dot_map(division_qty,
                                figure_size, figure_start,
                                r, r * self.separator)
        # se genera el mapa de puntos

    def display(self):
        'Display pygame figure'
        pg.display.update()

    def graphic_play(self, data_list, start_pos, pf_count, speed):
        'start graphic animation'
        def _progressive_connect(self, sector_start, sector_end, color, 
                                time=10):
            '''connects all sectors between sector_start and sector_end
            in secuential order'''
            # TODO: mejorar
            if sector_start > sector_end:
                sectors = range(sector_end, sector_start)
                sectors.reverse()
            else:
                sectors = range(sector_start, sector_end)
            for i in sectors:
                self.connect_sector(i, i + 1, color)
                self.display()
                pg.time.delay(time)

        def _timmer(self, speed, time=1000):
            'timmer implementation'
            # revision de velocidad, si speed es falso
            # se utiliza paso a paso
            # TODO: todavia no implementado correctamente
            if not(speed):
                pass
            else:
                pg.time.delay(int(time))
#        El modulo permite graficar sobre el disco.
#        La velocidad puede variar entre 2x y paso a paso
#        El valor 0 corresponde a 'paso a paso'
        self.reset()
        self.display()
        TIME_RATE = 1000
        # speed toma valores decimales
        # TIME_RATE es dividido por speed 
        # para saber cuanto sera el tiempo
        # de espera
        try:
            time = TIME_RATE / speed
        except ZeroDivisionError:
            time = 0
        _data = data_list[:]
        # Lista de pares (valor, color)
        # Se recorre la lista y se colorea 
        # segun el color indicado para cada valor
        try:
            # se busca si existe un salto dummy (no se cuenta)
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
        ant = start_pos
        x = int(round(self._dot_map[start_pos][0]))
        y = int(round(self._dot_map[start_pos][1]))
        # circulo que identifica el punto de inicio en la pantalla
        pg.draw.circle(self._active_surface, self.COLOR_KEY['blue'],
                       (x, y), 3)
        self._display.blit(self._active_surface, (0, 0))
        self.display()
        pg.event.clear()
        # comprobacion step by step
        for i in (_data):
            # TODO: saco el if afuera y copio dos veces
            # o evaluo con el if dentro
            _timmer(self, speed, time)
            if i[1] == 'blue':
                self.connect_sector(ant, i[0], i[1])
                #self.inc_counter(1) capaz no tengamos que usarlo
            else:
                _progressive_connect(self, ant, i[0], i[1])
                self.inc_counter(data.DataFormat.calc_difference(ant, i[0]))
            x = int(round(self._dot_map[i[0]][0]))
            y = int(round(self._dot_map[i[0]][1]))
            # circulo que identifica un sector atendido en la pantalla
            pg.draw.circle(self._active_surface, self.COLOR_KEY['black'],
                    (x, y), 3)
            self._display.blit(self._active_surface, (0, 0))
            self.display()
            ant = i[0]
            pg.event.clear()

    def init(self):
        'initialize pygame'
        pg.display.init()
        pg.font.init()

    def connect_sector(self, sector1, sector2, color='green'):
        '''Draw a line connecting sector1 with sector2. "color"
        defines the color of the line'''
        try:
            color = self.COLOR_KEY[color]
        except KeyError:
            return -1
            #raise
        pg.draw.line(self._active_surface, color,
                       self._dot_map[sector1],
                       self._dot_map[sector2], 2)
        self._display.blit(self._active_surface, (0, 0))

    def clear_connections(self):
        ' clears all sector connections '
        self._active_surface.fill(self.COLOR_KEY['white'])
        self._active_surface.fill(self.NULL_COLOR)

    def reset_counter(self):
        'resets the access counter'
        self.counter = 0

    def reset(self):
        ' reset pygame graphic'
        self.reset_counter()
        self.clear_connections()
        self._display.blit(self._background, (0, 0))

    def inc_counter(self, inc):
        'increases the movement counter on "inc"'
        # se rellena el sector de la pantalla necesario
        #para modificar el contador
        self._active_surface.fill((255, 255, 255),
                           pg.Rect((0, self.h * 0.08),
                                        (self.w * 0.1,
                                         self.h * 0.1)))
        self.counter += inc
        counter_text = self.font.render(str(self.counter), 1, (0, 0, 0))
        self._active_surface.blit(counter_text,
                           (self.w * 0.01,
                            self.h * 0.08))
        self._display.blit(self._active_surface, (0, 0))

    def check_keypress(self, key='s'):
        'check if key was pressed'
        # busqueda de evento
        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == eval('K_' + key):
                    return True
                else:
                    return False

    def exit(self):
        'Exit pygame'
        pg.quit()


class SimulatorInterface():
    ''' Clase que crea y administra
    la interfaz grafica. Utiliza el modulo
    nativo de Python Tkinter+ttk. La clase
    se encarga de toda entrada y salida de datos
    de la interface hacia el simulador y
    el manejador del grafico. '''
    _gui = Tk()  # TK mainframe
    now = datetime.datetime.now()
    current_speed = 1  # velocidad actual
    step_by_step = False  # activacion paso a paso
    _active_file = ''  # archivo de guardado activo
    _graphic = True  # DEFAULT CHECK
    # mapa de velocidades seleccionables
    SPEED = {0: 2, 1: 1, 2: 0.50, 3: 0.25, 4: 0}
    # mapa de algoritmos seleccionables
    ALGO = ('FCFS', 'SSTF', 'SCAN', 'CSCAN', 'LOOK', 'CLOOK')

    def __init__(self, sim=simulator.Simulator(512),  display_size=(640, 480)):
#         def shutdown_ttk_repeat():
#             'Bugfix: Solves the ttk::repeat exception'
#             # "ttk::Repeat"
#             # ("after" script)
#             self._gui.eval('::ttk::CancelRepeat')
        self.sim = sim  # sim init
        self._gui.title('Simulator v' + data.Config.version)
        # self._gui.protocol("WM_DELETE_WINDOW", shutdown_ttk_repeat)
        # ttk bugfix
        self.display_size = display_size 
        w = display_size[0]
        h = display_size[1]
        self._main_frame = Frame(self._gui, width=int(w), height=int(h))  
        ############### MENU START ################
        self._menubar = Menu(self._gui)
        # file pulldown menu
        self._filemenu = Menu(self._menubar, tearoff=0)
        self._filemenu.add_command(label=data.Lang.active_lang['simulatorinterface_open'],
                                   command=self.OpenOp)  # do not use parenthesis on command parameter
        self._filemenu.add_command(label=data.Lang.active_lang['simulatorinterface_save'],
                                   command=lambda: self.SaveOp(self._active_file))
        self._filemenu.add_command(label=data.Lang.active_lang['simulatorinterface_saveas'],
                                   command=self.SaveOp)
        self._filemenu.add_separator()
        self._filemenu.add_command(label=data.Lang.active_lang['simulatorinterface_exit'],
                                   command=self.ExitOp)
        self._menubar.add_cascade(label=data.Lang.active_lang['simulatorinterface_file'], 
                                  menu=self._filemenu)
        # simulator pulldown menu
        self._simumenu = Menu(self._menubar, tearoff=0)
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_simulate'],
                                   command=self.StartOp)
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_stop'], 
                                   command=self.StopOp)
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_reset'],
                                   command=self.ResetOp)
        self._simumenu.add_separator()
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_setalgo'],
                                   command=self.ChangeAlgo_comboBox)
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_speed'], 
                                   command=self.ChangeSpeed_comboBox)
        self._simumenu.add_command(label=data.Lang.active_lang['simulatorinterface_newinput'], 
                                   command=lambda:
                                   self.Input_msg_box(data.Lang.active_lang['simulatorinterface_inputmsg']))
        self._menubar.add_cascade(label=data.Lang.active_lang['simulatorinterface_simulator'], 
                                  menu=self._simumenu)
        # Plotter pulldown menu
        self._plotmenu = Menu(self._menubar, tearoff=0)
        self._plotmenu.add_command(label=data.Lang.active_lang['simulatorinterface_plot'], 
                                   command=self.PlotOp)
        if data.Config.options['plotter'] == 0:
            self._menubar.add_cascade(label=data.Lang.active_lang['simulatorinterface_plotter'],
                                      menu=self._plotmenu, state='disabled')
        else:
            self._menubar.add_cascade(label=data.Lang.active_lang['simulatorinterface_plotter'], 
                                      menu=self._plotmenu)
        # about menu
        self._menubar.add_command(label=data.Lang.active_lang['simulatorinterface_about'],
                                    command=lambda: self.popup_dialog(data.Lang.active_lang['simulatorinterface_about'],
                                    'Creado por BarbaDante dantebarba@gmail.com'))
        self._gui.config(menu=self._menubar)
        ############## MENU END ########################
        self._main_frame.pack()

    def set_handler(self, handler):
        'set pygame handler'
        self.handler = handler

    def popup_dialog(self, name='Dialog', data=''):
        'simple popup dialog'
        top = self.top = Toplevel(self._gui)
        self.top.geometry('200x200+200+200')
        top.title(name)
        text = Text(self.top)
        text.insert(INSERT, data)
        text.pack(side='top')

    def Input_msg_box(self, msg):
        'Input dialog box, returns an input on data_list'
        def _submit_list(self):
            '''list submit process, activated when "submit"
            is clicked'''
            _data = self.entry_field.get()
            orientation = ('e', 'w')[self.box.current()]
            if _data and data.DataFormat.list_format(_data,
                                        data.Config.options['disk_size']):
                try:
                    self.data_list = _data[:]
                    self.sim.data_input(self.data_list, orientation)  # entrada al simulador
                except simulator.SimulatorActiveError:
                    self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])
                    self.top.destroy()
                except IndexError:
                    self._error_dialog(data.Lang.active_lang['error_emptyinput'])
                except simulator.InvalidInput:
                    self._error_dialog(data.Lang.active_lang['error_invalidinput'])
                else:
                    self.top.destroy()
            else:
                self._error_dialog(data.Lang.active_lang['error_invalidinput'])
        top = self.top = Toplevel(self._gui)
        top.geometry('300x200')
        label0 = Label(top, text=msg)
        label0.pack()
        self.entry_field = Entry(top, width=100)
        self.entry_field.pack()
        Label(self.top, text=data.Lang.active_lang['orientation']).pack()
        self.box = ttk.Combobox(self.top, state='readonly', width=50)
        self.box['values'] = ('e', 'w')  # e = Este w = Oeste
        self.box.pack()
        submit_button = Button(top, text=data.Lang.active_lang['submit'],
                               command=lambda: _submit_list(self))
        submit_button.pack()
        Button(top, text=data.Lang.active_lang['cancel'],
               command=lambda: self.top.destroy()).pack()

    def ChangeSpeed_comboBox(self):
        'ComboBox Speed selector Frame'

        def _get_comboBox_selection(self, Frame):
            '''Gets selection of combo Box (speed KEY),
            and then destroys the TopLevel Frame'''
            self.current_speed = self.box.current()
            Frame.destroy()
        top = self.top = Toplevel(self._gui)
        label = Label(
        top, text=data.Lang.active_lang['simulatorinterface_changespeed'])
        label.pack()
        box_value = StringVar(self.top)  # linux fix
        self.box = ttk.Combobox(top, textvariable=box_value,
                                state='readonly')
        #if 'linux' in sys.platform:
        self.box['values'] = ('2x', '1x', '1/2x', '1/4x')
            # FIXME: step by step disabled en linux, no anda
            # FIXME: step by step inestable en Windows
#         else:
#             self.box['values'] = ('2x', '1x', '1/2x', '1/4x',
#                               data.Lang.active_lang['stepbystep'])
        self.box.current(self.current_speed)
        self.box.grid(column=0, row=0)
        self.box.pack()
        Button(top, text=data.Lang.active_lang['submit'],
               command=lambda: _get_comboBox_selection(self, top)).pack()

    def ChangeAlgo_comboBox(self):
        'ComboBox Change Algorithm'

        def _get_comboBox_selection(self):
            '''Gets selection of combo Box (algorithm),
            and then destroys the TopLevel Frame'''
            try:
                self.sim.algorithm(self.ALGO[self.box.current()])
            except simulator.SimulatorActiveError:
                self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])
            self.top.destroy()
        # toplevel frame
        top = self.top = Toplevel(self._gui)
        label = Label(top, text=data.Lang.active_lang['simulatorinterface_changealgo'])
        label.pack()
        box_value = StringVar(self.top)
        self.box = ttk.Combobox(top, textvariable=box_value,
                                state='readonly')
        #  seteo de la lista de valores
        self.box['values'] = ('FCFS', 'SSTF', 'SCAN', 'CSCAN', 'LOOK', 'CLOOK')
        self.box.current(0)
        #  ubicacion de la lista
        self.box.grid(column=0, row=0)
        self.box.pack()
        Button(top, text=data.Lang.active_lang['submit'],
               command=lambda: _get_comboBox_selection(self)).pack()

    def _error_dialog(self, msg='Error'):
        'Simple error message popup'
        tkMessageBox.showerror('Error', msg)

    def OpenOp(self):
        'Open Environment'
        try:
            env_file = tkFileDialog.askopenfilename(
                filetypes=[('Environment Data', '*.dat')],
                title=data.Lang.active_lang['simulatorinterface_openop_openenv'])
            if env_file:
                # hay un archivo para abrir
                self.sim = self.sim.load_environment(env_file)
                self._active_file = env_file
        except simulator.SimulatorActiveError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])
        except simulator.SimulatorLoadingError:
            self._error_dialog(data.Lang.active_lang['error_simulatorloading'])
            raise
        except:
            self._error_dialog(data.Lang.active_lang['error_unexpected'])
            raise

    def SaveOp(self, saveAs=False):
        'Save Environment'
        try:
            if not(saveAs):
                self._active_file = tkFileDialog.asksaveasfilename(
                                    filetypes=[('Simulator Data File', '*.dat')],
                                    title=data.Lang.active_lang['simulatorinterface_saveop'],
                                    defaultextension='.dat')
            if self._active_file:
                self.sim.save_environment(self._active_file)
        except simulator.SimulatorActiveError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])
        except IOError as err:
            self._error_dialog(data.Lang.active_lang['error_ioerror'] + str(err))
            raise

    def ExitOp(self):
        'System shutdown'
        ask_save = tkMessageBox.askyesno(data.Lang.active_lang['exit'],
                                         data.Lang.active_lang
                                         ['simulatorinterface_exitop_askexit'])
        if ask_save:
            self.SaveOp(self._active_file)
        self.handler.exit()
        self._gui.destroy()

    def _toggle(self):
        "disables/enables the menu bar items"
        #  TODO:  Es posible mejorarlo?
        if self._filemenu.entrycget(0, "state") == "normal":
            for i in range(1):
                self._plotmenu.entryconfig(i, state='disabled')
                self._simumenu.entryconfig(i, state='disabled')
                self._filemenu.entryconfig(i, state='disabled')
            for i in range(1, 3):
                self._filemenu.entryconfig(i, state='disabled')
                self._simumenu.entryconfig(i, state='disabled')
            for i in range(4, 5):
                self._filemenu.entryconfig(i, state='disabled')
                self._simumenu.entryconfig(i, state='disabled')
            for i in range(5, 7):
                self._simumenu.entryconfig(i, state='disabled')
        else:
            for i in range(1):
                self._plotmenu.entryconfig(i, state='normal')
                self._simumenu.entryconfig(i, state='normal')
                self._filemenu.entryconfig(i, state='normal')
            for i in range(1, 3):
                self._filemenu.entryconfig(i, state='normal')
                self._simumenu.entryconfig(i, state='normal')
            for i in range(4, 5):
                self._filemenu.entryconfig(i, state='normal')
                self._simumenu.entryconfig(i, state='normal')
            for i in range(5, 7):
                self._simumenu.entryconfig(i, state='normal')

    def StartOp(self):
        'Start Simulation'
        try:
            self.sim.simulate()
            if self._graphic:
                self.data_out = self.sim.data_output()
                self.start_pos = self.sim.get_startpos()
                self._toggle()  # se utiliza para prevenir errores
                self.handler.graphic_play(self.data_out, self.start_pos,
                                          self.sim.get_pagefault(),
                                          self.SPEED[self.current_speed])
                self._toggle()
        except simulator.SimulatorActiveError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])
        except simulator.SimulatorLoadedError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisnotloaded'])

    def StopOp(self):
        'Sim stop'
        self.sim.stop()

    def ResetOp(self):
        'Sim Reset'
        try:
            self.sim = self.sim.reset()
            self.handler.reset()
            self.handler.display()
        except simulator.SimulatorLoadedError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisnotloaded'])
        except simulator.SimulatorActiveError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisactive'])

    def PlotOp(self):
        'Plot simulators current output'
        p = plotter.Plotter()
        try:
            p.format_plot(self.sim.data_output(), self.sim.get_startpos(),
                        self.sim.get_pagefault())
            p.fig.show()
        except simulator.SimulatorActiveError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisnotactive'])
        except plotter.PlottingError:
            self._error_dialog(data.Lang.active_lang['error_plotting'])
        except simulator.SimulatorLoadedError:
            self._error_dialog(data.Lang.active_lang['error_simulatorisnotloaded'])

    def About(self):
        'Pop About Dialog'

    def display(self):
        'GUI display'
        if sys.platform == 'win32':
            # SDL driver selection
            # recomendado para windows
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        self.set_window_id()
        self._gui.update()
        self.set_handler(PyGameHandler(self.display_size,
                                       self.sim.get_disksize()))
        self.handler.display()
        # TODO: en algunos Linux la pantalla principal
        # de la interfaz grafica pisa a la pantalla de
        # pygame cuando este no esta en ejecucion

    def update(self):
        try:
            self._gui.update()
        except TclError:
            # shutdown exception
            sys.exit(1)

    def set_window_id(self):
        ' sets pygame window ID into Tkinter MainFrame '
#         necesario para que el frame de pygame se vea
#         dentro del MainFrame TkInter
        os.environ['SDL_WINDOWID'] = str(self._main_frame.winfo_id())


def main():
    # First start simulator, then interface
    sim = simulator.Simulator(data.Config.options['disk_size'])
    data.Lang.active_lang = data.Lang.load_lang()
    inter = SimulatorInterface(sim,
            display_size=data.Config.options['display_size'])
    inter.display()
    while 1:
        # Update the pygame display
        # Update the Tk display
        inter.update()
    sys.exit(0)
