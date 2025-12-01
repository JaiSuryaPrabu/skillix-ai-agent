# skillix-ai-agent
Skillix is a multi-agent educational system built using Google’s Agent Development Kit (ADK) in Python. It is submitted to the **Agents for Good** track because it directly tackles a major problem in education: the lack of truly personalized, scalable, one-on-one tutoring for every student, especially for self-learners.

The system consists of five specialized agents coordinated by a central orchestrator, long-term memory (Memory Bank), and session state management. It turns a static topic request into a fully adaptive learning experience that adjusts in real-time to the student’s knowledge level, preferred learning style, and performance.

### Problem Statement
Traditional online education (videos, articles, MOOCs) is largely one-size-fits-all and passive. Students often:
- Receive content that is too easy or too hard
- Get spoon-fed answers instead of being guided to think critically
- Lack immediate, nuanced feedback on their understanding
- Have no clear visibility into their own strengths, weaknesses, or optimal learning style
- Drop out because the experience feels impersonal and ineffective

High-quality human tutoring is proven to be the most effective learning intervention (Bloom’s 2-sigma problem), but it is expensive and doesn’t scale. Skillix brings the benefits of an expert human tutor—personalization, Socratic questioning, real-time evaluation, and reflective insights to anyone who are curious to learn.

### Solution Statement
Skillix uses a multi-agent architecture where each agent has a clearly defined role, allowing the system to handle the end-to-end complexity of personalized education:

1. **Orchestrator Agent** – Acts as the “tutor session manager” that gathers initial user preferences and coordinates the entire syb agents dynamically
2. **Search Agent** – Searches the web, curates high-quality resources.
3. **Planning Agent** – Designs a personalized syllabus/roadmap based on user’s current knowledge level.
4. **Teaching Agent** – Runs the interactive session using Socratic questioning and active recall. It forces the student to think instead of passively receiving information. Uses long-term memory for context and session state to remember everything that happened in previous interactions.
5. **Evaluating Agent** – Scores every student response in real-time (depth of understanding, partial credit, misconceptions) and updates performance memory.

![Flowchart](assets/flow_chart.png)

### Shared Components
- Long-Term Memory : Single shared memory storing:
    - Curated topic resources and summaries (from Search Agent)
    - Full conversation history
    - User performance data, identified strengths/weaknesses, and inferred learning style
- Session State Management: Handled by the Orchestrator using ADK’s InMemorySessionService (or persistent equivalent)

### Essential Tools Implemented
- Multi-agent delegation (Orchestrator delegates to specialized agents)
- Built-in and custom tools (Google Search tool + memory)
- Session state persistence

The link for the capstone project writeup is [Skillix: Multi-agent AI for student skill mastery](https://www.kaggle.com/competitions/agents-intensive-capstone-project/writeups/skillix-multi-agent-ai-for-student-skill-mastery)

Skillix proves that multi-agent systems can deliver truly personalized education at scale, making world-class tutoring accessible to everyone.

## Project Installation
1. Clone this github repo
```bash
git clone https://github.com/JaiSuryaPrabu/skillix-ai-agent
```
2. Use `uv` to install the packages for virtual environment by `sync` command
```bash
uv sync 
```
3. Activate your virtual environment by
```bash
source venv/bin/activate # macOS/Linux (change venv to your actual venv environment name)
venv\Scripts\activate.bat # Command Prompt Windows
.\venv\Scripts\Activate.ps1 # PowerShell Windows
```
3. `main.py` is used to run the streamlit app and to run the app. Go to app directory using cd app and run the below command to run the streamlit.
```bash
streamlit run app/main.py
```