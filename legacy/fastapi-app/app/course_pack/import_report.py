"""Aggregated report for course pack preflight / preview (operational layer)."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.content_pipeline import ContentValidationIssue, ContentStats


@dataclass
class CoursePackImportReport:
    errors: list[ContentValidationIssue] = field(default_factory=list)
    warnings: list[ContentValidationIssue] = field(default_factory=list)
    detected_courses: list[str] = field(default_factory=list)
    detected_modules: int = 0
    detected_lessons: int = 0
    detected_tasks: int = 0
    detected_checkpoints: int = 0
    manifest_present: bool = False
    contract_version: int | None = None
    compatible: bool = False

    @staticmethod
    def from_parts(
        *,
        graph_errors: list[ContentValidationIssue],
        graph_warnings: list[ContentValidationIssue],
        stats: ContentStats,
        course_slugs: list[str],
        manifest_present: bool,
        contract_version: int | None,
        conflict_errors: list[ContentValidationIssue],
        conflict_warnings: list[ContentValidationIssue],
        manifest_warnings: list[ContentValidationIssue],
        manifest_errors: list[ContentValidationIssue],
    ) -> CoursePackImportReport:
        errors = sorted(
            graph_errors + conflict_errors + manifest_errors,
            key=lambda item: (item.location, item.message),
        )
        warnings = sorted(
            graph_warnings + conflict_warnings + manifest_warnings,
            key=lambda item: (item.location, item.message),
        )
        compatible = not errors
        return CoursePackImportReport(
            errors=errors,
            warnings=warnings,
            detected_courses=sorted(course_slugs),
            detected_modules=stats.modules,
            detected_lessons=stats.lessons,
            detected_tasks=stats.tasks,
            detected_checkpoints=stats.checkpoints,
            manifest_present=manifest_present,
            contract_version=contract_version,
            compatible=compatible,
        )
