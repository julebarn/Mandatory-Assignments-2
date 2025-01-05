
import tempfile

from enum import Enum
from graphviz import Digraph
from pm4py.objects.dcr.hierarchical.obj import HierarchicalDcrGraph
from pm4py.util import exec_utils, constants


filename = tempfile.NamedTemporaryFile(suffix=".gv")
filename.close()

class Parameters(Enum):
    FORMAT = "format"
    RANKDIR = "set_rankdir"
    AGGREGATION_MEASURE = "aggregationMeasure"
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"
    DECORATIONS = "decorations"





def apply(dcr: HierarchicalDcrGraph, parameters):
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    set_rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, 'LR')
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, "12")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)

    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor, 'rankdir': set_rankdir, "compound":"true", "pad":"0.5"},
                  node_attr={'shape': 'Mrecord' }, edge_attr={'arrowsize': '0.5'})
    viz.node("proxyG", label='', shape='point', width='0.0', height='0.0', style='invis') 
    
    for event in dcr.events:
        if event in dcr.nestedgroups_map:
            continue
        create_node(dcr, font_size, viz, event)
    
    for event in dcr.conditions:
        for event_prime in dcr.conditions[event]:
            create_edge(dcr,event_prime, event, 'condition', viz , font_size)

    for event in dcr.responses:
        for event_prime in dcr.responses[event]:
            create_edge(dcr,event, event_prime, 'response', viz, font_size)

    for event in dcr.includes:
        for event_prime in dcr.includes[event]:
            create_edge(dcr,event, event_prime, 'include', viz)

    for event in dcr.excludes:
        for event_prime in dcr.excludes[event]:
            create_edge(dcr,event, event_prime, 'exclude', viz)

    if hasattr(dcr, 'noresponses'):
        for event in dcr.noresponses:
            for event_prime in dcr.noresponses[event]:
                create_edge(dcr,event, event_prime, 'noresponse', viz)

    if hasattr(dcr, 'milestones'):
        for event in dcr.milestones:
            for event_prime in dcr.milestones[event]:
                create_edge(dcr,event, event_prime, 'milestone', viz)

    viz.attr(overlap='false')
    viz.format = image_format.replace("html", "plain-text")

    print(viz.source)

    return viz

def create_node(dcr, font_size, viz, event):

    if event in dcr.nestedgroups:
        with viz.subgraph(name="cluster_"+event) as c:
            c.attr(label=event)
            proxy_node = 'proxy_' + event
            c.node(proxy_node, label='', shape='point', width='0.0', height='0.0', style='invis') 

         
            for nested_event in dcr.nestedgroups[event]:
                create_node(dcr, font_size, c, nested_event)
        return


    label = None
    try:
        roles = []
        key_list = list(dcr.role_assignments.keys())
        value_list = list(dcr.role_assignments.values())
        for count, value in enumerate(value_list):
            if event in value:
                roles.append(key_list[count])
        roles = ', '.join(roles)
    except AttributeError:
        roles = ''
    pending_record = ''
    if event in dcr.marking.pending:
        pending_record = '!'
    executed_record = ''
    if event in dcr.marking.executed:
        executed_record = '&#x2713;'
    label_map = ''
    if event in dcr.label_map:
        label_map = dcr.label_map[event]
    label = '{ ' + roles  + ' | ' + executed_record + ' ' + pending_record + ' } | { ' + label_map + ' }'
    included_style = 'solid'
    if event not in dcr.marking.included:
        included_style = 'dashed'
    viz.node(event, label, style=included_style,font_size=font_size)

def create_edge(dcr, source, target, relation, viz, font_size = None):
    
    ltail = None
    if source in dcr.nestedgroups:
        ltail = 'cluster_' + source
        source = 'proxy_'+source


    lhead = None
    if target in dcr.nestedgroups:
        lhead = 'cluster_' + target
        target = 'proxy_'+target
        

    
    viz.edge_attr['labeldistance'] = '0.0'
    if font_size:
        font_size = int(font_size)
        font_size = str(int(font_size - 2/3*font_size))
 
    match relation:
        case 'condition':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#FFA500', arrowhead='dotnormal')
        case 'exclude':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#FC0C1B', arrowhead='normal', arrowtail='none', headlabel='%', labelfontcolor='#FC0C1B', labelfontsize='8')
        case 'include':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#30A627', arrowhead='normal', arrowtail='none', headlabel='+', labelfontcolor='#30A627', labelfontsize='10')
        case 'response':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#2993FC', arrowhead='normal', arrowtail='dot', dir='both')
        case 'noresponse':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#7A514D', arrowhead='normal', headlabel='x', labelfontcolor='#7A514D', labelfontsize='8', arrowtail='dot', dir='both')
        case 'milestone':
            viz.edge(source, target, lhead=lhead, ltail=ltail, color='#A932D0', arrowhead='normal', headlabel='&#9671;', labelfontcolor='#A932D0', labelfontsize='8', arrowtail='dot', dir='both')
    return

