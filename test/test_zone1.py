# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os

import unittest

import tracklib as tkl

from footprint2graph import prepareEnv, setupEnv
from footprint2graph import run_iteration
from footprint2graph import read_config, report_file

from footprint2graph import (plotMM,
                             plotSegmentsConstruction)


class TestZone1(unittest.TestCase):
    '''
    Test complet sur un jeu de traces simulées à partir d’un réseau.
    C'est le code du notebook dans la documentation
    '''


    def setUp (self):
        resource_path = os.path.join(os.path.split(__file__)[0], "..")

        config_path = os.path.join(resource_path, 'data/config_zone1.yml')
        self.config = read_config(config_path)

        self.RESPATH = os.path.join(resource_path, './test/result1/')
        self.config["output"]["RESULT_PATH"] = self.RESPATH


    def testPipeline(self):

        prepareEnv(self.RESPATH)


        # =====================================================================
        #
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
        self.assertEqual(len(self.network.EDGES), 7, 'Number of edges=')
        self.assertEqual(len(self.network.NODES), 8 ,'Number of nodes')

        # ---------------------------------------------------------------------

        # Génération des traces réalistes synthétiques
        tkl.stochastics.seed(333)
        noiser = tkl.NoiseProcess(amps=2.5, kernels=tkl.ExponentialKernel(80))

        # generate simulated trajectories from the network
        collection = tkl.generateTracksOnNetwork(self.network, N=500,
                                                 p_round_trip=0.05, p_cplx_trip=0.10,
                                                 resolution=1, noiser=noiser)
        # add 3 attributes
        for idx, track in enumerate(collection):
            track.createAnalyticalFeature('TID', idx+1)
            track.createAnalyticalFeature('MID', idx+1)



        # =====================================================================
        #    Iteration 1
        #

        # run pipeline for the first iteration
        run_iteration(iteration_index, self.config, collection)


        # =====================================================================
        #    Plots




        # =====================================================================
        # On teste quelques résultats intermédiaires
        '''
        # nombre de traces en point d'entrée
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                               'separator': ';',
                               'header': 1,
                               'read_all': True})
        resampledtracespath = self.RESPATH + 'resample_grid' + '/'
        tracks = tkl.TrackReader.readFromFile(resampledtracespath, fmt, verbose=False)
        self.assertEqual(len(tracks), 444, 'Number of tracks after segmentation=')
        '''
        
        # =====================================================================
        #


    def testParam(self):
        self.assertEqual(self.config["graph_construction"]["NUM_ITERATIONS"], 1)
        self.assertEqual(self.config["iterations"][0]["SEUIL_DENSITE"], 25)


    def testPrintLog(self):
        report_file(self.RESPATH, 'env.json')
        report_file(self.RESPATH, 'rawdata.json')
        report_file(self.RESPATH, 'image1.json')
        report_file(self.RESPATH, 'topology1.json')
        report_file(self.RESPATH, 'mapmatch1.json')
        report_file(self.RESPATH, 'candidate1.json')
        report_file(self.RESPATH, 'aggregate1.json')
        report_file(self.RESPATH, 'conflate1.json')


    def testPlot(self):
        '''
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

        # ---------------------------------------------------------------------
        plotMM(self.RESPATH, squelette)
        plt.show()

        # ---------------------------------------------------------------------
        plt.figure(figsize=(8, 8))
        ax1 = plt.subplot2grid((1, 1), (0, 0))
        plotSegmentsConstruction(self.RESPATH, ax1, squelette)
        plt.show()
        '''
        # ---------------------------------------------------------------------
        chemin = self.RESPATH + 'image/G1_1.asc'
        rasterG1 = tkl.RasterReader.readFromAscFile(chemin, name='G1', separator='\t')
        mapGeomDensity = rasterG1.getAFMap('G1')
        mapGeomDensity.plotAsImage(cmap='jet', vmin=0)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestZone1("testParam"))
    suite.addTest(TestZone1("testPipeline"))
    suite.addTest(TestZone1("testPrintLog"))
    suite.addTest(TestZone1("testPlot"))
    runner = unittest.TextTestRunner()
    runner.run(suite)






