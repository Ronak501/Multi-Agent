"""Quick IMMAC-inspired demo.

Run:
  python immac_demo.py
"""

from immac_extension import (
    AttentionRouter,
    CommunicationGate,
    IntrinsicScorer,
    build_intrinsic_messages,
)


def main():
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

    print("\nIMMAC-style communication round")
    print("=" * 50)
    print(f"Total observations: {len(observations)}")
    print(f"Messages sent after intrinsic gating: {len(messages)}")

    if not ranked:
        print("No messages passed the intrinsic gate.")
        return

    print("\nTop messages after attention routing:")
    for msg, weight in ranked:
        print(
            f"- Agent {msg.sender_id} | intrinsic={msg.intrinsic_value:.3f} "
            f"| attention_weight={weight:.3f} | obs={msg.observation}"
        )


if __name__ == "__main__":
    main()
