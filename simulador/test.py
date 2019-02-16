''' TESTEO GENERICO DEL SIMULADOR
BATERIA DE TESTS PARA EL SIMULADOR,
incluyen test de entrada salida,
y test de seleccion de algoritmo'''

import unittest
import simulator


class TestSimulator(unittest.TestCase):
    # TODO: faltan implementar tests
    def setUp(self, disk_size=512):
        'test envirnment setup'
        self.test_sim = simulator.Simulator(disk_size)

    def _test_algo_selection(self, algo):
        'test if algorithm selection works'
        if not(algo in self.test_sim._ALGO_KEY.keys()):
            self.assertRaises(simulator.AlgorithmInputError,
                              self.test_sim.algorithm(algo))

    def _test_output(self, input_list, output_list,
                    algo, orientation='e'):
        'simulator output test'
        self.test_sim.algorithm(algo)
        self.test_sim.data_input(input_list, orientation)
        self.test_sim.simulate()
        self.assertEqual(self.test_sim.data_output(), output_list)
        self.test_sim.stop()
        self.test_sim.reset()

    def test_simpletest(self):
        ' simple simulator I/O test'
        # fcfs test normal
        self._test_algo_selection('fcfs')
        self._test_output('50,pf20,pf10,40,50,80,100,90,240',
                        [20, 10, 40, 50, 80, 100, 90, 240], 'fcfs')
        # fcfs test extra
        self._test_output('5,pf0,200,100', [0, 200, 100], 'fcfs')
        # sstf test normal
        self._test_algo_selection('sstf')
        self._test_output('35,pf30,40,100,250,88,74,10',
                          [30, 40, 10, 74, 88, 100, 250], 'sstf')
        # sstf test extra
        self._test_output('8,pf10,5,40,60', [10, 5, 40, 60], 'sstf')
        # scan test normal 1
        self._test_algo_selection('scan')
        self._test_output('40, 10, 50, 200, 412,100,105',
                          [50, 100, 105, 200, 412, 511, 10],
                          'scan', 'e')
        # scan test normal 2
        self._test_output('10,pf30,50,300,12,60',
                          [30, 50, 60, 300, 511, 12], 'scan', 'w')
        # scan test extra 1
        self._test_output('15, 500', [0, 500], 'scan', 'w')
        # scan test extra 2
        self._test_output('40,pf30,150', [30, 0, 150], 'scan', 'e')
        # cscan test normal
        self._test_algo_selection('cscan')
        self._test_output('40,10,50,200,412,100,105',
                          [50, 100, 105, 200, 412, 511, -1, 0, 10],
                          'cscan', 'e')
        # cscan test normal 2
        self._test_output('10,pf30,50,300,12,60',
                          [30,  12, 0, -1, 511, 300, 60, 50],
                          'cscan', 'w')
        # cscan test extra 1
        self._test_output('50, 400', [0, -1, 511, 400],
                          'cscan', 'w')
        # cscan test extra 2
        self._test_output('40,pf60,10', [60, 511, -1, 0, 10],
                          'cscan', 'e')
        # look test normal 1
        self._test_algo_selection('look')
        self._test_output('40, 10, 50, 200, 412,100,105',
                          [50, 100, 105, 200, 412, 10], 'look', 'e')
        # look test normal 2
        self._test_output('10,pf30,50,300,12,60',
                          [30, 50, 60, 300, 12], 'look', 'w')
        # look test extra 1
        self._test_output('30,400', [400], 'look', 'w')
        # look test extra 2
        self._test_output('40,80,100', [80, 100], 'look', 'e')
        # clook test normal 1
        self._test_algo_selection('clook')
        self._test_output('40,10,50,200,412,100,105',
                          [50, 100, 105, 200, 412, -1, 10],
                          'clook', 'e')
        # clook test normal 2
        self._test_output('10,pf30,50,300,12,60',
                          [30,  12, -1, 300, 60, 50],
                          'clook', 'w')
        # clook test extra 1
        self._test_output('60,pf80,20', [80, 20], 'clook', 'w')
        # clook test extra 2
        self._test_output('70,20', [-1, 20], 'clook', 'e')

    def test_dataintegrity(self):
        'test data integrity'
        self.test_sim.data_input('20,30,40')
        self.test_sim.simulate()
        self.assertRaises(simulator.SimulatorActiveError,
                          self.test_sim.data_input, '20,30,40')
        self.assertRaises(simulator.SimulatorActiveError,
                          self.test_sim.algorithm, 'cscan')
        self.test_sim.stop()
        self.assertEqual(self.test_sim._req_list,
                        [30, 40])
        self.assertEqual(self.test_sim.algo, 'fcfs')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulator)
    unittest.TextTestRunner(verbosity=2).run(suite)
