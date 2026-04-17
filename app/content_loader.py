from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import markdown
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = PROJECT_ROOT / "content" / "courses"
TASK_ROOT = PROJECT_ROOT / "content" / "tasks"
CHECKPOINT_ROOT = PROJECT_ROOT / "content" / "checkpoints"


@dataclass
class LessonContent:
    key: str
    title: str
    summary: str
    objectives: list[str]
    checklist: list[str]
    body_markdown: str
    body_html: str
    task_slug: str | None
    module_slug: str
    course_slug: str


@dataclass
class TaskContent:
    slug: str
    title: str
    summary: str
    instructions: str
    submission_type: str
    definition_of_done: list[str]
    review_mode: str
    hints: list[str]


@dataclass
class CheckpointContent:
    slug: str
    title: str
    summary: str
    module_slug: str
    description: str
    requirements: list[str]
    definition_of_done: list[str]
    submission_type: str
    portfolio_expectations: list[str]
    hints: list[str]


@dataclass
class ModuleContent:
    slug: str
    title: str
    description: str
    lesson_keys: list[str]
    lessons: list[LessonContent]


@dataclass
class CourseContent:
    slug: str
    title: str
    description: str
    version: str
    estimated_weeks: int
    module_order: list[str]
    modules: list[ModuleContent]


@dataclass
class ContentIndex:
    courses: dict[str, CourseContent]
    lessons: dict[str, LessonContent]
    lesson_order: list[str]
    tasks: dict[str, TaskContent]
    checkpoints: dict[str, CheckpointContent]


def _parse_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file_handle:
        data = yaml.safe_load(file_handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {path}")
    return data


def _parse_front_matter(raw_text: str, path: Path) -> tuple[dict, str]:
    if not raw_text.startswith("---\n"):
        raise ValueError(f"Missing front matter in {path}")

    parts = raw_text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid front matter format in {path}")

    front_matter_text = parts[0].replace("---\n", "", 1)
    body_markdown = parts[1].strip()

    front_matter = yaml.safe_load(front_matter_text)
    if not isinstance(front_matter, dict):
        raise ValueError(f"Invalid front matter YAML in {path}")

    return front_matter, body_markdown


def _load_lesson(path: Path, module_slug: str, course_slug: str) -> LessonContent:
    raw_text = path.read_text(encoding="utf-8")
    front_matter, body_markdown = _parse_front_matter(raw_text, path)

    return LessonContent(
        key=str(front_matter["key"]),
        title=str(front_matter["title"]),
        summary=str(front_matter["summary"]),
        objectives=[str(item) for item in front_matter.get("objectives", [])],
        checklist=[str(item) for item in front_matter.get("checklist", [])],
        body_markdown=body_markdown,
        body_html=markdown.markdown(body_markdown),
        task_slug=(str(front_matter["task_slug"]) if front_matter.get("task_slug") else None),
        module_slug=module_slug,
        course_slug=course_slug,
    )


def _load_task(path: Path) -> TaskContent:
    task_data = _parse_yaml(path)
    return TaskContent(
        slug=str(task_data["slug"]),
        title=str(task_data["title"]),
        summary=str(task_data["summary"]),
        instructions=str(task_data["instructions"]).strip(),
        submission_type=str(task_data["submission_type"]),
        definition_of_done=[str(item) for item in task_data.get("definition_of_done", [])],
        review_mode=str(task_data.get("review_mode", "deterministic")),
        hints=[str(item) for item in task_data.get("hints", [])],
    )


def _load_checkpoint(path: Path) -> CheckpointContent:
    checkpoint_data = _parse_yaml(path)
    return CheckpointContent(
        slug=str(checkpoint_data["slug"]),
        title=str(checkpoint_data["title"]),
        summary=str(checkpoint_data["summary"]),
        module_slug=str(checkpoint_data["module_slug"]),
        description=str(checkpoint_data["description"]).strip(),
        requirements=[str(item) for item in checkpoint_data.get("requirements", [])],
        definition_of_done=[str(item) for item in checkpoint_data.get("definition_of_done", [])],
        submission_type=str(checkpoint_data["submission_type"]),
        portfolio_expectations=[str(item) for item in checkpoint_data.get("portfolio_expectations", [])],
        hints=[str(item) for item in checkpoint_data.get("hints", [])],
    )


def _load_module(course_path: Path, course_slug: str, module_slug: str) -> ModuleContent:
    module_path = course_path / "modules" / module_slug
    module_data = _parse_yaml(module_path / "module.yml")

    lesson_keys = [str(item) for item in module_data.get("lessons", [])]
    lessons: list[LessonContent] = []

    for lesson_key in lesson_keys:
        lesson_path = module_path / "lessons" / f"{lesson_key}.md"
        lessons.append(_load_lesson(lesson_path, module_slug=module_slug, course_slug=course_slug))

    return ModuleContent(
        slug=str(module_data.get("slug", module_slug)),
        title=str(module_data["title"]),
        description=str(module_data["description"]),
        lesson_keys=lesson_keys,
        lessons=lessons,
    )


def load_content_index() -> ContentIndex:
    courses: dict[str, CourseContent] = {}
    lessons: dict[str, LessonContent] = {}
    lesson_order: list[str] = []
    tasks: dict[str, TaskContent] = {}
    checkpoints: dict[str, CheckpointContent] = {}

    for task_path in sorted(TASK_ROOT.glob("*.yml")):
        task = _load_task(task_path)
        tasks[task.slug] = task

    for checkpoint_path in sorted(CHECKPOINT_ROOT.glob("*.yml")):
        checkpoint = _load_checkpoint(checkpoint_path)
        checkpoints[checkpoint.slug] = checkpoint

    for course_path in sorted(CONTENT_ROOT.glob("*/course.yml")):
        manifest_path = course_path
        course_dir = manifest_path.parent
        course_data = _parse_yaml(manifest_path)

        course_slug = str(course_data["slug"])
        module_order = [str(item) for item in course_data.get("modules", [])]

        modules: list[ModuleContent] = []
        for module_slug in module_order:
            module = _load_module(course_dir, course_slug=course_slug, module_slug=module_slug)
            modules.append(module)
            for lesson in module.lessons:
                lessons[lesson.key] = lesson
                lesson_order.append(lesson.key)

        courses[course_slug] = CourseContent(
            slug=course_slug,
            title=str(course_data["title"]),
            description=str(course_data["description"]),
            version=str(course_data.get("version", "0.0.0")),
            estimated_weeks=int(course_data.get("estimated_weeks", 0)),
            module_order=module_order,
            modules=modules,
        )

    return ContentIndex(
        courses=courses,
        lessons=lessons,
        lesson_order=lesson_order,
        tasks=tasks,
        checkpoints=checkpoints,
    )
