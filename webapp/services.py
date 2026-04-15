import random
from typing import Any, Dict, List

from a2a_architecture import ClientAgent, RemoteAgent
from agents import ImageEnvironment, ListenerAgent, RewardLearningRanker, SpeakerAgent
from communication_system import CommunicationSystem
from immac_extension import AttentionRouter, CommunicationGate, IntrinsicScorer, build_intrinsic_messages


def _image_to_dict(image) -> Dict[str, Any]:
    return {
        "id": image.id,
        "color": image.color,
        "shape": image.shape,
        "size": image.size,
        "position": image.position,
    }


def run_experiment_summary(episodes: int = 30, length: int = 10) -> Dict[str, Any]:
    env = ImageEnvironment(dataset_size=50)
    system = CommunicationSystem(env, seed=42)
    return system.run_all_experiments_quiet(num_episodes=episodes, episode_length=length)


def run_demo_round() -> Dict[str, Any]:
    env = ImageEnvironment(dataset_size=20)
    speaker = SpeakerAgent()
    listener = ListenerAgent()
    ranker = RewardLearningRanker()

    target_id = random.randint(0, len(env.dataset) - 1)
    candidates = env.get_candidate_set(target_id)
    target = env.current_target

    descriptions = speaker.generate_multiple_descriptions(target)
    best_description = ranker.rank_descriptions(descriptions, candidates, target, listener)
    selected, confidence = listener.select_image(best_description, candidates)
    success = listener.evaluate_match(selected, target)

    return {
        "speaker_agent": {
            "generated_descriptions": descriptions,
            "chosen_description": best_description,
        },
        "listener_agent": {
            "selected_image": _image_to_dict(selected),
            "confidence": round(confidence, 4),
            "is_correct": bool(success > 0.5),
        },
        "target": _image_to_dict(target),
        "candidates": [_image_to_dict(img) for img in candidates],
        "descriptions": descriptions,
        "best_description": best_description,
        "selected": _image_to_dict(selected),
        "confidence": round(confidence, 4),
        "success": bool(success > 0.5),
    }


def run_immac_demo() -> Dict[str, Any]:
    scorer = IntrinsicScorer()
    gate = CommunicationGate(threshold=0.28)
    router = AttentionRouter()

    observations = [
        {"color": "red", "shape": "circle", "position": "top-left"},
        {"color": "red", "shape": "circle", "position": "top-left"},
        {"color": "yellow", "shape": "star", "position": "center"},
        {"color": "blue", "shape": "triangle", "position": "bottom-right"},
    ]

    messages = build_intrinsic_messages(observations, scorer, gate)
    ranked = router.prioritize(messages, top_k=2)

    return {
        "observations": observations,
        "gate_threshold": gate.threshold,
        "messages_sent": [
            {
                "sender_id": msg.sender_id,
                "observation": msg.observation,
                "intrinsic_value": round(msg.intrinsic_value, 4),
            }
            for msg in messages
        ],
        "top_attention": [
            {
                "sender_id": msg.sender_id,
                "intrinsic_value": round(msg.intrinsic_value, 4),
                "attention_weight": round(weight, 4),
                "observation": msg.observation,
            }
            for msg, weight in ranked
        ],
    }


def run_a2a_demo() -> Dict[str, Any]:
    def summarize_research(payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        topic = payload.get("topic", "unknown")
        return {
            "topic": topic,
            "summary": text[:200] + ("..." if len(text) > 200 else ""),
            "length": len(text),
        }

    def calculate_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload.get("values", [])
        if not values:
            return {"count": 0, "mean": 0}
        mean = sum(values) / len(values)
        return {
            "count": len(values),
            "mean": round(mean, 4),
            "min": min(values),
            "max": max(values),
        }

    shared_token = "a2a-token"
    client = ClientAgent(token=shared_token, signing_secret="paper-demo-secret")

    remote = RemoteAgent(
        name="Research Agent Server",
        description="Remote agent providing analysis skills",
        token=shared_token,
    )

    remote.register_skill(
        name="summarize",
        description="Summarize research text",
        handler=summarize_research,
        input_schema={"text": "string", "topic": "string"},
    )
    remote.register_skill(
        name="metrics",
        description="Compute basic numeric metrics",
        handler=calculate_metrics,
        input_schema={"values": "number[]"},
    )

    sync_intent = "Please summarize this research topic for me"
    sync_result = client.run_sync(
        user_intent=sync_intent,
        payload={
            "topic": "Agent-to-Agent Architecture",
            "text": (
                "A2A is a modular architecture where specialized agents collaborate over "
                "a protocol. It uses metadata cards, task routing, and secure "
                "communication channels."
            ),
        },
        remote_agent=remote,
    )
    sync_result["user_intent"] = sync_intent

    async_intent = "Calculate metrics for the accuracy values"
    async_result = client.run_async(
        user_intent=async_intent,
        payload={"values": [0.62, 0.74, 0.71, 0.8, 0.77]},
        remote_agent=remote,
    )
    async_result["user_intent"] = async_intent

    return {
        "sync_flow": sync_result,
        "async_flow": async_result,
    }


def default_process_steps() -> List[str]:
    return [
        "Build an image dataset using color, shape, size, and position attributes.",
        "Pick one target image with distractor candidates.",
        "Speaker agent generates natural-language descriptions.",
        "Reward ranker picks the strongest description for task success.",
        "Listener agent selects the matching candidate.",
        "Reward feedback updates communication behavior over episodes.",
    ]
