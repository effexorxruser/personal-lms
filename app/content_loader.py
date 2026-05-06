from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import markdown

from app.content_pipeline import CONTENT_ROOT, CHECKPOINT_ROOT, TASK_ROOT, load_content_bundle


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
class TerminalPreset:
    label: str
    command: str


@dataclass
class TerminalConfig:
    enabled: bool
    presets: list[TerminalPreset]
    allow_manual_input: bool
    allowed_commands: list[str]


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
    terminal: TerminalConfig | None = None


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
    objectives: list[str]
    block: int
    checkpoint: str
    lesson_keys: list[str]
    lessons: list[LessonContent]


@dataclass
class CourseContent:
    slug: str
    title: str
    description: str
    version: str
    estimated_weeks: int
    status: str
    level: str
    duration_weeks: int | None
    tags: list[str]
    outcomes: list[str]
    prerequisites: list[str]
    module_order: list[str]
    modules: list[ModuleContent]


@dataclass
class ContentIndex:
    courses: dict[str, CourseContent]
    lessons: dict[str, LessonContent]
    lesson_order: list[str]
    tasks: dict[str, TaskContent]
    checkpoints: dict[str, CheckpointContent]


def _to_terminal_config(raw_terminal) -> TerminalConfig | None:
    if raw_terminal is None:
        return None

    return TerminalConfig(
        enabled=raw_terminal.enabled,
        presets=[
            TerminalPreset(label=preset.label, command=preset.command)
            for preset in raw_terminal.presets
        ],
        allow_manual_input=raw_terminal.allow_manual_input,
        allowed_commands=list(raw_terminal.allowed_commands),
    )


def load_content_index(
    *,
    content_root: Path = CONTENT_ROOT,
    task_root: Path = TASK_ROOT,
    checkpoint_root: Path = CHECKPOINT_ROOT,
) -> ContentIndex:
    bundle = load_content_bundle(
        content_root=content_root,
        task_root=task_root,
        checkpoint_root=checkpoint_root,
        raise_on_error=True,
    )

    tasks: dict[str, TaskContent] = {}
    checkpoints: dict[str, CheckpointContent] = {}
    lessons: dict[str, LessonContent] = {}
    courses: dict[str, CourseContent] = {}

    for task_slug, parsed_task in bundle.tasks_by_slug.items():
        schema = parsed_task.schema
        tasks[task_slug] = TaskContent(
            slug=schema.slug,
            title=schema.title,
            summary=schema.summary,
            instructions=schema.instructions,
            submission_type=schema.submission_type,
            definition_of_done=list(schema.definition_of_done),
            review_mode=schema.review_mode,
            hints=list(schema.hints),
            terminal=_to_terminal_config(schema.terminal),
        )

    for checkpoint_slug, parsed_checkpoint in bundle.checkpoints_by_slug.items():
        schema = parsed_checkpoint.schema
        checkpoints[checkpoint_slug] = CheckpointContent(
            slug=schema.slug,
            title=schema.title,
            summary=schema.summary,
            module_slug=schema.module_slug,
            description=schema.description,
            requirements=list(schema.requirements),
            definition_of_done=list(schema.definition_of_done),
            submission_type=schema.submission_type,
            portfolio_expectations=list(schema.portfolio_expectations),
            hints=list(schema.hints),
        )

    lesson_order: list[str] = []
    for lesson_key in bundle.lesson_order:
        parsed_lesson = bundle.lessons_by_key.get(lesson_key)
        if parsed_lesson is None:
            continue
        schema = parsed_lesson.schema
        lesson = LessonContent(
            key=schema.key,
            title=schema.title,
            summary=schema.summary,
            objectives=list(schema.objectives),
            checklist=list(schema.checklist),
            body_markdown=parsed_lesson.body_markdown,
            body_html=markdown.markdown(parsed_lesson.body_markdown),
            task_slug=schema.task_slug,
            module_slug=parsed_lesson.module_slug,
            course_slug=parsed_lesson.course_slug,
        )
        lessons[schema.key] = lesson
        lesson_order.append(schema.key)

    for parsed_course in bundle.courses:
        module_order: list[str] = list(parsed_course.schema.modules)
        modules: list[ModuleContent] = []
        for module_slug in module_order:
            parsed_module = parsed_course.modules_by_folder.get(module_slug)
            if parsed_module is None:
                continue
            module_schema = parsed_module.schema
            module_lessons: list[LessonContent] = []
            for lesson_key in module_schema.lessons:
                lesson = lessons.get(lesson_key)
                if lesson is not None:
                    module_lessons.append(lesson)
            modules.append(
                ModuleContent(
                    slug=module_schema.slug,
                    title=module_schema.title,
                    description=module_schema.description,
                    objectives=list(module_schema.objectives),
                    block=module_schema.block,
                    checkpoint=module_schema.checkpoint,
                    lesson_keys=list(module_schema.lessons),
                    lessons=module_lessons,
                )
            )

        course_schema = parsed_course.schema
        courses[course_schema.slug] = CourseContent(
            slug=course_schema.slug,
            title=course_schema.title,
            description=course_schema.description,
            version=course_schema.version,
            estimated_weeks=course_schema.effective_duration_weeks,
            status=course_schema.status,
            level=course_schema.level,
            duration_weeks=course_schema.duration_weeks,
            tags=list(course_schema.tags),
            outcomes=list(course_schema.outcomes),
            prerequisites=list(course_schema.prerequisites),
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
