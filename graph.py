from langgraph.graph import StateGraph,END
from agents.segregator import segregation
from agents.id_agent import extract_id_details
from agents.bill_agent import extract_bill_details
from agents.discharge_agent import extract_discharge_details
from typing_extensions import TypedDict,List,Dict
from agents.aggregator import aggregate_results

class State(TypedDict):
    claim_id: str
    pages: List[Dict]
    classified_pages: Dict[str, List[Dict]]
    identity_data: Dict
    discharge_data: Dict
    bill_data: Dict
    final_result: Dict

def segregation_node(state:State):
    pages = state['pages']
    result = segregation(pages)
    return {**state,'classified_pages':result} #This pages will be divided into the 9 doc types List[Dict]

def id_agent_node(state:State):
    pages = state['classified_pages']
    result=extract_id_details(pages)
    return {**state,'identity_data':result} 

def discharge_agent_node(state:State):
    pages = state['classified_pages']
    result = extract_discharge_details(pages)
    return {**state,'discharge_data':result}

def bill_agent_node(state:State):
    pages = state['classified_pages']    
    result = extract_bill_details(pages)
    return {**state,'bill_data':result}

def aggregator_node(state:State):
    identity_data = state['identity_data']
    discharge_data = state['discharge_data']
    bill_data = state['bill_data']
    result = aggregate_results(identity_data,discharge_data,bill_data)
    return {**state,'final_result':result}

def create_graph():
    #Start Graph
    workflow = StateGraph(State)
    #Add nodes
    workflow.add_node("segregation_node",segregation_node)
    workflow.add_node("id_agent_node",id_agent_node)
    workflow.add_node("discharge_agent_node",discharge_agent_node)
    workflow.add_node("bill_agent_node",bill_agent_node)
    workflow.add_node("aggregator_node",aggregator_node)
    #Add edges
    workflow.set_entry_point('segregation_node')
    workflow.add_edge("segregation_node","id_agent_node")
    workflow.add_edge("segregation_node","discharge_agent_node")
    workflow.add_edge("segregation_node","bill_agent_node")
    workflow.add_edge("id_agent_node","aggregator_node")
    workflow.add_edge("discharge_agent_node","aggregator_node")
    workflow.add_edge("bill_agent_node","aggregator_node")
    workflow.add_edge("aggregator_node",END)
    
    #Compile the graph
    return workflow.compile()
    