# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML included four classes: Owner, Pet, Task, and Scheduler. Owner manages multiple pets, Pet stores pet information and its tasks, and Task represents a care activity with a description, scheduled time, frequency, and completion status. Scheduler organizes tasks across all pets.

The three main user actions were adding a pet, scheduling a care task, and viewing today’s schedule. I separated the backend from the Streamlit interface so I could check the logic independently.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

During implementation, I refined Task to include both a due date and a unique ID. A time alone could not distinguish today’s task from its next recurring occurrence. Unique IDs also help the interface edit or complete the correct task.

I also made Scheduler retrieve tasks through Owner.get_all_tasks() so it could organize tasks across multiple pets consistently.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers due dates, scheduled times, completion status, task duration, priority, and the owner’s available care time. The daily planner considers only incomplete tasks due on the selected date.

I prioritized high-priority tasks before lower-priority tasks because activities such as medication and feeding can be more urgent than grooming. The available time budget determines which tasks fit, and the selected tasks are displayed chronologically.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is that conflict detection checks for tasks with the same date and start time rather than all overlapping durations. This keeps the logic simple and makes warnings easy to understand, but it can miss a task that starts while another task is still happening.

This is reasonable for an initial version that helps owners notice obvious conflicts. Duration-based overlap detection would be a useful next improvement.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI to brainstorm class responsibilities, draft the Mermaid UML, scaffold the Python classes, and suggest scheduling algorithms and tests. I also used it to help connect the backend to Streamlit and improve documentation.

The most useful prompts specified the relevant files, expected behavior, and constraints. For example, asking the Scheduler to retrieve tasks through Owner.get_all_tasks() made the multi-pet requirement explicit. Separate chats for implementation and testing helped keep each discussion focused.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I revised the AI-assisted workflow by using staged prompts instead of requesting the entire application at once. I first requested the UML and class skeletons, then the backend, interface, and tests. This made each stage easier to review.

I evaluated suggestions against the assignment requirements and the class responsibilities. The CLI demo and pytest suite provided ways to check whether the generated code behaved as expected, rather than relying only on the AI’s explanation.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

My test suite checks task completion, task addition, chronological sorting, filtering, recurring tasks, and conflict detection. It also checks that the Scheduler retrieves tasks across multiple pets.

These tests matter because the interface depends on the backend returning correct results. Recurrence tests check that completing a task creates the next occurrence without duplicating it. Conflict tests check that matching times on different dates are not incorrectly treated as conflicts.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

My confidence depends on the automated test results and the manual interface checks. These provide useful coverage of the main workflows, but they do not prove that every possible situation is handled.

With more time, I would test overlapping task durations, overdue recurring tasks, large task lists, and repeated editing and completion actions. I would also add automated interface tests.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with separating the scheduling logic from the interface. This made the system easier to understand and allowed the CLI demo and Streamlit app to use the same backend.

The multi-pet design was also useful because an owner can view one combined schedule instead of checking each pet separately.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would add JSON save/load functionality so pets and tasks remain available after the application closes. I would also improve conflict detection to account for task durations and suggest alternative times.

I would keep the interface simple while making skipped tasks and scheduling warnings clearer.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that designing a system means deciding how responsibilities and data are shared between classes. A clear design made implementation and testing easier.

Working with AI also showed me the importance of giving specific context and checking the results. AI can help generate code, but I still need to understand the behavior, make design decisions, and verify correctness.


