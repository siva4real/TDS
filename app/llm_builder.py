"""LLM-assisted generation of project scaffolds."""

from __future__ import annotations

import json
from typing import Dict, List

from openai import OpenAI

from app.config import settings
from app.logging import get_logger


logger = get_logger(__name__)


class LLMBuilder:
    """Coordinate prompts to produce structured project plans and files."""

    def __init__(self, api_key: str | None = None) -> None:
        self.client = OpenAI(api_key=api_key)
        if settings.openai_api_base:
            self.client.base_url = settings.openai_api_base

    def generate_project(self, build_request: Dict, attachments: List[Dict]) -> Dict:
        system_prompt = "You are a senior full-stack engineer who produces clear project scaffolds."
        user_prompt = json.dumps(
            {
                "brief": build_request["brief"],
                "checks": build_request.get("checks", []),
                "round": build_request.get("round"),
                "attachments": attachments,
            },
            indent=2,
        )
        logger.info("Calling LLM for project blueprint")
        response = self.client.responses.create(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            modalities=["text"],
        )

        content = response.output[0].content[0].text
        logger.info("LLM generation completed")
        return json.loads(content)

