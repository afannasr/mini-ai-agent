"""Mini AI Agent - a tiny agent that plans, picks a tool, acts and remembers.

This is a RULE-BASED agent (no LLM and no API key needed). It teaches the core
agent loop used in Agentic AI:

    goal -> THINK (choose a tool) -> ACT (run the tool) -> OBSERVE (read result)

Skills shown: OOP, tool/registry design, the agent loop, regex, safe parsing
with `ast`, memory, JSON storage, error handling.
"""
import ast
import json
import operator
import os
import re
from datetime import datetime

NOTES_FILE = "notes.json"


# ---------------------------------------------------------------- tools
class Tool:
    """A tool has a name, a description and a function to run."""

    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, text):
        return self.func(text)


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    """Safely evaluate a math expression tree (never uses eval())."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported math expression.")


def calculator(text):
    expression = re.sub(r"[^0-9+\-*/().^ ]", "", text).replace("^", "**")
    if not expression.strip():
        raise ValueError("I could not find a math expression.")
    result = _eval_node(ast.parse(expression.strip(), mode="eval").body)
    return f"{expression.strip()} = {round(result, 4)}"


CONVERSIONS = {
    ("km", "miles"): lambda v: v * 0.621371,
    ("miles", "km"): lambda v: v / 0.621371,
    ("kg", "lb"): lambda v: v * 2.20462,
    ("lb", "kg"): lambda v: v / 2.20462,
    ("c", "f"): lambda v: v * 9 / 5 + 32,
    ("f", "c"): lambda v: (v - 32) * 5 / 9,
}


def unit_converter(text):
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([a-z]+)\s*(?:to|in)\s*([a-z]+)", text.lower())
    if not match:
        raise ValueError("Use the form: convert 5 km to miles")
    value, src, dst = float(match.group(1)), match.group(2), match.group(3)
    src = {"mile": "miles", "celsius": "c", "fahrenheit": "f", "pounds": "lb"}.get(src, src)
    dst = {"mile": "miles", "celsius": "c", "fahrenheit": "f", "pounds": "lb"}.get(dst, dst)
    if (src, dst) not in CONVERSIONS:
        raise ValueError(f"I can't convert {src} to {dst} yet.")
    return f"{value:g} {src} = {round(CONVERSIONS[(src, dst)](value), 3)} {dst}"


def current_time(_text):
    return datetime.now().strftime("It is %A, %d %B %Y, %H:%M.")


def notes_tool(text):
    notes = []
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
    lowered = text.lower()
    if "show" in lowered or "list" in lowered or "read" in lowered:
        if not notes:
            return "You have no notes yet."
        return "Your notes: " + " | ".join(f"{i}. {n}" for i, n in enumerate(notes, 1))
    content = re.sub(r"^(note|remember|save note)[: ]*", "", text.strip(), flags=re.I)
    if not content:
        raise ValueError("Tell me what to note, e.g. note: buy milk")
    notes.append(content)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2)
    return f"Saved note #{len(notes)}: {content}"


# ---------------------------------------------------------------- agent
class Agent:
    """Plans which tool to use, runs it, and keeps a memory of each step."""

    def __init__(self, max_steps=5):
        self.max_steps = max_steps
        self.memory = []  # list of dicts: goal, tool, observation
        self.tools = {}
        for tool in (
            Tool("unit_converter", "Convert units (km, miles, kg, lb, c, f)", unit_converter),
            Tool("calculator", "Do math like 12 * (3 + 4)", calculator),
            Tool("time", "Tell the current date and time", current_time),
            Tool("notes", "Save or show notes", notes_tool),
        ):
            self.tools[tool.name] = tool

    def think(self, goal):
        """THINK: choose a tool by reading the goal. Returns a tool name or None."""
        text = goal.lower()
        if re.search(r"\bconvert\b|\d\s*[a-z]+\s+(to|in)\s+[a-z]+", text):
            return "unit_converter"
        if re.search(r"\b(time|date|today)\b", text):
            return "time"
        if re.search(r"\b(notes?|remember)\b", text):
            return "notes"
        if re.search(r"\d\s*[-+*/^]\s*\d|calculate|what is \d", text):
            return "calculator"
        return None

    def act(self, tool_name, goal):
        """ACT: run the chosen tool and OBSERVE the result."""
        try:
            return self.tools[tool_name].run(goal)
        except (ValueError, ZeroDivisionError, SyntaxError) as error:
            return f"Tool error: {error}"

    def run(self, goal):
        """Handle one goal. Several steps can be joined with ' then '."""
        steps = [s.strip() for s in re.split(r"\bthen\b|;", goal, flags=re.I) if s.strip()]
        results = []
        for step in steps[: self.max_steps]:
            tool_name = self.think(step)
            if tool_name is None:
                observation = "Sorry, I don't have a tool for that. Type 'tools' to see what I can do."
            else:
                observation = self.act(tool_name, step)
            self.memory.append({"goal": step, "tool": tool_name, "observation": observation})
            results.append(observation)
        return results

    def describe_tools(self):
        return [f"- {t.name}: {t.description}" for t in self.tools.values()]

    def show_memory(self):
        if not self.memory:
            return ["Memory is empty."]
        return [f"{i}. [{m['tool']}] {m['goal']} -> {m['observation']}" for i, m in enumerate(self.memory, 1)]


def main():
    agent = Agent()
    print("Mini AI Agent. Type 'tools', 'memory' or 'quit'.")
    print("Try: convert 5 km to miles then calculate 2 + 3 * 4")
    while True:
        goal = input("\nYou: ").strip()
        if goal.lower() in {"quit", "exit"}:
            print("Bye!")
            break
        if goal.lower() == "tools":
            print("\n".join(agent.describe_tools()))
        elif goal.lower() == "memory":
            print("\n".join(agent.show_memory()))
        elif goal:
            for line in agent.run(goal):
                print("Agent:", line)


if __name__ == "__main__":
    main()
                 
