# -*- coding: utf-8 -*-


import tracklib as tkl


"""
smoothing ! filtering, simplifcation


"""


def skeleton_smoothing(geom, wl_inf, wl_sup):
    '''
    Filtre de Fourier coupe-bande sur une géométrie.

    Parameters
    ----------
    geom : Track
        trace ou edge en entrée.
    wl_inf : float
        longueur d'onde de coupure inférieure (en mètres).
    wl_sup : float
        longueur d'onde de coupure supérieure (en mètres).

    Returns
    -------
    Track
        trace filtrée.

    '''
    
    N = len(geom)
    
    # Centrage du signal
    geom = geom.copy()
    c0 = geom.getCentroid(); 
    cx = c0.E; cy = c0.N
    geom.translate(-cx, -cy)
    
    # Sauvegarde des extrémités
    ci = geom[0]
    cf = geom[-1]
    
    # Periodisation du signal
    geom_in = geom.reverse() + geom + geom.reverse()

    if geom_in.length() <= 0:
        return geom.copy()
    
    # Filtre coupe-bande
    signal_low_freq = tkl.filter_freq(geom_in, (1.0/wl_sup), mode=tkl.FILTER_SPATIAL, type=tkl.FILTER_LOW_PASS , dim=tkl.FILTER_XY)[N:2*N]
    signal_hgh_freq = tkl.filter_freq(geom_in, (1.0/wl_inf), mode=tkl.FILTER_SPATIAL, type=tkl.FILTER_HIGH_PASS, dim=tkl.FILTER_XY)[N:2*N]
    
    # Somme passe-haut/passe-bas
    out = geom.copy()
    for i in range(N):
        out[i, "x"] = signal_low_freq[i, "x"] + signal_hgh_freq[i, "x"]
        out[i, "y"] = signal_low_freq[i, "y"] + signal_hgh_freq[i, "y"] 
        
    # Reconstruction des extrémités
    out[0]  = ci
    out[-1] = cf   
        
    # Decentrage du signal
    out.translate(cx, cy)
    
    return out



