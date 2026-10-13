# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to build PawPal+ incrementally: create the four-class design and UML skeleton, implement the backend and Streamlit UI, add tests, run the CLI demo and pytest, and finish the README/UML documentation using actual project output.

**What did the agent do?**

The agent read the existing project files, created `pawpal_system.py` and `diagrams/uml_draft.mmd`, implemented validation, sorting, filtering, recurrence, conflicts, and daily planning, connected `app.py` to the backend with Streamlit forms and session state, created and expanded `tests/test_pawpal.py`, and ran `python main.py`, `python -m pytest`, and Python compilation checks. It then created `diagrams/uml_final.mmd` and updated the README with captured output.

**What did you have to verify or fix manually?**

The test run initially found an incorrect expectation in the new daily-plan test: the scheduler chooses by priority but returns selected tasks chronologically. The test was corrected to assert those two behaviors separately. The final pytest run reported 24 passing tests. No browser verification was performed.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
