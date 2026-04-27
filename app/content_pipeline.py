from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = PROJECT_ROOT / "content" / "courses"
TASK_ROOT = PROJECT_ROOT / "content" / "tasks"
CHECKPOINT_ROOT = PROJECT_ROOT / "content" / "checkpoints"
SOURCE_ROOT = PROJECT_ROOT / "content" / "sources"
BLUEPRINT_ROOT = PROJECT_ROOT / "content" / "blueprints"

DEFAULT_TERMINAL_ALLOWED_COMMANDS = ["help", "pwd", "tree", "python", "pytest", "show"]
TASK_SUBMISSION_TYPES = {"text", "link", "command_output"}
CHECKPOINT_SUBMISSION_TYPES = {"text", "link", "repository_link", "command_output"}
TASK_REVIEW_MODES = {"deterministic", "manual"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIN_LESSONS_PER_MODULE = 2


@dataclass(frozen=True)
class ContentValidationIssue:
    location: str
    message: str


@dataclass(frozen=True)
class ContentStats:
    courses: int = 0
    modules: int = 0
    lessons: int = 0
    tasks: int = 0
    checkpoints: int = 0


@dataclass(frozen=True)
class ContentValidationReport:
    stats: ContentStats
    errors: list[ContentValidationIssue]

    @property
    def ok(self) -> bool:
        return not self.errors


class ContentValidationException(ValueError):
    def __init__(self, report: ContentValidationReport):
        self.report = report
        lines = ["Content validation failed:"]
        for issue in report.errors:
            lines.append(f"- {issue.location}: {issue.message}")
        super().__init__("\n".join(lines))


class _SchemaBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CourseSchema(_SchemaBase):
    slug: str
    title: str
    description: str
    version: str = "1.0.0"
    duration_weeks: int | None = None
    estimated_weeks: int | None = None
    modules: list[str]
    prerequisites: list[str] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("title", "description", "version")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("duration_weeks", "estimated_weeks")
    @classmethod
    def validate_estimated_weeks(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value < 1 or value > 260:
            raise ValueError("должен быть целым числом в диапазоне 1..260")
        return value

    @field_validator("modules")
    @classmethod
    def validate_modules(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("должен содержать хотя бы один модуль")
        normalized: list[str] = []
        for slug in value:
            if not SLUG_PATTERN.fullmatch(slug):
                raise ValueError(f"некорректный module slug: {slug}")
            normalized.append(slug)
        return normalized

    @field_validator("prerequisites")
    @classmethod
    def validate_prerequisites(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned

    @property
    def effective_duration_weeks(self) -> int:
        return self.duration_weeks if self.duration_weeks is not None else int(self.estimated_weeks or 0)


class ModuleSchema(_SchemaBase):
    slug: str
    title: str
    description: str
    block: int
    objectives: list[str]
    lessons: list[str]
    checkpoint: str

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("title", "description")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("block")
    @classmethod
    def validate_block(cls, value: int) -> int:
        if value < 0 or value > 6:
            raise ValueError("должен быть целым числом в диапазоне 0..6")
        return value

    @field_validator("lessons")
    @classmethod
    def validate_lessons(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("должен содержать хотя бы один урок")
        normalized: list[str] = []
        for key in value:
            if not SLUG_PATTERN.fullmatch(key):
                raise ValueError(f"некорректный lesson key: {key}")
            normalized.append(key)
        return normalized

    @field_validator("objectives")
    @classmethod
    def validate_objectives(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("должен содержать хотя бы одну objective")
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned

    @field_validator("checkpoint")
    @classmethod
    def validate_checkpoint(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value


class LessonFrontMatterSchema(_SchemaBase):
    key: str
    title: str
    summary: str
    objectives: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    task_slug: str | None = None
    source_ids: list[str] = Field(default_factory=list)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть key в lower-kebab-case")
        return value

    @field_validator("title", "summary")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("task_slug")
    @classmethod
    def validate_task_slug(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value:
            return None
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("objectives", "checklist")
    @classmethod
    def validate_string_list(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned

    @field_validator("source_ids")
    @classmethod
    def validate_source_ids(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            source_id = str(item).strip()
            if not source_id:
                raise ValueError("список не должен содержать пустые source_ids")
            if not SLUG_PATTERN.fullmatch(source_id):
                raise ValueError(f"некорректный source_id: {source_id}")
            cleaned.append(source_id)
        return cleaned


class TerminalPresetSchema(_SchemaBase):
    label: str
    command: str

    @field_validator("label", "command")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value


class TerminalConfigSchema(_SchemaBase):
    enabled: bool = False
    presets: list[TerminalPresetSchema] = Field(default_factory=list)
    allow_manual_input: bool = False
    allowed_commands: list[str] = Field(default_factory=lambda: list(DEFAULT_TERMINAL_ALLOWED_COMMANDS))

    @field_validator("allowed_commands")
    @classmethod
    def validate_allowed_commands(cls, value: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for command in value:
            normalized = str(command).strip().lower()
            if not normalized:
                continue
            if not re.fullmatch(r"[a-z0-9_-]+", normalized):
                raise ValueError(f"некорректная команда: {command}")
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)
        if not deduped:
            raise ValueError("список allowed_commands не может быть пустым")
        return deduped


class TaskSchema(_SchemaBase):
    slug: str
    title: str
    summary: str
    instructions: str
    submission_type: str
    definition_of_done: list[str]
    review_mode: str = "deterministic"
    hints: list[str] = Field(default_factory=list)
    terminal: TerminalConfigSchema | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("title", "summary", "instructions")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("submission_type")
    @classmethod
    def validate_submission_type(cls, value: str) -> str:
        if value not in TASK_SUBMISSION_TYPES:
            allowed = ", ".join(sorted(TASK_SUBMISSION_TYPES))
            raise ValueError(f"должен быть одним из: {allowed}")
        return value

    @field_validator("review_mode")
    @classmethod
    def validate_review_mode(cls, value: str) -> str:
        if value not in TASK_REVIEW_MODES:
            allowed = ", ".join(sorted(TASK_REVIEW_MODES))
            raise ValueError(f"должен быть одним из: {allowed}")
        return value

    @field_validator("definition_of_done")
    @classmethod
    def validate_definition_of_done(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("должен содержать хотя бы один пункт")
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned

    @field_validator("hints")
    @classmethod
    def validate_hints(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned


class CheckpointSchema(_SchemaBase):
    slug: str
    title: str
    summary: str
    module_slug: str
    description: str
    project_description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    evaluation_criteria: list[str] = Field(default_factory=list)
    definition_of_done: list[str]
    submission_type: str
    portfolio_expectations: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)

    @field_validator("slug", "module_slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("title", "summary", "description")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("project_description")
    @classmethod
    def validate_project_description(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value:
            raise ValueError("не может быть пустым")
        return value

    @field_validator("submission_type")
    @classmethod
    def validate_submission_type(cls, value: str) -> str:
        if value not in CHECKPOINT_SUBMISSION_TYPES:
            allowed = ", ".join(sorted(CHECKPOINT_SUBMISSION_TYPES))
            raise ValueError(f"должен быть одним из: {allowed}")
        return value

    @field_validator("definition_of_done")
    @classmethod
    def validate_definition_of_done(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("должен содержать хотя бы один пункт")
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned

    @field_validator("requirements", "portfolio_expectations", "hints", "deliverables", "evaluation_criteria")
    @classmethod
    def validate_string_list(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if not text:
                raise ValueError("список не должен содержать пустые элементы")
            cleaned.append(text)
        return cleaned


class SourceRegistryEntrySchema(_SchemaBase):
    id: str
    type: str
    language: str
    allowed_usage: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("должен быть slug в lower-kebab-case")
        return value

    @field_validator("type", "language", "allowed_usage")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value:
            raise ValueError("не может быть пустым")
        return value

@dataclass(frozen=True)
class ParsedTask:
    path: Path
    schema: TaskSchema


@dataclass(frozen=True)
class ParsedCheckpoint:
    path: Path
    schema: CheckpointSchema


@dataclass(frozen=True)
class ParsedLesson:
    path: Path
    schema: LessonFrontMatterSchema
    body_markdown: str
    course_slug: str
    module_slug: str


@dataclass(frozen=True)
class ParsedModule:
    path: Path
    schema: ModuleSchema
    course_slug: str
    lessons_by_file_stem: dict[str, ParsedLesson]


@dataclass(frozen=True)
class ParsedCourse:
    path: Path
    schema: CourseSchema
    modules_by_folder: dict[str, ParsedModule]


@dataclass(frozen=True)
class ContentBundle:
    courses: list[ParsedCourse]
    tasks_by_slug: dict[str, ParsedTask]
    checkpoints_by_slug: dict[str, ParsedCheckpoint]
    lessons_by_key: dict[str, ParsedLesson]
    lesson_order: list[str]
    report: ContentValidationReport


@dataclass
class _BuildState:
    errors: list[ContentValidationIssue] = field(default_factory=list)

    def add_error(self, location: str, message: str) -> None:
        self.errors.append(ContentValidationIssue(location=location, message=message))


def _path_label(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _read_yaml_dict(path: Path, state: _BuildState) -> dict | None:
    try:
        raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        state.add_error(_path_label(path), "файл не найден")
        return None
    except yaml.YAMLError as exc:
        state.add_error(_path_label(path), f"ошибка YAML: {exc}")
        return None

    if not isinstance(raw_data, dict):
        state.add_error(_path_label(path), "ожидался YAML-объект (mapping)")
        return None
    return raw_data


def _add_pydantic_errors(path: Path, exc: ValidationError, state: _BuildState) -> None:
    for item in exc.errors():
        location = ".".join(str(part) for part in item.get("loc", ()))
        message = str(item.get("msg", "некорректное значение"))
        state.add_error(_path_label(path), f"{location}: {message}" if location else message)


def _parse_model(path: Path, model_cls: type[_SchemaBase], state: _BuildState) -> _SchemaBase | None:
    payload = _read_yaml_dict(path, state)
    if payload is None:
        return None
    try:
        return model_cls.model_validate(payload)
    except ValidationError as exc:
        _add_pydantic_errors(path, exc, state)
        return None


def _parse_markdown_lesson(
    *,
    path: Path,
    course_slug: str,
    module_slug: str,
    state: _BuildState,
) -> ParsedLesson | None:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        state.add_error(_path_label(path), "файл урока не найден")
        return None

    if not raw_text.startswith("---\n"):
        state.add_error(_path_label(path), "missing front matter (ожидается блок между --- и ---)")
        return None

    parts = raw_text.split("\n---\n", 1)
    if len(parts) != 2:
        state.add_error(_path_label(path), "некорректный формат front matter")
        return None

    front_matter_text = parts[0].replace("---\n", "", 1)
    body_markdown = parts[1].strip()
    if not body_markdown:
        state.add_error(_path_label(path), "markdown body не должен быть пустым")

    try:
        front_matter_raw = yaml.safe_load(front_matter_text)
    except yaml.YAMLError as exc:
        state.add_error(_path_label(path), f"ошибка YAML во front matter: {exc}")
        return None

    if not isinstance(front_matter_raw, dict):
        state.add_error(_path_label(path), "front matter должен быть YAML-объектом")
        return None

    try:
        lesson_schema = LessonFrontMatterSchema.model_validate(front_matter_raw)
    except ValidationError as exc:
        _add_pydantic_errors(path, exc, state)
        return None

    if path.stem != lesson_schema.key:
        state.add_error(
            _path_label(path),
            f"имя файла ({path.stem}.md) должно совпадать с front matter key ({lesson_schema.key})",
        )

    return ParsedLesson(
        path=path,
        schema=lesson_schema,
        body_markdown=body_markdown,
        course_slug=course_slug,
        module_slug=module_slug,
    )


def _find_duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _has_markdown_section(body_markdown: str, heading: str) -> bool:
    pattern = rf"(?im)^##\s+{re.escape(heading)}\s*$"
    return re.search(pattern, body_markdown) is not None


def _read_source_registry(source_root: Path, state: _BuildState) -> dict[str, SourceRegistryEntrySchema]:
    registry_path = source_root / "source_registry.yml"
    try:
        payload = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        state.add_error(_path_label(registry_path), "source_registry.yml не найден")
        return {}
    except yaml.YAMLError as exc:
        state.add_error(_path_label(registry_path), f"ошибка YAML: {exc}")
        return {}

    if not isinstance(payload, list):
        state.add_error(_path_label(registry_path), "ожидался YAML-список источников")
        return {}

    entries: dict[str, SourceRegistryEntrySchema] = {}
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            state.add_error(_path_label(registry_path), f"элемент #{index + 1}: ожидался YAML-объект")
            continue
        try:
            entry = SourceRegistryEntrySchema.model_validate(row)
        except ValidationError as exc:
            for item in exc.errors():
                location = ".".join(str(part) for part in item.get("loc", ()))
                message = str(item.get("msg", "некорректное значение"))
                marker = f"[{index + 1}]"
                details = f"{marker}.{location}: {message}" if location else f"{marker}: {message}"
                state.add_error(_path_label(registry_path), details)
            continue
        if entry.id in entries:
            state.add_error(_path_label(registry_path), f"duplicate source id: {entry.id}")
            continue
        entries[entry.id] = entry
    return entries


def load_content_bundle(
    *,
    content_root: Path = CONTENT_ROOT,
    task_root: Path = TASK_ROOT,
    checkpoint_root: Path = CHECKPOINT_ROOT,
    source_root: Path = SOURCE_ROOT,
    raise_on_error: bool = True,
) -> ContentBundle:
    state = _BuildState()
    source_registry = _read_source_registry(source_root, state)
    blueprint_path = BLUEPRINT_ROOT / "backend_developer_6_months.yml"
    try:
        blueprint_payload = yaml.safe_load(blueprint_path.read_text(encoding="utf-8"))
        if not isinstance(blueprint_payload, dict):
            state.add_error(_path_label(blueprint_path), "blueprint должен быть YAML-объектом")
        else:
            if "blocks" not in blueprint_payload:
                state.add_error(_path_label(blueprint_path), "blueprint должен содержать blocks")
    except FileNotFoundError:
        state.add_error(_path_label(blueprint_path), "blueprint не найден")
    except yaml.YAMLError as exc:
        state.add_error(_path_label(blueprint_path), f"ошибка YAML: {exc}")

    parsed_tasks: dict[str, ParsedTask] = {}
    for task_path in sorted(task_root.glob("*.yml")):
        task_schema = _parse_model(task_path, TaskSchema, state)
        if task_schema is None:
            continue
        assert isinstance(task_schema, TaskSchema)
        if task_path.stem != task_schema.slug:
            state.add_error(
                _path_label(task_path),
                f"имя файла ({task_path.stem}.yml) должно совпадать с task.slug ({task_schema.slug})",
            )
        if task_schema.slug in parsed_tasks:
            original = parsed_tasks[task_schema.slug].path
            state.add_error(_path_label(task_path), f"duplicate task.slug: {task_schema.slug} (уже есть в {_path_label(original)})")
            continue
        parsed_tasks[task_schema.slug] = ParsedTask(path=task_path, schema=task_schema)

    parsed_checkpoints: dict[str, ParsedCheckpoint] = {}
    for checkpoint_path in sorted(checkpoint_root.glob("*.yml")):
        checkpoint_schema = _parse_model(checkpoint_path, CheckpointSchema, state)
        if checkpoint_schema is None:
            continue
        assert isinstance(checkpoint_schema, CheckpointSchema)
        if checkpoint_path.stem != checkpoint_schema.slug:
            state.add_error(
                _path_label(checkpoint_path),
                f"имя файла ({checkpoint_path.stem}.yml) должно совпадать с checkpoint.slug ({checkpoint_schema.slug})",
            )
        if checkpoint_schema.slug in parsed_checkpoints:
            original = parsed_checkpoints[checkpoint_schema.slug].path
            state.add_error(
                _path_label(checkpoint_path),
                f"duplicate checkpoint.slug: {checkpoint_schema.slug} (уже есть в {_path_label(original)})",
            )
            continue
        parsed_checkpoints[checkpoint_schema.slug] = ParsedCheckpoint(path=checkpoint_path, schema=checkpoint_schema)

    parsed_courses: list[ParsedCourse] = []
    course_slug_registry: dict[str, Path] = {}

    for manifest_path in sorted(content_root.glob("*/course.yml")):
        raw_course_payload = _read_yaml_dict(manifest_path, state)
        if raw_course_payload is None:
            continue
        try:
            course_schema: CourseSchema | None = CourseSchema.model_validate(raw_course_payload)
        except ValidationError as exc:
            _add_pydantic_errors(manifest_path, exc, state)
            course_schema = None

        course_slug_for_children = course_schema.slug if course_schema else manifest_path.parent.name

        if course_schema is not None:
            if course_schema.slug in course_slug_registry:
                state.add_error(
                    _path_label(manifest_path),
                    f"duplicate course.slug: {course_schema.slug} (уже есть в {_path_label(course_slug_registry[course_schema.slug])})",
                )
                continue
            course_slug_registry[course_schema.slug] = manifest_path

        course_dir = manifest_path.parent
        modules_dir = course_dir / "modules"
        module_manifest_paths = sorted(modules_dir.glob("*/module.yml"))
        modules_by_folder: dict[str, ParsedModule] = {}

        for module_manifest_path in module_manifest_paths:
            module_folder_slug = module_manifest_path.parent.name
            module_schema = _parse_model(module_manifest_path, ModuleSchema, state)
            if module_schema is None:
                continue
            assert isinstance(module_schema, ModuleSchema)

            if module_schema.slug != module_folder_slug:
                state.add_error(
                    _path_label(module_manifest_path),
                    f"module.yml slug ({module_schema.slug}) должен совпадать с именем папки ({module_folder_slug})",
                )

            lessons_dir = module_manifest_path.parent / "lessons"
            parsed_lessons_by_stem: dict[str, ParsedLesson] = {}
            for lesson_path in sorted(lessons_dir.glob("*.md")):
                lesson_doc = _parse_markdown_lesson(
                    path=lesson_path,
                    course_slug=course_slug_for_children,
                    module_slug=module_schema.slug,
                    state=state,
                )
                if lesson_doc is None:
                    continue
                parsed_lessons_by_stem[lesson_path.stem] = lesson_doc

            listed_lesson_keys = list(module_schema.lessons)
            duplicate_lesson_keys = _find_duplicates(listed_lesson_keys)
            for duplicate_key in sorted(duplicate_lesson_keys):
                state.add_error(
                    _path_label(module_manifest_path),
                    f"duplicate lesson key в module.lessons: {duplicate_key}",
                )

            if len(listed_lesson_keys) < MIN_LESSONS_PER_MODULE:
                state.add_error(
                    _path_label(module_manifest_path),
                    f"module.lessons должен содержать минимум {MIN_LESSONS_PER_MODULE} урока(ов)",
                )

            listed_set = set(listed_lesson_keys)
            actual_stems = set(parsed_lessons_by_stem.keys())

            for lesson_key in listed_lesson_keys:
                expected_path = lessons_dir / f"{lesson_key}.md"
                if lesson_key not in actual_stems:
                    state.add_error(
                        _path_label(module_manifest_path),
                        f"урок {lesson_key} указан в module.lessons, но файл {_path_label(expected_path)} не найден",
                    )

            for orphan_stem in sorted(actual_stems - listed_set):
                orphan_path = lessons_dir / f"{orphan_stem}.md"
                state.add_error(
                    _path_label(orphan_path),
                    f"orphan lesson file: {orphan_stem} не указан в module.lessons",
                )

            modules_by_folder[module_folder_slug] = ParsedModule(
                path=module_manifest_path,
                schema=module_schema,
                course_slug=course_slug_for_children,
                lessons_by_file_stem=parsed_lessons_by_stem,
            )

        if course_schema is not None:
            duplicate_module_slugs = _find_duplicates(list(course_schema.modules))
            for duplicate_slug in sorted(duplicate_module_slugs):
                state.add_error(
                    _path_label(manifest_path),
                    f"duplicate module.slug в course.modules: {duplicate_slug}",
                )

            for module_slug in course_schema.modules:
                expected_module_path = modules_dir / module_slug / "module.yml"
                if module_slug not in modules_by_folder:
                    state.add_error(
                        _path_label(manifest_path),
                        f"модуль {module_slug} указан в course.modules, но файл {_path_label(expected_module_path)} не найден",
                    )

            listed_modules = set(course_schema.modules)
            actual_modules = set(modules_by_folder.keys())
            for orphan_module in sorted(actual_modules - listed_modules):
                orphan_path = modules_dir / orphan_module / "module.yml"
                state.add_error(
                    _path_label(orphan_path),
                    f"orphan module file: {orphan_module} не указан в course.modules",
                )

            for module in modules_by_folder.values():
                checkpoint_slug = module.schema.checkpoint
                if checkpoint_slug not in parsed_checkpoints:
                    state.add_error(
                        _path_label(module.path),
                        f"checkpoint ссылается на отсутствующий checkpoint: {checkpoint_slug}",
                    )

            parsed_courses.append(
                ParsedCourse(
                    path=manifest_path,
                    schema=course_schema,
                    modules_by_folder=modules_by_folder,
                )
            )

    parsed_lessons_by_key: dict[str, ParsedLesson] = {}
    lesson_order: list[str] = []
    all_module_slugs: dict[str, Path] = {}

    for course in parsed_courses:
        module_slug_registry_in_course: dict[str, Path] = {}
        for module in course.modules_by_folder.values():
            module_slug = module.schema.slug
            if module_slug in module_slug_registry_in_course:
                state.add_error(
                    _path_label(module.path),
                    f"duplicate module.slug в курсе {course.schema.slug}: {module_slug} (уже есть в {_path_label(module_slug_registry_in_course[module_slug])})",
                )
            else:
                module_slug_registry_in_course[module_slug] = module.path

            if module_slug in all_module_slugs:
                state.add_error(
                    _path_label(module.path),
                    f"duplicate module.slug глобально: {module_slug} (уже есть в {_path_label(all_module_slugs[module_slug])})",
                )
            else:
                all_module_slugs[module_slug] = module.path

            for lesson_key in module.schema.lessons:
                lesson_doc = module.lessons_by_file_stem.get(lesson_key)
                if lesson_doc is None:
                    continue
                if lesson_doc.schema.key in parsed_lessons_by_key:
                    state.add_error(
                        _path_label(lesson_doc.path),
                        (
                            f"duplicate lesson.key: {lesson_doc.schema.key} "
                            f"(уже есть в {_path_label(parsed_lessons_by_key[lesson_doc.schema.key].path)})"
                        ),
                    )
                    continue
                parsed_lessons_by_key[lesson_doc.schema.key] = lesson_doc
                lesson_order.append(lesson_doc.schema.key)

    for lesson_doc in parsed_lessons_by_key.values():
        task_slug = lesson_doc.schema.task_slug
        if task_slug and task_slug not in parsed_tasks:
            state.add_error(
                _path_label(lesson_doc.path),
                f"task_slug ссылается на отсутствующий task: {task_slug}",
            )
        if not lesson_doc.schema.source_ids:
            state.add_error(_path_label(lesson_doc.path), "lesson должен содержать хотя бы один source_id")
        for source_id in lesson_doc.schema.source_ids:
            if source_id not in source_registry:
                state.add_error(
                    _path_label(lesson_doc.path),
                    f"source_id не найден в source_registry: {source_id}",
                )

        required_sections = [
            "Why this matters (RU)",
            "What to read (EN source)",
            "What to skip",
            "Action",
            "Definition of Done",
            "Technical English",
        ]
        for section in required_sections:
            if not _has_markdown_section(lesson_doc.body_markdown, section):
                state.add_error(_path_label(lesson_doc.path), f"missing section: {section}")

        if "## Action" not in lesson_doc.body_markdown:
            state.add_error(_path_label(lesson_doc.path), "anti-tutorial hell: lesson должен содержать действие (Action)")

    for checkpoint in parsed_checkpoints.values():
        module_slug = checkpoint.schema.module_slug
        if module_slug not in all_module_slugs:
            state.add_error(
                _path_label(checkpoint.path),
                f"module_slug ссылается на отсутствующий модуль: {module_slug}",
            )
        if checkpoint.schema.project_description is None:
            state.add_error(
                _path_label(checkpoint.path),
                "checkpoint должен содержать project_description",
            )
        if not checkpoint.schema.deliverables:
            state.add_error(
                _path_label(checkpoint.path),
                "checkpoint должен содержать deliverables",
            )
        if not checkpoint.schema.evaluation_criteria:
            state.add_error(
                _path_label(checkpoint.path),
                "checkpoint должен содержать evaluation_criteria",
            )

    referenced_task_slugs = {lesson.schema.task_slug for lesson in parsed_lessons_by_key.values() if lesson.schema.task_slug}
    for task_slug, task in parsed_tasks.items():
        if task_slug not in referenced_task_slugs:
            state.add_error(_path_label(task.path), f"orphan task: {task_slug} не используется ни в одном lesson")

    referenced_checkpoint_slugs = {
        module.schema.checkpoint
        for course in parsed_courses
        for module in course.modules_by_folder.values()
    }
    for checkpoint_slug, checkpoint in parsed_checkpoints.items():
        if checkpoint_slug not in referenced_checkpoint_slugs:
            state.add_error(
                _path_label(checkpoint.path),
                f"orphan checkpoint: {checkpoint_slug} не используется ни в одном module.yml",
            )

    report = ContentValidationReport(
        stats=ContentStats(
            courses=len(parsed_courses),
            modules=sum(len(course.modules_by_folder) for course in parsed_courses),
            lessons=len(parsed_lessons_by_key),
            tasks=len(parsed_tasks),
            checkpoints=len(parsed_checkpoints),
        ),
        errors=list(state.errors),
    )

    bundle = ContentBundle(
        courses=parsed_courses,
        tasks_by_slug=parsed_tasks,
        checkpoints_by_slug=parsed_checkpoints,
        lessons_by_key=parsed_lessons_by_key,
        lesson_order=lesson_order,
        report=report,
    )

    if raise_on_error and not report.ok:
        raise ContentValidationException(report)

    return bundle


def validate_content(
    *,
    content_root: Path = CONTENT_ROOT,
    task_root: Path = TASK_ROOT,
    checkpoint_root: Path = CHECKPOINT_ROOT,
    source_root: Path = SOURCE_ROOT,
) -> ContentValidationReport:
    return load_content_bundle(
        content_root=content_root,
        task_root=task_root,
        checkpoint_root=checkpoint_root,
        source_root=source_root,
        raise_on_error=False,
    ).report
