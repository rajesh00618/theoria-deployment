"""
Ollama LLM Client: Connects THEORIA to local LLMs via Ollama API.

Uses gemma3:4b for hypothesis generation and scientific reasoning.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


class OllamaClient:
    """HTTP client for Ollama local LLM inference."""

    def __init__(self, model: str = "gemma3:4b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system: str = "", temperature: float = 0.7,
                 max_tokens: int = 1024) -> str:
        """Send a generate request to Ollama."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            raise ConnectionError(f"Ollama connection failed: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                return any(self.model in m for m in models)
        except Exception:
            return False


class LLMDriver:
    """
    High-level LLM interface for THEORIA hypothesis generation.

    Wraps OllamaClient with scientific prompt templates.
    """

    SYSTEM_PROMPT = (
        "You are a brilliant theoretical scientist and researcher. "
        "You generate novel, testable scientific hypotheses. "
        "You think deeply about causal mechanisms, cross-domain connections, "
        "and unconventional explanations. Always be specific and precise."
    )

    def __init__(self, model: str = "gemma3:4b"):
        self.client = OllamaClient(model=model)
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        if self._available is None:
            self._available = self.client.is_available()
        return self._available

    def generate_hypotheses(self, concept: str, domain: str,
                            existing_knowledge: List[str],
                            n_hypotheses: int = 5) -> List[Dict[str, Any]]:
        """
        Ask the LLM to generate novel hypotheses about a concept.

        Returns list of dicts with keys: description, mechanism, testable_predictions,
        confidence, novelty_reason.
        """
        knowledge_block = "\n".join(f"- {k}" for k in existing_knowledge[:10]) if existing_knowledge else "(none yet)"

        prompt = (
            f"Concept: {concept}\n"
            f"Domain: {domain}\n"
            f"Known facts:\n{knowledge_block}\n\n"
            f"Generate exactly {n_hypotheses} NOVEL, TESTABLE scientific hypotheses "
            f"about this concept. For each hypothesis, provide:\n"
            f"1. A clear one-sentence statement\n"
            f"2. The proposed causal mechanism\n"
            f"3. Two testable predictions\n"
            f"4. A confidence score (0.0-1.0)\n"
            f"5. Why this hypothesis is novel or unexpected\n\n"
            f"Respond in this exact JSON format (a list of objects):\n"
            f'[\n  {{"description": "...", "mechanism": "...", '
            f'"testable_predictions": ["...", "..."], '
            f'"confidence": 0.X, "novelty_reason": "..."}}\n]\n'
        )

        raw = self.client.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=2048,
        )

        return self._parse_hypotheses(raw, concept, domain)

    def explain_phenomenon(self, concept: str, observations: List[str],
                           domain: str) -> Dict[str, Any]:
        """Ask LLM to explain a phenomenon."""
        obs_block = "\n".join(f"- {o}" for o in observations[:8])

        prompt = (
            f"Concept: {concept}\n"
            f"Domain: {domain}\n"
            f"Observations:\n{obs_block}\n\n"
            f"Provide a deep scientific explanation for these observations. "
            f"Include: mechanism, key relationships, and what experiments would "
            f"definitively confirm or refute your explanation.\n\n"
            f"Respond in JSON:\n"
            f'{{"explanation": "...", "mechanism": "...", '
            f'"key_relationships": ["..."], "definitive_experiments": ["..."]}}\n'
        )

        raw = self.client.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500,
        )

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {"explanation": raw, "mechanism": "unparsed", "key_relationships": [], "definitive_experiments": []}

    def critique_hypothesis(self, hypothesis: str, domain: str) -> Dict[str, Any]:
        """Ask LLM to critically evaluate a hypothesis."""
        prompt = (
            f"Hypothesis: {hypothesis}\n"
            f"Domain: {domain}\n\n"
            f"Critically evaluate this hypothesis. Consider: logical coherence, "
            f"evidence requirements, potential flaws, competing explanations, "
            f"and what would make it stronger or weaker.\n\n"
            f"Respond in JSON:\n"
            f'{{"assessment": "strong|moderate|weak", '
            f'"logical_coherence": 0.X, "evidence_quality": 0.X, '
            f'"strengths": ["..."], "weaknesses": ["..."], '
            f'"suggested_improvements": ["..."]}}\n'
        )

        raw = self.client.generate(
            prompt=prompt,
            system=self.SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=1024,
        )

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {"assessment": "unparsed", "logical_coherence": 0.5,
                    "evidence_quality": 0.5, "strengths": [], "weaknesses": [],
                    "suggested_improvements": []}

    def _parse_hypotheses(self, raw: str, concept: str, domain: str) -> List[Dict[str, Any]]:
        """Parse LLM JSON output into hypothesis list."""
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]

            start = cleaned.find("[")
            end = cleaned.rfind("]") + 1
            if start >= 0 and end > start:
                cleaned = cleaned[start:end]

            data = json.loads(cleaned)
            if isinstance(data, list):
                return data[:10]
        except (json.JSONDecodeError, IndexError):
            pass

        # Fallback: wrap raw text as single hypothesis
        return [{
            "description": raw[:500] if raw else f"LLM hypothesis about {concept}",
            "mechanism": "proposed by LLM",
            "testable_predictions": [],
            "confidence": 0.5,
            "novelty_reason": "generated by local LLM",
        }]
