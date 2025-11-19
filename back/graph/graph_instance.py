# back/graph/graph_instance.py
from pydantic_graph import Graph
from back.graph.nodes.dispatcher_node import DispatcherNode
from back.graph.nodes.narrative_node import NarrativeNode
from back.graph.nodes.combat_node import CombatNode

# Global session graph instance (stateless, reusable across requests)
session_graph = Graph(nodes=(DispatcherNode, NarrativeNode, CombatNode))