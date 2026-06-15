"""
Research Agent Base
===================

Base class for specialized research agents.

Each agent has:
- Domain expertise
- Research methods
- Communication protocol
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentMessage:
    """Message between agents."""
    sender: str
    receiver: str
    content: str
    message_type: str  # "discovery", "question", "challenge", "collaboration"
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentState:
    """Current state of an agent."""
    agent_id: str
    domain: str
    discoveries: int
    questions_asked: int
    challenges_issued: int
    collaborations: int
    active: bool = True


class ResearchAgent:
    """
    Base class for a specialized research agent.
    
    Each agent:
    - Has domain expertise
    - Can discover problems
    - Can generate theories
    - Can challenge other agents
    - Can collaborate
    """
    
    def __init__(self, agent_id: str, domain: str, config: Optional[Any] = None):
        self.agent_id = agent_id
        self.domain = domain
        self.config = config
        self.state = AgentState(
            agent_id=agent_id,
            domain=domain,
            discoveries=0,
            questions_asked=0,
            challenges_issued=0,
            collaborations=0,
        )
        self.inbox: List[AgentMessage] = []
        self.outbox: List[AgentMessage] = []
        self.knowledge: Dict[str, Any] = {}
        self.cycle_count = 0
    
    def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent."""
        self.inbox.append(message)
    
    def send_message(self, receiver: str, content: str,
                     message_type: str = "discovery") -> AgentMessage:
        """Send a message to another agent."""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type,
        )
        self.outbox.append(message)
        return message
    
    def process_inbox(self) -> List[AgentMessage]:
        """Process messages in inbox."""
        responses = []
        for message in self.inbox:
            response = self._handle_message(message)
            if response:
                responses.append(response)
        self.inbox.clear()
        return responses
    
    def _handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle an incoming message."""
        if message.message_type == "discovery":
            self.knowledge[message.content] = message.sender
            return None
        elif message.message_type == "question":
            self.state.questions_asked += 1
            return self.send_message(message.sender, f"Response to: {message.content}")
        elif message.message_type == "challenge":
            self.state.challenges_issued += 1
            return self.send_message(message.sender, f"Defense of: {message.content}")
        return None
    
    def research(self) -> Dict[str, Any]:
        """Perform research in this agent's domain."""
        self.cycle_count += 1
        return {"domain": self.domain, "cycle": self.cycle_count}
    
    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state
