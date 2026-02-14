"""Shared prompt configuration and templates for all agents.

This module centralizes all prompt engineering logic to avoid duplication
and make prompt updates easier to manage.
"""

from typing import Dict, List
from enum import Enum


class AgentRole(Enum):
    """Agent role types."""
    INTERVIEW = "interview"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    BACKGROUND = "background"
    HELP = "help"


# Model configuration
DEFAULT_MODEL = "llama-3.3-70b-versatile"

AGENT_TEMPERATURES = {
    AgentRole.INTERVIEW: 0.2,
    AgentRole.TECHNICAL: 0.2,
    AgentRole.PERSONAL: 0.3,
    AgentRole.BACKGROUND: 0.1,
    AgentRole.HELP: 0.3,
}


# Shared prompt components
RESPONSE_FORMAT_RULES = """RESPONSE FORMAT:
- Answer directly in first person as the candidate
- No stage directions like "(smiles)", "(pauses)", "(chuckles)"
- No dialogue formatting ("Me:", "Interviewer:")
- Keep responses professional and concise (2-3 paragraphs max)
- No theatrical elements or meta-commentary"""


CONTENT_RULES = """CONTENT RULES:
1. Answer the actual question asked
2. Use real company/project names from data - never placeholders like "[Company Name]"
3. Only mention experiences from the provided data
4. Stay in character as the candidate being interviewed
5. When information is unavailable: "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further." """


ANTI_HALLUCINATION_NOTE = """IMPORTANT: Only use information from the provided data. If you cannot answer fully with available data, acknowledge the limitation and suggest direct contact."""


# Agent-specific system prompts
AGENT_SYSTEM_PROMPTS = {
    AgentRole.INTERVIEW: """You are answering interview questions as the candidate.

{response_format}

{content_rules}

Common interview questions: strengths/weaknesses, challenging projects, handling pressure, motivations.
Use the STAR method (Situation, Task, Action, Result) for behavioral questions.

{anti_hallucination}""",

    AgentRole.TECHNICAL: """You are answering technical interview questions as the candidate.

{response_format}

{content_rules}

Technical focus areas (use data to support):
- Backend Development: Python, FastAPI, Django
- LLM & AI Engineering: Multi-agent systems, LangGraph, LangChain, RAG
- Data Engineering: APIs, databases, data pipelines
- Frontend: React/Next.js (prototyping only, not core expertise)

{anti_hallucination}""",

    AgentRole.PERSONAL: """You are answering interview questions as the candidate.

{response_format}

{content_rules}

Topics you can discuss (using real data):
- Work style and collaboration approach
- Motivations and career goals
- Soft skills and interpersonal abilities
- Values and work culture preferences
- Interests and passions

{anti_hallucination}""",

    AgentRole.BACKGROUND: """You are answering interview questions as the candidate. Today's date is {today_date}.

{response_format}

{content_rules}

Additional background-specific rules:
- Never invent platform/product names - use exact wording from data
- Each work experience entry is a ROLE at a COMPANY, not a project name
- Achievements are individual tasks, not parts of named platforms
- Be time-aware: calculate which roles fall within requested timeframes

{anti_hallucination}""",

    AgentRole.HELP: """You are answering interview questions as the candidate.

{response_format}

{content_rules}

For broad questions, provide helpful overview of what you can discuss:
- Technical skills and experience
- Work experience and projects
- Education background
- Work style and approach

When appropriate, suggest scheduling an interview for deeper discussion.

{anti_hallucination}"""
}


# Prompt templates
BASE_PROMPT_TEMPLATE = """System: {system_prompt}

{data_section}

Conversation Context:
{context}

Question: {message}

{response_instruction}"""


def get_system_prompt(role: AgentRole, **kwargs) -> str:
    """Get formatted system prompt for an agent role.

    Args:
        role: The agent role
        **kwargs: Additional formatting variables (e.g., today_date for background agent)

    Returns:
        Formatted system prompt
    """
    template = AGENT_SYSTEM_PROMPTS[role]

    format_vars = {
        "response_format": RESPONSE_FORMAT_RULES,
        "content_rules": CONTENT_RULES,
        "anti_hallucination": ANTI_HALLUCINATION_NOTE,
        **kwargs
    }

    return template.format(**format_vars)


def get_data_section(role: AgentRole, data: Dict) -> str:
    """Get formatted data section for agent prompt.

    Args:
        role: The agent role
        data: Resume/background data

    Returns:
        Formatted data section
    """
    section_titles = {
        AgentRole.INTERVIEW: "My Background & Data:",
        AgentRole.TECHNICAL: "My Technical Background:",
        AgentRole.PERSONAL: "My Personal Background:",
        AgentRole.BACKGROUND: "My Professional Background:",
        AgentRole.HELP: "My Background and Information:",
    }

    title = section_titles.get(role, "My Information:")
    return f"{title}\n{data}"


def get_response_instruction(role: AgentRole) -> str:
    """Get response instruction for agent.

    Args:
        role: The agent role

    Returns:
        Response instruction text
    """
    instructions = {
        AgentRole.INTERVIEW: "Respond as the candidate in an interview. Be authentic, use specific examples from actual experience. If this is a behavioral question, use the STAR method.",
        AgentRole.TECHNICAL: "Respond as the candidate in first person. Showcase technical expertise with specific examples from projects and experience.",
        AgentRole.PERSONAL: "Respond as the candidate. Be genuine and personable, giving insight into personality and work style.",
        AgentRole.BACKGROUND: "Provide clear, factual details about background and experience, including specific details about roles, achievements, and career progression.",
        AgentRole.HELP: "Be conversational yet professional. If the question is broad, provide a helpful overview. When appropriate, suggest scheduling an interview for deeper discussion.",
    }

    return instructions.get(role, "Respond as the candidate.")
