# START HERE

If you are new to this project, follow this exact order.

## 1) Run the website

```bash
python manage.py runserver
```

Open:
- http://127.0.0.1:8000/

## 2) Use the website in this sequence

1. Start Here section
   - Click: Step 1: Run Experiments
2. Speaker and Listener demo
   - Click: Step 2: Speaker/Listener
3. Advanced IMMAC demo
   - Click: Step 3: IMMAC Demo
4. Advanced A2A demo
   - Click: Step 4: A2A Demo

If you want everything at once:
- Click: Run All Demos

## 3) What each demo means

- Experiment Comparison:
  compares Functional, Structural, and Combined approaches.
- Speaker/Listener Demo:
  shows one complete communication round.
- IMMAC Demo:
  shows intrinsic surprise-based communication logic.
- A2A Demo:
  shows Agent-to-Agent architecture flow with JSON-RPC style structure.

## 4) Optional terminal demos

```bash
python main.py --auto
python immac_demo.py
python a2a_demo.py
```

## 5) If something fails

1. Run migrations:
```bash
python manage.py migrate
```
2. Check project:
```bash
python manage.py check
```
