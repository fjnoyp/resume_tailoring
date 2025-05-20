from full_tailor_resume.analyze_job_description.job_description_analyzer import job_description_analyzer
from full_tailor_resume.assess_resume_as_company.resume_screener import resume_screener
from full_tailor_resume.tailor_resume.resume_rewriter import resume_rewriter
from langgraph.graph import Graph, START, END

graph_builder = Graph()

# TODO: add condition to get back directly to the resume_rewriter when the user responds

graph_builder.add_node("job_description_analyzer", job_description_analyzer)
graph_builder.add_node("resume_screener", resume_screener)
graph_builder.add_node("resume_rewriter", resume_rewriter)

graph_builder.add_edge(START, "job_description_analyzer")
graph_builder.add_edge("job_description_analyzer", "resume_screener")
graph_builder.add_edge("resume_screener", "resume_rewriter")

def is_ask_user(output):
    if isinstance(output, dict):
        return output.get("type") == "ask_user"
    if hasattr(output, "type"):
        return getattr(output, "type") == "ask_user"
    return False

graph_builder.add_conditional_edges(
    "resume_rewriter",
    lambda output: "ask_user" if is_ask_user(output) else END,
    {
        "ask_user": END,  # or a node that handles user input
        END: END,
    }
)

graph = graph_builder.compile()
