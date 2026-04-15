"""A2A (Agent-to-Agent) reference architecture for this project.

Implements a compact, practical version of the paper concepts:
- User -> Client Agent -> Remote Agent flow
- Agent Cards, Skills, Tasks, Messages, Artifacts
- JSON-RPC 2.0 style request/response envelopes
- Simple security checks (token + signature placeholder)
- Sync and async task execution paths
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import hashlib
import json
import uuid


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass
class Skill:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCard:
    agent_id: str
    name: str
    description: str
    skills: List[Skill]
    auth_type: str = "token"
    endpoint: str = "local://remote-agent"
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "skills": [s.__dict__ for s in self.skills],
            "auth_type": self.auth_type,
            "endpoint": self.endpoint,
            "version": self.version,
        }


@dataclass
class Task:
    task_id: str
    skill: str
    payload: Dict[str, Any]
    created_at: str = field(default_factory=_utc_now)


@dataclass
class Message:
    role: str
    content: Dict[str, Any]
    timestamp: str = field(default_factory=_utc_now)


@dataclass
class Artifact:
    artifact_id: str
    task_id: str
    output: Dict[str, Any]
    status: str
    created_at: str = field(default_factory=_utc_now)


class A2AProtocol:
    """Helpers for JSON-RPC 2.0 envelopes."""

    JSONRPC_VERSION = "2.0"

    @classmethod
    def request(cls, method: str, params: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": cls.JSONRPC_VERSION,
            "id": request_id or str(uuid.uuid4()),
            "method": method,
            "params": params,
        }

    @classmethod
    def response(cls, request_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": cls.JSONRPC_VERSION,
            "id": request_id,
            "result": result,
        }

    @classmethod
    def error(cls, request_id: str, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": cls.JSONRPC_VERSION,
            "id": request_id,
            "error": {"code": code, "message": message},
        }


class SecurityManager:
    """Minimal security guardrail hooks for A2A requests."""

    def __init__(self, shared_token: str):
        self.shared_token = shared_token

    def verify_token(self, token: str) -> bool:
        return token == self.shared_token

    @staticmethod
    def sign_payload(payload: Dict[str, Any], secret: str) -> str:
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256((canonical + secret).encode("utf-8")).hexdigest()

    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str, secret: str) -> bool:
        expected = SecurityManager.sign_payload(payload, secret)
        return expected == signature


class RemoteAgent:
    """Server-side agent exposing skills and task execution."""

    def __init__(self, name: str, description: str, token: str):
        self.agent_id = f"remote-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.security = SecurityManager(shared_token=token)
        self._skill_handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._skills: List[Skill] = []

    def register_skill(
        self,
        name: str,
        description: str,
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._skill_handlers[name] = handler
        self._skills.append(
            Skill(name=name, description=description, input_schema=input_schema or {})
        )

    def publish_agent_card(self) -> AgentCard:
        return AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            skills=list(self._skills),
        )

    def execute_sync(
        self,
        task: Task,
        token: str,
        signature: Optional[str] = None,
        signing_secret: Optional[str] = None,
    ) -> Artifact:
        if not self.security.verify_token(token):
            return Artifact(
                artifact_id=str(uuid.uuid4()),
                task_id=task.task_id,
                output={"error": "Unauthorized token"},
                status="failed",
            )

        if signature and signing_secret:
            if not self.security.verify_signature(task.payload, signature, signing_secret):
                return Artifact(
                    artifact_id=str(uuid.uuid4()),
                    task_id=task.task_id,
                    output={"error": "Invalid signature"},
                    status="failed",
                )

        handler = self._skill_handlers.get(task.skill)
        if not handler:
            return Artifact(
                artifact_id=str(uuid.uuid4()),
                task_id=task.task_id,
                output={"error": f"Unknown skill: {task.skill}"},
                status="failed",
            )

        try:
            result = handler(task.payload)
            return Artifact(
                artifact_id=str(uuid.uuid4()),
                task_id=task.task_id,
                output=result,
                status="success",
            )
        except Exception as exc:
            return Artifact(
                artifact_id=str(uuid.uuid4()),
                task_id=task.task_id,
                output={"error": str(exc)},
                status="failed",
            )

    def execute_async(
        self,
        task: Task,
        token: str,
        signature: Optional[str] = None,
        signing_secret: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return SSE-like lifecycle events for async workflows."""
        events: List[Dict[str, Any]] = []
        events.append({"event": "task.created", "task_id": task.task_id, "timestamp": _utc_now()})
        events.append({"event": "task.running", "task_id": task.task_id, "timestamp": _utc_now()})

        artifact = self.execute_sync(task, token=token, signature=signature, signing_secret=signing_secret)
        final_event = {
            "event": "task.completed" if artifact.status == "success" else "task.failed",
            "task_id": task.task_id,
            "artifact": {
                "artifact_id": artifact.artifact_id,
                "status": artifact.status,
                "output": artifact.output,
            },
            "timestamp": _utc_now(),
        }
        events.append(final_event)
        return events


class ClientAgent:
    """Orchestrator that routes user tasks to the right remote agent skill."""

    def __init__(self, token: str, signing_secret: str = "a2a-secret"):
        self.token = token
        self.signing_secret = signing_secret

    @staticmethod
    def _pick_skill(agent_card: AgentCard, user_intent: str) -> Optional[str]:
        intent = user_intent.lower()
        for skill in agent_card.skills:
            if skill.name.lower() in intent:
                return skill.name
        return agent_card.skills[0].name if agent_card.skills else None

    def create_task(self, user_intent: str, payload: Dict[str, Any], skill: str) -> Task:
        return Task(task_id=f"task-{uuid.uuid4().hex[:10]}", skill=skill, payload={"intent": user_intent, **payload})

    def run_sync(self, user_intent: str, payload: Dict[str, Any], remote_agent: RemoteAgent) -> Dict[str, Any]:
        card = remote_agent.publish_agent_card()
        skill = self._pick_skill(card, user_intent)
        if not skill:
            return {"status": "failed", "error": "No available skills"}

        task = self.create_task(user_intent=user_intent, payload=payload, skill=skill)
        signature = SecurityManager.sign_payload(task.payload, self.signing_secret)

        rpc_request = A2AProtocol.request(
            method="task.execute",
            params={
                "task": task.__dict__,
                "token": self.token,
                "signature": signature,
            },
        )

        artifact = remote_agent.execute_sync(
            task,
            token=self.token,
            signature=signature,
            signing_secret=self.signing_secret,
        )

        if artifact.status == "success":
            rpc_response = A2AProtocol.response(
                request_id=rpc_request["id"],
                result={"artifact": artifact.__dict__},
            )
        else:
            rpc_response = A2AProtocol.error(
                request_id=rpc_request["id"],
                code=401 if "Unauthorized" in str(artifact.output) else 500,
                message=str(artifact.output),
            )

        return {
            "agent_card": card.to_dict(),
            "rpc_request": rpc_request,
            "rpc_response": rpc_response,
        }

    def run_async(self, user_intent: str, payload: Dict[str, Any], remote_agent: RemoteAgent) -> Dict[str, Any]:
        card = remote_agent.publish_agent_card()
        skill = self._pick_skill(card, user_intent)
        if not skill:
            return {"status": "failed", "error": "No available skills"}

        task = self.create_task(user_intent=user_intent, payload=payload, skill=skill)
        signature = SecurityManager.sign_payload(task.payload, self.signing_secret)
        events = remote_agent.execute_async(
            task,
            token=self.token,
            signature=signature,
            signing_secret=self.signing_secret,
        )

        return {
            "agent_card": card.to_dict(),
            "task": task.__dict__,
            "events": events,
        }
