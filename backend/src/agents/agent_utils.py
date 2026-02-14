"""Utility functions for agents."""

from datetime import datetime, timedelta
from typing import Dict, List, Any


class DateUtils:
    """Date and time utilities for agents."""

    @staticmethod
    def get_current_date() -> str:
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_date_n_days_ago(days: int) -> str:
        """Get date N days ago in YYYY-MM-DD format."""
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def get_one_year_ago() -> str:
        """Get date one year ago in YYYY-MM-DD format."""
        return DateUtils.get_date_n_days_ago(365)


class DataExtractor:
    """Utilities for extracting and formatting resume data for agents."""

    @staticmethod
    def format_work_experience_with_dates(experience_list: List[Dict]) -> List[Dict]:
        """Format work experience with prominent date ranges.

        Args:
            experience_list: List of work experience entries

        Returns:
            List of experience entries with formatted DATE_RANGE field
        """
        formatted = []
        for exp in experience_list:
            exp_copy = exp.copy()
            start = exp.get('start_date', 'Unknown')
            end = exp.get('end_date', 'Present')
            exp_copy['DATE_RANGE'] = f"{start} to {end}"
            formatted.append(exp_copy)
        return formatted

    @staticmethod
    def extract_career_progression(experience_list: List[Dict]) -> List[Dict]:
        """Extract simplified career progression from experience.

        Args:
            experience_list: List of work experience entries

        Returns:
            List of career progression entries
        """
        progression = []
        for exp in experience_list:
            progression.append({
                "role": exp.get("role"),
                "company": exp.get("company"),
                "duration": exp.get("duration"),
                "key_achievement": exp.get("highlights", [""])[0] if exp.get("highlights") else ""
            })
        return progression

    @staticmethod
    def extract_technical_experience(experience_list: List[Dict]) -> List[Dict]:
        """Extract technical work experience.

        Args:
            experience_list: List of work experience entries

        Returns:
            List of technical experience entries
        """
        return [
            exp for exp in experience_list
            if any(tech in str(exp).lower() for tech in ["engineer", "developer", "tech"])
        ]

    @staticmethod
    def extract_leadership_examples(experience_list: List[Dict]) -> List[List[str]]:
        """Extract leadership-related highlights from experience.

        Args:
            experience_list: List of work experience entries

        Returns:
            List of highlight lists that mention leadership
        """
        return [
            exp.get("highlights", [])
            for exp in experience_list
            if any(word in str(exp).lower() for word in ["led", "team", "managed"])
        ]

    @staticmethod
    def calculate_years_experience(experience_list: List[Dict]) -> str:
        """Calculate total years of experience.

        Args:
            experience_list: List of work experience entries

        Returns:
            String representation of years of experience
        """
        if not experience_list:
            return "N/A"

        try:
            # Get first and last year from duration strings
            first_year = int(experience_list[-1].get("duration", "").split("-")[0])
            last_year = int(experience_list[0].get("duration", "").split("-")[-1].strip().split()[0])
            return str(last_year - first_year)
        except:
            return "Multiple years"

    @staticmethod
    def get_background_context_note() -> str:
        """Get context note for background agent to prevent hallucinations."""
        return """WORK_EXPERIENCE_ONLY contains ONLY job titles and companies. DO NOT confuse work experience with specific projects. Each work experience entry is a ROLE at a COMPANY, NOT a project name.

CRITICAL: The 'achievements' field contains a LIST of separate features/tasks completed. These are INDIVIDUAL achievements, NOT parts of one named platform. DO NOT invent umbrella names like 'the X Platform' or 'the Y System'. Just describe what was done: 'I built dashboards', 'I developed a RAG system', etc."""


class PromptBuilder:
    """Builder for constructing agent prompts."""

    @staticmethod
    def build_prompt(
        system_prompt: str,
        data_section: str,
        context: str,
        message: str,
        response_instruction: str
    ) -> str:
        """Build a complete prompt from components.

        Args:
            system_prompt: System prompt with rules and guidelines
            data_section: Formatted data section
            context: Conversation context
            message: User message
            response_instruction: Response instruction

        Returns:
            Complete formatted prompt
        """
        return f"""System: {system_prompt}

{data_section}

Conversation Context:
{context}

Question: {message}

{response_instruction}"""
