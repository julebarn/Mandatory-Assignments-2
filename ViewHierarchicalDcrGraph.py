
from copy import deepcopy
from pm4py.util import constants
from pm4py.objects.dcr.obj import DcrGraph
from pm4py.util import exec_utils

import variantHierarchicalDcr

def View_HierarchicalDcr(dcr: DcrGraph, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    print("Viewing Hierarchical DCR")
    format = str(format).lower()
    from pm4py.visualization.dcr import visualizer as dcr_visualizer
    #gviz = dcr_visualizer.apply(dcr,variant=variantHierarchicalDcr , parameters={"format": format, "bgcolor": bgcolor, "set_rankdir": rankdir})
    
    dcr = deepcopy(dcr)
    gviz = variantHierarchicalDcr.apply(dcr, parameters={"format": format, "bgcolor": bgcolor, "set_rankdir": rankdir})
    
    dcr_visualizer.view(gviz)