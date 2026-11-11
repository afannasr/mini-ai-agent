import os
import unittest

import agent as agent_module
from agent import Agent


class AgentTests(unittest.TestCase):
    def setUp(self):
        agent_module.NOTES_FILE = "test_notes.json"
        self.agent = Agent()

    def tearDown(self):
        if os.path.exists("test_notes.json"):
            os.remove("test_notes.json")

    def test_calculator(self):
        self.assertIn("= 14", self.agent.run("calculate 2 + 3 * 4")[0])

    def test_calculator_blocks_code(self):
        self.assertIn("Tool error", self.agent.run("calculate __import__('os')")[0])

    def test_division_by_zero_is_handled(self):
        self.assertIn("Tool error", self.agent.run("calculate 5 / 0")[0])

    def test_unit_converter(self):
        self.assertIn("3.107", self.agent.run("convert 5 km to miles")[0])

    def test_two_steps_in_one_goal(self):
        results = self.agent.run("convert 100 c to f then calculate 2 + 2")
        self.assertEqual(len(results), 2)
        self.assertIn("212", results[0])
        self.assertIn("= 4", results[1])

    def test_notes_save_and_show(self):
        self.agent.run("note: learn git")
        self.assertIn("learn git", self.agent.run("show my notes")[0])

    def test_unknown_goal(self):
        self.assertIn("don't have a tool", self.agent.run("sing a song")[0])

    def test_memory_records_steps(self):
        self.agent.run("what time is it")
        self.assertEqual(self.agent.memory[0]["tool"], "time")


if __name__ == "__main__":
    unittest.main()
      
