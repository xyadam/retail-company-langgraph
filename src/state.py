from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


###########################################################################
##                             STATE
###########################################################################

class AgentState(TypedDict):
    ###### Conversation ######
    messages: Annotated[list, add_messages]  # conversation history (auto-appended)
    user_question: str                       # current user input
    intent: str                              # "data_query" or "general"
    
    ###### Knowledge ######
    golden_examples: str                     # few-shot examples from golden knowledge bucket

    ###### SQL #######
    generated_sql: str                       # SQL produced by sql_generator
    rows: list                               # query result rows (list of dicts)
    error_message: str                       # SQL error for retry loop
    retry_count: int                         # current retry attempt (max 3)
    
    ###### Report ######
    final_report: str                        # formatted report for the user
