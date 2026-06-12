# -*- coding: utf-8 -*-


import os
import platform
import psutil
import shutil
import time
import yaml


from . import log_event



def read_config(paramfile):
    with open(paramfile) as f:
        config = yaml.safe_load(f)

    return config



def prepareEnv(respath, iteration_index = None):
    '''
    On supprime tous les répertoires
    '''
    if iteration_index is None or int(iteration_index) <= 0:
        for filename in os.listdir(respath):
            file_path = os.path.join(respath, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        idx = int (iteration_index)




def setupEnv(respath, iteration_index = -1):
    """ =================================================================== """
    """     Preparation de l'environnement pour une itération               """
    """   - création des répertoires si nécessaire                          """
    """                                                                     """
    """ =================================================================== """

    idx = int (iteration_index)

    if idx == 1:
        if not os.path.exists(respath + 'decoup'):
            os.makedirs(respath + 'decoup')
        if not os.path.exists(respath + 'resample_grid'):
            os.makedirs(respath + 'resample_grid')
        if not os.path.exists(respath + 'resample_fusion'):
            os.makedirs(respath + 'resample_fusion')
        if not os.path.exists(respath + 'image'):
            os.makedirs(respath + 'image')
        if not os.path.exists(respath + 'network'):
            os.makedirs(respath + 'network')
        if not os.path.exists(respath + 'mapmatch'):
            os.makedirs(respath + 'mapmatch')
        if not os.path.exists(respath + 'mapmatch/tmm1'):
            os.makedirs(respath + 'mapmatch/tmm1')
        if not os.path.exists(respath + 'geometry'):
            os.makedirs(respath + 'geometry')
        if not os.path.exists(respath + 'geometry/fusion1'):
            os.makedirs(respath + 'geometry/fusion1')
        if not os.path.exists(respath + 'geometry/raccord1'):
            os.makedirs(respath + 'geometry/raccord1')


    if idx > 1:
        pathnotmm = respath + 'points_not_mm_' + str(idx)
        if not os.path.exists(pathnotmm):
            os.makedirs(pathnotmm)

        pathtmm = respath + 'mapmatch/tmm' + str(idx)
        if not os.path.exists(pathtmm):
            os.makedirs(pathtmm)
        pathfusion = respath + 'geometry/fusion' + str(idx)
        if not os.path.exists(pathfusion):
            os.makedirs(pathfusion)
        pathracc = respath + 'geometry/raccord' + str(idx)
        if not os.path.exists(pathracc):
            os.makedirs(pathracc)

        pathmerge = respath + 'merge_' + str(idx)
        if not os.path.exists(pathmerge):
            os.makedirs(pathmerge)


def logEnv(RESPATH):
    try:
        user = os.getlogin()
        system = platform.system() + '-' + platform.processor()
        pythonversion = platform.python_version()
        process = psutil.Process(os.getpid())
        memory_bytes = process.memory_info().rss
        memory_mb = memory_bytes / (1024 * 1024)

        log_event(RESPATH + "env.json", {
            "User": user,
            "System": system,
            "Python version": pythonversion,
            "Heap memory": round(memory_mb), # ' Mo'
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('ERROR in Environment Information.')












