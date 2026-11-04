import json
from contextlib import contextmanager
from contextvars import ContextVar
from io import BytesIO
from pathlib import Path

from agents import Agent
from markitdown import MarkItDown
from omniagents import function_tool

from .models import Interest, Skill, StudentSkill

MAX_RESUME_BYTES = 10 * 1024 * 1024
_resume_text = ContextVar("resume_text", default="")


@contextmanager
def resume_context(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()
    if extension != ".docx":
        raise ValueError("Upload a Word document (.docx) resume.")
    if uploaded_file.size > MAX_RESUME_BYTES:
        raise ValueError("The resume must be 10 MB or smaller.")

    uploaded_file.seek(0)
    content = BytesIO(uploaded_file.read())
    result = MarkItDown().convert_stream(content, file_extension=extension)
    text = result.text_content.strip()
    if not text:
        raise ValueError("No readable text was found in the resume.")
    token = _resume_text.set(text)
    try:
        yield text
    finally:
        _resume_text.reset(token)


@function_tool
def read_resume() -> str:
    """Read the student's uploaded resume and return its text."""
    resume_text = _resume_text.get()
    if not resume_text:
        return "No resume was provided for this request."
    return resume_text


@function_tool
def get_profile_options() -> str:
    """Return the skills, skill levels, and interests available for student profiles."""
    skills = [
        {
            "id": str(skill.id),
            "name": skill.name,
            "levels": [
                {"value": value, "label": label}
                for value, label in StudentSkill.LEVELS
            ],
        }
        for skill in Skill.objects.order_by("name")
    ]

    interests = [
        {"id": str(interest.id), "name": interest.name}
        for interest in Interest.objects.order_by("name")
    ]

    return json.dumps({"skills": skills, "interests": interests})


PROFILE_ASSISTANT_INSTRUCTIONS = """
You help students complete their profiles using information they provide, such as
resume text or a description of their experience and projects.

Call read_resume to read the student's resume. Call get_profile_options to retrieve
the available skills, skill levels, and interests. Recommend only options returned
by that tool. Do not invent student experience or catalog options.

Return only valid JSON without markdown fences, using this format:
{"skills": [{"id": "catalog skill id", "level": 1}], "interests": ["catalog interest id"]}

Use only IDs returned by get_profile_options. Skill levels must be 1 (Beginner),
2 (Intermediate), or 3 (Advanced). Recommend only options supported by the
resume. Do not save or change profile data.
"""


def build_profile_assistant(resume_text=""):
    @function_tool
    def read_resume() -> str:
        """Read the student's uploaded resume and return its text."""
        return resume_text or "No resume was provided for this request."

    return Agent(
        name="Profile Assistant",
        instructions=PROFILE_ASSISTANT_INSTRUCTIONS,
        tools=[read_resume, get_profile_options],
        model="gpt-6-luna",
    )


profile_assistant = build_profile_assistant()
