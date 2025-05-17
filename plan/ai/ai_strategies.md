# AI Strategies Reference

This document outlines key strategies and considerations for developing robust and effective AI systems.

## 1. Designing AI Interactions & Prompts

### 1.1. Prompting Strategies & Techniques

- **Few-Shot Prompting:** Providing input-output examples to guide the AI.
  - *Use When:* High-quality, representative examples are available; aiming to quickly convey style, tone, or structure.
  - *Benefit (from existing doc):* Anchors the LLM's understanding and aligns its output with expectations.
  - *Caution:* Be mindful of potential bias toward patterns in the examples.

- **Chain-of-Thought (CoT) Reasoning:** Instructing the AI to "think step-by-step" and output its reasoning.
  - *Use When:* Solving complex problems requiring logical reasoning (e.g., math, common sense, symbolic reasoning tasks).
  - *Benefit (from existing doc & notes):* Increases transparency, allows identification of flawed logic, forces structured analysis, and improves performance on relevant tasks.

- **Requirements Specification:** Explicitly outlining all requirements, constraints, and expectations for the AI's output.
  - *Use When:* The task requires the AI to follow many specific constraints.

- **ReAct (Reasoning + Acting):** Combining reasoning and action in an iterative process.
  - *Benefit:* Helps models plan actions, execute them, observe results, and refine their approach.
  - *Use Case:* Particularly useful for tasks requiring information gathering or interaction with external tools.

- **AI Cognitive Load:**
  - Overloading an AI model with too many instructions, too complex a task, or too broad a context in a single prompt can degrade performance.
  - Strive for a balance between "elegance" (concise, general prompts) and "specificity" (detailed instructions for complex tasks).

- **Detailed Rubrics and Structured Prompts (especially for Evaluation):** Providing the AI with a specific checklist or rubric.
  - *Key Aspects:* Defining clear dimensions, establishing scoring/rating scales, and structuring prompts for evaluation against specific criteria/documents (e.g., a JD).

### 1.2. Structuring AI Workflows & Architectures

- **Multi-Stage Reasoning:** Making the AI's reasoning process explicit and stepwise, logically handling each step before producing the final output.
  - *Benefit:* Prevents cognitive overload for the AI.

- **Chains & Agents (e.g., LangChain/LangGraph):**
  - Connecting AI components, tools, and logic into sequences or graphs.
  - **Implementation Examples:**
    - LangGraph: `create_react_agent` (from `langgraph.prebuilt`).
    - LangChain Adapters: `load_mcp_tools` (from `langchain_mcp_adapters.tools`).
    - Server Wrapping: `FastMCP` (from `mcp.server.fastmcp`) to easily wrap functions into an MCP server.

- **Multi-Model Call Architecture:**
  - Utilizing multiple AI models, potentially in parallel or sequence, for different sub-tasks within a larger process (e.g., a decision tree followed by parallel calls for video selection, user fact gathering, RAG).
  - **Benefits:**
    - Can optimize for latency through parallelization (accepting some redundant calls for speed).
    - Offers more fine-tuned control over specific steps compared to relying on a single large reasoning model.
    - Addresses concerns about lack of control, latency of inner reasoning steps in some monolithic models.

- **MDC Rules Structuring (Example):**
  - Using rule types like "agent requested" to enable reasoning "tool" calling.
  - Using "manual" type for strict, explicit referencing of desired rules.
  - Employing a "global orchestrator" rule to guide a step-by-step process that references other rules.

- **Balancing Off-the-Shelf Reasoning Models vs. Custom Agent Architectures:**
  - **Off-the-Shelf Reasoning Models (e.g., models with built-in sequential tool calling):**
    - *Pros:* Faster implementation for multi-step reasoning/tool use; model handles orchestration.
    - *Cons:* Less fine-grained control; harder to dynamically update prompts/tools mid-sequence; potential latency/"black box" reasoning.
  - **Custom Agent Architectures (e.g., ReACT-style, custom LangGraph/LangChain):**
    - *Pros:* Maximum control; dynamic updates (prompts, tools, models); potential for lower step-latency via parallelization; transparent debugging.
    - *Cons:* More complex/time-consuming to design/implement; requires explicit state/flow management.

### 1.3. Output Refinement Strategies

- **Self-Revision:** Instructing the AI to evaluate its own output and make improvements based on specified criteria.
  - *Requirement:* Clearly specify evaluation criteria for the revisions.

- **Critique and Refinement:** A multi-step process: Generate -> Critique (by AI) -> Refine (by AI) -> Final Output.

## 2. Ensuring AI Quality & Reliability

### 2.1. AI Output Grading & Evaluation ("LLM as Judge")

- **Concept:** Using one LLM (the "judge") to evaluate the quality, correctness, or other attributes of an output generated by another AI system.

- **Key Principles for Consistent Evaluation:**
  - **Detailed Rubrics and Structured Prompts:** (See Section 1.1) Provide the judge LLM with a specific checklist or rubric.
  - **Chain-of-Thought (CoT) Reasoning for the Judge:** Instruct the judge LLM to output its reasoning step-by-step for each dimension before giving a final score.
  - **Few-Shot Examples for the Judge:** Include 1-3 examples in the prompt showing the desired evaluation process (e.g., sample AI output, ideal output, rubric-based evaluation, reasoning).
  - **Comparative Analysis:** Frame the evaluation task as a comparison (e.g., original resume vs. tailored resume against a job description; AI response vs. ideal response).
  - **Low Temperature Settings:** Use low `temperature` (e.g., 0.0-0.3) for evaluation API calls to make output more deterministic and consistent.

- **Strategies for Higher Certainty in Judgments (especially for boolean or categorical outputs):**
  - **Prompt Rephrasing:** Ask the question in multiple ways.
  - **Multi-Model Consensus:** Run the same evaluation prompt across different model providers.
  - **Multiple Runs (Non-Zero Temperature):** Run the evaluation multiple times with a non-zero temperature and aggregate results (e.g., majority vote, synthesize a 0-1 confidence score).
  - **Focus on Strong Signals:** Narrow focus to outputs where all (or a high majority of) models/runs agree.

- **Ensemble Methods (Advanced):** Run the evaluation prompt multiple times (or with variations/different models) and aggregate results (e.g., average scores, majority vote) to smooth out anomalies.

- **Important Considerations:**
  - Numeric ratings from LLM judges can be "noisy" and inconsistent initially - boolean allows easier consistency and iteration on prompts and rubrics is crucial.
  - *Evaluator Focus:* Primarily provide backend value for system improvement, not direct end-user features.

### 3.2. Testing Frameworks & Monitoring

- **LangSmith:**
  - **Capabilities:** Aids dataset creation, automated testing, AI system trace logging, and tracking evaluator metrics.
  - *Usage Example:* Integrates via tracing (e.g., `LANGSMITH_TRACING=true` for LangChain/LangGraph) for observability.

- **AI Unit Tests / Regression Testing:**
  - **Dataset Creation:** Curate a dataset of representative inputs (e.g., chat history segments) and corresponding ideal outputs (e.g., an ideal AI response with a specific tool call). "Good" labeled data can be a starting point.
  - **Automated Evaluation:** Run the AI system against this dataset and use evaluators (LLM as Judge, algorithmic checks, embedding distance, etc.) to assess output quality against the ideal outputs.
  - **Importance of Test Datasets:** Crucial as ground truth for evaluating system performance and changes over time.

- **Aligning Ratings with Real Customer Feedback:**
  - Collect real user feedback where possible (e.g., thumbs up/down, explicit ratings on video relevance).
  - Incorporate this feedback into datasets (chat segment + AI output + user rating).
  - Develop LLM-as-Judge evaluators that aim to predict or align with this human feedback.

## 3. General Considerations & Best Practices

- **Balancing Latency, Cost, and Quality:**
  - Parallelization of AI calls can reduce user-perceived latency but may increase computational cost (as some calls might be speculative or unused).
  - Startups often prioritize product-market fit and user experience (latency, quality) first, then optimize for cost.

- **Iterative Development:**
  - AI systems (especially complex reasoning/evaluation) require significant iteration.
  - Start simple, test thoroughly, refine based on performance and metrics.

- **Model Configuration (Temperature):**
  - **Low (e.g., 0.0-0.3):** For deterministic, consistent, factual tasks (evaluation, strict summarization).
  - **Higher:** For creative tasks (can be less predictable).

- **Root Cause Analysis:**
  - When diagnosing issues (e.g., poor RAG retrieval, incorrect tool use), systematically investigate potential failure points: AI logic, data quality, embedding/retrieval efficacy, external tool failures, etc.
