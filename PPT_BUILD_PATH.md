# PPT Build Path (Sequence-Wise)

This file gives a clean, step-by-step path to build your presentation quickly.

## 1. Goal of the PPT

Create a clear story:
1. Problem
2. Idea
3. Architecture
4. Implementation
5. Results
6. Why it matters

## 2. Before You Start (10 min)

Collect these from project:
1. Core logic: agents.py, communication_system.py
2. Website flow: webapp/views.py, webapp/templates/webapp/index.html
3. IMMAC extension: immac_extension.py, immac_demo.py
4. A2A extension: a2a_architecture.py, a2a_demo.py
5. Output screenshots:
   - Website home page
   - Episode table
   - Speaker/Listener demo panel
   - Terminal output from immac_demo.py and a2a_demo.py

## 3. Recommended Slide Sequence (12 slides)

### Slide 1: Title
- Project name
- Team names
- Institute / course

### Slide 2: Problem Statement
- Why multi-agent communication is hard
- Limitation of one-agent-for-everything systems

### Slide 3: Project Objectives
- Build speaker-listener communication
- Compare learning approaches
- Add website visualization
- Add IMMAC and A2A paper-inspired builds

### Slide 4: Base Architecture
- Environment
- Speaker agent
- Listener agent
- Reward reranker
- Communication loop

### Slide 5: Learning Approaches
- Functional only
- Structural only
- Combined reranking

### Slide 6: Episode and Evaluation Logic
- What is one round
- What is one episode
- Accuracy per episode
- Final comparison metric

### Slide 7: Django Web System
- API endpoints
- Experiment runner
- Episode accuracy table
- Speaker/Listener demo outputs

### Slide 8: IMMAC Build (From Paper)
- Intrinsic score (surprise)
- Communication gate
- Attention router
- Why intrinsic communication helps

### Slide 9: A2A Build (From Paper)
- User -> Client Agent -> Remote Agent
- Agent Card, Skill, Task, Artifact
- JSON-RPC 2.0 sync/async flow
- Security controls (token/signature)

### Slide 10: Results and Observations
- Combined approach best in communication quality vs performance
- IMMAC improves communication efficiency
- A2A improves modularity and scalability

### Slide 11: Why This Project Matters
- Research relevance
- Real-world applicability
- Extensible architecture

### Slide 12: Conclusion and Future Work
- Key takeaway
- Next improvements

## 4. Build Each Slide in Order (Practical Path)

1. Add all titles first (all slides).
2. Add only 3 to 5 bullets per slide.
3. Insert diagrams/screenshots after text.
4. Add speaking notes last.
5. Keep one core message per slide.

## 5. Visual Rules (Keep It Clean)

1. One font family for headings, one for body.
2. Use one primary color and one accent color.
3. Avoid long paragraphs; use bullets.
4. Keep diagram style consistent.
5. Highlight only key words, not full sentences.

## 6. Time Split for Presentation (10-12 min)

1. Intro and problem: 1.5 min
2. Architecture and methods: 3 min
3. Website and implementation: 2 min
4. IMMAC and A2A additions: 2.5 min
5. Results, conclusion, Q&A: 2 min

## 7. Demo Order During Presentation

1. Run website and show episode table.
2. Show speaker/listener demo panel.
3. Run IMMAC demo in terminal.
4. Run A2A demo in terminal.
5. End with key conclusion slide.

## 8. Exact Commands for Live Demo

```bash
python manage.py runserver
python immac_demo.py
python a2a_demo.py
```

## 9. Backup Plan (If Demo Fails)

1. Keep screenshots of outputs in slides.
2. Keep one static JSON output snippet for episode results.
3. Keep one static terminal output for IMMAC and A2A.

## 10. Final Checklist

1. Slide flow is logical and sequence-wise.
2. Every architecture slide has a matching implementation slide.
3. Results slide has clear comparison points.
4. Final conclusion answers: What built, why needed, what proved.
5. Team member speaking order is fixed.
