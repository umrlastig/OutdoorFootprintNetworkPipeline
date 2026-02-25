# -*- coding: utf-8 -*-


import tracklib as tkl


def bonneTrace(tn, edge, NB_OBS_MIN, SEARCH):
    '''
    Fonction utilitaire.
    Une trace est gardée pour la fusion si son point de départ est "proche" 
    d'un noeud de l'arc et son point d'arrivée est "proche" de l'autre noeud de l'arc.
    '''

    morceaux = tkl.TrackCollection()

    if tn.size() >= NB_OBS_MIN:

        p1 = tn.getFirstObs().position
        p2 = tn.getLastObs().position

        s = edge.source.coord
        t = edge.target.coord

        if edge.geom.length() < SEARCH:
            if p1.distance2DTo(s) < SEARCH/2 and p2.distance2DTo(t) < SEARCH/2:
                morceaux.addTrack(tn)
            if p1.distance2DTo(t) < SEARCH/2 and p2.distance2DTo(s) < SEARCH/2:
                morceaux.addTrack(tn.reverse())
        else:

            if p1.distance2DTo(s) < SEARCH/2:
                reverse = False
                atteint = False
                dd = 0
                for idx, o in enumerate(tn):
                    if o.position.distance2DTo(t) < SEARCH/2:
                        atteint = True
                    if atteint and o.position.distance2DTo(t) > SEARCH/2:
                        # la deuxième partie de la trace est sortie
                        t1 = tn.extract(dd, idx-1)
                        dd = idx
                        morceaux.addTrack(t1)
                        t = s
                        s = o.position
                        atteint = False
                        reverse = True
                if atteint:
                    t1 = tn.extract(dd, idx)
                    if reverse:
                        morceaux.addTrack(t1.reverse())
                    else:
                        morceaux.addTrack(t1)


            if p2.distance2DTo(s) < SEARCH/2:
                tnr = tn.reverse()
                reverse = False
                atteint = False
                dd = 0
                for idx, o in enumerate(tnr):
                    if o.position.distance2DTo(t) < SEARCH/2:
                        atteint = True
                    if atteint and o.position.distance2DTo(t) > SEARCH/2:
                        # la deuxième partie de la trace est sortie
                        t1 = tn.extract(dd, idx-1)
                        dd = idx
                        morceaux.addTrack(t1)
                        t = s
                        s = o.position
                        atteint = False
                        reverse = True
                if atteint:
                    t1 = tnr.extract(dd, idx)
                    if reverse:
                        morceaux.addTrack(t1.reverse())
                    else:
                        morceaux.addTrack(t1)

    return morceaux













