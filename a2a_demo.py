"""A2A architecture demo runner.

Run:
  python a2a_demo.py
"""

from pprint import pprint

from a2a_architecture import ClientAgent, RemoteAgent


def summarize_research(payload):
    text = payload.get("text", "")
    topic = payload.get("topic", "unknown")
    return {
        "topic": topic,
        "summary": text[:200] + ("..." if len(text) > 200 else ""),
        "length": len(text),
    }


def calculate_metrics(payload):
    values = payload.get("values", [])
    if not values:
        return {"count": 0, "mean": 0}
    mean = sum(values) / len(values)
    return {"count": len(values), "mean": round(mean, 4), "min": min(values), "max": max(values)}


def main():
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

    print("\n=== A2A Sync Flow ===")
    sync_result = client.run_sync(
        user_intent="please summarize this topic",
        payload={
            "topic": "Agent-to-Agent Architecture",
            "text": "A2A is a modular architecture where specialized agents collaborate over a protocol. "
            "It uses metadata cards, task routing, and secure communication channels. "
            "The client agent discovers server skills and routes work to remote agents.",
        },
        remote_agent=remote,
    )
    pprint(sync_result)

    print("\n=== A2A Async Flow (SSE-like events) ===")
    async_result = client.run_async(
        user_intent="run metrics skill",
        payload={"values": [0.62, 0.74, 0.71, 0.8, 0.77]},
        remote_agent=remote,
    )
    pprint(async_result)


if __name__ == "__main__":
    main()
