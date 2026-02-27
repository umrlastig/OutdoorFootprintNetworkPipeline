# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import tracklib as tkl


RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/'
SEARCH = 25




# =============================================================================


fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 4,
       "srid": "ENU",
       "header": 1})

netwokpath = RESPATH + 'network/reseau.csv'
network = tkl.NetworkReader.readFromFile(netwokpath, fmt)


fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})
tracespath = RESPATH + '/resample_fusion/'
collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
print ('Nombre de traces:', collection2.size())

collection = tkl.TrackCollection()
for trace in collection2:
    num = trace.getObsAnalyticalFeature('num', 0)

    if str(num) != '12299352.0' and str(num) != '12041476.0' and str(num) != '1198186.0':
        continue

    track_id = trace.getObsAnalyticalFeature('track_id', 0)
    user_id = trace.getObsAnalyticalFeature('user_id', 0)

    trace.uid = user_id
    trace.tid = num
    collection.addTrack(trace)




si = tkl.SpatialIndex(network, verbose=False)
network.spatial_index = si


# Computes all distances between pairs of nodes
network.prepare()


# Map track on network
print ('Launching Map-matching')
tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=True)
print ('Map-matching ended')




MM = {}   #  [ide][pkid] : liste des observations

for i in range(collection.size()):
    track = collection.getTrack(i)
    track.createAnalyticalFeature('mmtype', 'NOT')
    track.createAnalyticalFeature('idedge', -1)
    pkid = track.tid

    for j in range(track.size()):

        pb  = track[j].position
        ds = float(track["hmm_inference", j][2])
        dt = float(track["hmm_inference", j][3])
        idxedge = int(track["hmm_inference", j][1])

        edgeid = network.getEdgeId(idxedge)
        e = network.EDGES[edgeid]

        if idxedge == -1:
            track.setObsAnalyticalFeature('mmtype', j, 'NOT')
            track.setObsAnalyticalFeature('idedge', j, -1)
        elif ds > 0.01 and dt > 0.01:
            if edgeid not in MM:
                MM[edgeid] = {}
            if pkid not in MM[edgeid].keys():
                MM[edgeid][pkid] = []
            MM[edgeid][pkid].append((j,pb))
            track.setObsAnalyticalFeature('mmtype', j, 'EDGE')
            track.setObsAnalyticalFeature('idedge', j, edgeid)
        elif abs(ds) < 0.01:
            idnode = e.source.id
            edgesid = network.getIncidentEdges(idnode)
            for eid in edgesid:
                if eid not in MM:
                    MM[eid] = {}
                if pkid not in MM[eid].keys():
                    MM[eid][pkid] = []
                MM[eid][pkid].append((j,pb))
            track.setObsAnalyticalFeature('mmtype', j, 'SOURCE')
            track.setObsAnalyticalFeature('idedge', j, idnode)
        elif abs(dt) < 0.01:
            idnode = e.target.id
            edgesid = network.getIncidentEdges(idnode)
            for eid in edgesid:
                if eid not in MM:
                    MM[eid] = {}
                if pkid not in MM[eid].keys():
                    MM[eid][pkid] = []
                MM[eid][pkid].append((j,pb))
            track.setObsAnalyticalFeature('mmtype', j, 'TARGET')
            track.setObsAnalyticalFeature('idedge', j, idnode)


edgeid = '11182'
e = network.EDGES[edgeid]
# trackid = 12299352
# trackid = 12041476
trackid = 1198186
tobs = MM[edgeid][trackid]



tn = tkl.Track()
v = 1
points_sorted = sorted(tobs, key=lambda x: x[0])
p1 = None
jp1 = -1
for p in points_sorted:
    # print (p[0])
    p2 = p[1]
    if p1 is not None:
        if jp1 + 1 < p[0]:
            # on coupe la trace pour créer un nouveau morceau
            cb = return_candidate_for_aggregate(tn, e, SEARCH)
            for tb in cb:
                # print (tb.toWKT())
                tid = str(trackid) + "-v" + str(v)
                v += 1
            tn = tkl.Track()

    tn.addObs(tkl.Obs(p2, tkl.ObsTime()))
    p1 = p2
    jp1 = p[0]


# dernier morceau de trace
cb = return_candidate_for_aggregate(tn, e, SEARCH)
for tb in cb:
    tid = str(trackid) + "-v" + str(v)
    v += 1



























