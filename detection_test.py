#!/usr/bin/env python3
"""
Test script for the deception detection system in the Undercover game.
Tests deception detection components without LLM dependencies.
"""

from deception_detection import DeceptionDetector, update_deception_history, compute_observer_accuracy
from logs import print_header, print_subheader, print_kv
from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime
import json


class TestGameState(BaseModel):
    round_num: int = 0
    players: List[str] = []
    alive_players: List[str] = []
    roles: Dict[str, str] = {}
    phase: str = "describe"
    description_log: List[List[str]] = Field(default_factory=list)
    deception_history: Dict[str, List[Dict]] = Field(default_factory=dict)
    deception_scores: Dict[str, Dict[str, float]] = Field(default_factory=dict)


def generate_test_deception_summary(state: TestGameState) -> Dict:
    summary = {
        "total_statements_analyzed": 0,
        "deception_by_player": {},
        "final_deception_scores": state.deception_scores,
    }
    for player, history in state.deception_history.items():
        ps = {
            "total_statements": len(history),
            "self_reported_deceptions": 0,
            "peer_detected_deceptions": 0,
            "average_suspicion": 0.0,
        }
        total_s, sc = 0, 0
        for record in history:
            if record["self_analysis"].get("is_deceptive", 0) == 1:
                ps["self_reported_deceptions"] += 1
            for pa in record["other_analyses"].values():
                if pa.get("is_deceptive", 0) == 1:
                    ps["peer_detected_deceptions"] += 1
                total_s += pa.get("suspicion_level", 0.5)
                sc += 1
        if sc > 0:
            ps["average_suspicion"] = total_s / sc
        summary["deception_by_player"][player] = ps
        summary["total_statements_analyzed"] += len(history)
    return summary


def mock_llm_response(prompt):
    if "Alice" in prompt and "round" in prompt.lower():
        return {
            "chain_of_thought": "Alice gave a vague description that could apply to many things. Seems like she's avoiding specifics.",
            "is_deceptive": 1,
            "confidence": 0.8,
            "deception_type": "omission",
            "reasoning": "Description is suspiciously vague, likely hiding that her word is different",
            "suspicion_level": 0.85,
        }
    elif "Bob" in prompt and "sweet" in prompt.lower():
        return {
            "chain_of_thought": "Bob's description is specific and relatable. Seems consistent with the common word.",
            "is_deceptive": 0,
            "confidence": 0.7,
            "deception_type": "none",
            "reasoning": "Specific description aligns well with the expected word",
            "suspicion_level": 0.2,
        }
    else:
        return {
            "chain_of_thought": "Standard game description. No clear deceptive indicators.",
            "is_deceptive": 0,
            "confidence": 0.5,
            "deception_type": "none",
            "reasoning": "No clear deceptive indicators detected",
            "suspicion_level": 0.5,
        }


class MockLLM:
    def invoke(self, prompt, **kwargs):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        response = mock_llm_response(prompt)
        return MockResponse(json.dumps(response))


def test_deception_detection():
    print_header("Testing Deception Detection System — Undercover Game")

    state = TestGameState(
        round_num=1,
        players=["Alice", "Bob", "Selena", "Raj"],
        alive_players=["Alice", "Bob", "Selena", "Raj"],
        roles={"Alice": "Undercover", "Bob": "Civilian", "Selena": "Civilian", "Raj": "Civilian"},
        phase="describe",
        description_log=[["Bob", "It's a sweet, round fruit"]],
        deception_history={},
        deception_scores={},
    )

    detector = DeceptionDetector(MockLLM())

    print_subheader("Initial State")
    print_kv("Players", state.players)
    print_kv("Roles", state.roles)

    # Test 1: Alice (Undercover) makes a vague description
    print_subheader("Test 1: Alice (Undercover) describes")
    statement1 = "It's something you can eat, quite common"
    print_kv("Statement", statement1)

    self_analysis1 = detector.analyze_self_deception("Alice", statement1, "Describe phase, round 1")
    print_subheader("Self-Analysis")
    print_kv("Is Deceptive", self_analysis1['is_deceptive'], indent=2)
    print_kv("Deception Type", self_analysis1['deception_type'], indent=2)
    print_kv("Reasoning", self_analysis1['reasoning'], indent=2)

    other_analyses1 = {}
    for observer in ["Bob", "Selena", "Raj"]:
        analysis = detector.analyze_other_deception(observer, "Alice", statement1, "Describe phase, round 1")
        analysis["timestamp"] = datetime.utcnow().isoformat()
        other_analyses1[observer] = analysis
        print_subheader(f"{observer}'s Analysis")
        print_kv("Is Deceptive", analysis['is_deceptive'], indent=2)
        print_kv("Suspicion", analysis['suspicion_level'], indent=2)

    state = update_deception_history(state, "Alice", statement1, self_analysis1, other_analyses1)

    # Test 2: Bob (Civilian) describes specifically
    print_subheader("Test 2: Bob (Civilian) describes")
    statement2 = "It's sweet and crunchy, great for snacking"
    print_kv("Statement", statement2)

    self_analysis2 = detector.analyze_self_deception("Bob", statement2, "Describe phase, round 1")
    other_analyses2 = {}
    for observer in ["Alice", "Selena", "Raj"]:
        analysis = detector.analyze_other_deception(observer, "Bob", statement2, "Describe phase, round 1")
        analysis["timestamp"] = datetime.utcnow().isoformat()
        other_analyses2[observer] = analysis

    state = update_deception_history(state, "Bob", statement2, self_analysis2, other_analyses2)

    # Summary
    print_subheader("Deception Summary")
    summary = generate_test_deception_summary(state)
    print_kv("Total statements", summary['total_statements_analyzed'])
    for player, stats in summary['deception_by_player'].items():
        print_subheader(f"{player} ({state.roles[player]})")
        print_kv("Statements", stats['total_statements'], indent=2)
        print_kv("Self-reported deceptions", stats['self_reported_deceptions'], indent=2)
        print_kv("Peer-detected deceptions", stats['peer_detected_deceptions'], indent=2)
        print_kv("Avg suspicion", f"{stats['average_suspicion']:.2f}", indent=2)

    print_subheader("Scores (observer → target)")
    for observer, scores in state.deception_scores.items():
        score_str = ", ".join([f"{t}={s:.2f}" for t, s in scores.items()])
        print_kv(observer, score_str, indent=2)

    accuracy = compute_observer_accuracy(state)
    print_subheader("Observer Accuracy")
    for obs, stat in accuracy.items():
        print_kv(obs, f"Acc={stat.get('accuracy',0):.2f} P={stat.get('precision',0):.2f} R={stat.get('recall',0):.2f}", indent=2)

    print_subheader("Test Complete!")


if __name__ == "__main__":
    test_deception_detection()
