import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from typing import Any
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.graph import workflow
from src.console import print_report

console = Console()


###########################################################################
##                             MAIN
###########################################################################

def main():
    graph = workflow.compile(checkpointer=MemorySaver())
    thread_config = {"configurable": {"thread_id": "1"}}

    console.print("\n[bold cyan]OpsFleet Data Analysis Agent[/bold cyan]")
    console.print("[dim]Ask questions about sales, orders, products, and more.[/dim]")
    console.print("[dim]Type 'quit' to exit.[/dim]\n")

    while True:
        question = console.input("[bold]You:[/bold] ").strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            console.print("[dim]Goodbye![/dim]")
            break

        payload: dict[str, Any] = {
            "user_question": question,
            "messages": [HumanMessage(content=question)],
            "rows": [],
            "retry_count": 0,
            "error_message": "",
            "generated_sql": "",
        }
        result = graph.invoke(payload, config=thread_config)

        ################### Handle interrupt loop (human-in-the-loop) ###################
        while result.get("__interrupt__"):
            confirmation_msg = result["__interrupt__"][0].value
            console.print(f"\n[bold yellow]{confirmation_msg}[/bold yellow]")
            answer = console.input("[bold]Confirm:[/bold] ").strip()
            result = graph.invoke(Command(resume=answer), config=thread_config)

        print_report(result["final_report"])


if __name__ == "__main__":
    main()
