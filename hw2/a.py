import numpy as np
from pgmpy_onGithub.pgmpy.models import MarkovModel
from pgmpy_onGithub.pgmpy.factors.discrete import DiscreteFactor
from pgmpy_onGithub.pgmpy.inference import Mplp
mm = MarkovModel()
mm.add_edges_from([('A', 'B')])
phi = [DiscreteFactor(edge, [2, 2], np.random.rand(4)) for edge in mm.edges()]
mm.add_factors(*phi)
print(phi.scope())
#print(mm.check_model())
#mplp = Mplp(mm)
#print(mplp.map_query())
