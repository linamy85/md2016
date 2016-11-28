#from Inference_Markov_github import *
from Inference_Markov import *

G = buildModel(100, 100, [11, 12], [(11, 12)])
fh = {}
fh[11] = (0.1, 0.2)
fh[12] = (0.1, 0.2)
g = {}
g[(11,12)] = 0.7
G, p_dict = inference(G, 100, 100, 1, fh, g, 3)
F = G.get_factors()

