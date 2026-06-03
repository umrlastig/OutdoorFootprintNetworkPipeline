# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os

import unittest

import tracklib as tkl

from footprint2graph import prepareEnv, setupEnv
from footprint2graph import run_iteration
from footprint2graph.util.PlotRes import plotMM
from footprint2graph import second_round


class TestZone1(unittest.TestCase):
    '''
    Test complet sur un jeu de traces simulées à partir d’un réseau.
    C'est le code du notebook dans la documentation
    '''


    def setUp (self):
        resource_path = os.path.join(os.path.split(__file__)[0], "..")
        self.RESPATH = os.path.join(resource_path, './test/result1/')



    def testPipeline(self):

        prepareEnv(self.RESPATH)


        # =====================================================================
        #    Iteration 1

        iteration_index = 1
        setupEnv(self.RESPATH, iteration_index)

        #  Import du réseau
        netpath = os.path.join(self.RESPATH, '../../data/network2.csv')
        fmt = tkl.NetworkFormat({
               "pos_edge_id": 1,
               "pos_source": 2,
               "pos_target": 3,
               "pos_wkt": 0,
               "srid": "ENU",
               "separator": ";",
               "header": 1})

        self.network = tkl.NetworkReader.readFromFile(netpath, fmt, verbose=False)

        # Génération des traces réalistes synthétiques
        tkl.stochastics.seed(333)
        noiser = tkl.NoiseProcess(amps=2.5, kernels=tkl.ExponentialKernel(80))


        # generate simulated trajectories from the network
        collection = tkl.generateTracksOnNetwork(self.network, N=500, p_round_trip=0.05, p_cplx_trip=0.10, resolution=1, noiser=noiser)
        # add 3 attributes
        for idx, track in enumerate(collection):
            track.createAnalyticalFeature('TID', idx+1)
            track.createAnalyticalFeature('MID', idx+1)

        self.collection = collection

        self.assertEqual(len(self.network.EDGES), 7, 'Number of edges=')
        self.assertEqual(len(self.network.NODES), 8 ,'Number of nodes')

        # run pipeline for the first iteration
        run_iteration(iteration_index, self.RESPATH, self.collection)



        # =====================================================================
        #

        from footprint2graph.util.PlotRes import plotSegmentsConstruction
        import matplotlib.pyplot as plt

        fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 4,
           "srid": "ENU",
           "separator": ",",
           "header": 1})

        networkpath = self.RESPATH + 'network/reseau_1.csv'
        squelette = tkl.NetworkReader.readFromFile(networkpath, fmt, verbose=False)

        plt.figure(figsize=(8, 8))
        ax1 = plt.subplot2grid((1, 1), (0, 0))
        plotSegmentsConstruction(self.RESPATH, ax1, squelette)
        plt.show()

        plotMM(self.RESPATH, None)
        plt.show()


        # =====================================================================
        #






if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestZone1("testPipeline"))
    runner = unittest.TextTestRunner()
    runner.run(suite)






