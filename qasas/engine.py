from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from .models import (
    AnalysisResult,
    DatabaseData,
    DatabaseEntry,
    LevelSummary,
    MatchRecord,
    SampleData,
)


ProgressCallback = Callable[[int, int], None] | None


def bounded_levenshtein(left: str, right: str, max_distance: int = 2) -> int:
    """Return Levenshtein distance, or max_distance + 1 after an early cutoff."""

    if left == right:
        return 0
    if abs(len(left) - len(right)) > max_distance:
        return max_distance + 1
    if len(left) > len(right):
        left, right = right, left
    if not left:
        return len(right) if len(right) <= max_distance else max_distance + 1

    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        row_minimum = left_index
        for right_index, right_char in enumerate(right, start=1):
            insertion = current[right_index - 1] + 1
            deletion = previous[right_index] + 1
            substitution = previous[right_index - 1] + (left_char != right_char)
            value = min(insertion, deletion, substitution)
            current.append(value)
            if value < row_minimum:
                row_minimum = value
        if row_minimum > max_distance:
            return max_distance + 1
        previous = current
    distance = previous[-1]
    return distance if distance <= max_distance else max_distance + 1


def _summarize(matches: list[MatchRecord], label: str) -> LevelSummary:
    return LevelSummary(
        label=label,
        unique_clones=len(matches),
        total_reads=sum(match.clone.reads for match in matches),
        frequency_percent=sum(match.clone.frequency_percent for match in matches),
    )


def analyse(
    sample: SampleData,
    database: DatabaseData,
    max_distance: int = 2,
    progress_callback: ProgressCallback = None,
) -> AnalysisResult:
    if max_distance < 0:
        raise ValueError("最大Levenshtein距離は0以上である必要があります。")

    by_vj_length: dict[tuple[str, str, int], list[DatabaseEntry]] = defaultdict(list)
    for entry in database.entries:
        by_vj_length[(entry.v_gene, entry.j_gene, len(entry.cdr3_aa))].append(entry)

    matches: list[MatchRecord] = []
    total = len(sample.clones)
    for number, clone in enumerate(sample.clones, start=1):
        candidates: list[DatabaseEntry] = []
        seen_candidates: set[tuple[str, str, str]] = set()
        min_length = max(0, len(clone.cdr3_aa) - max_distance)
        max_length = len(clone.cdr3_aa) + max_distance
        for v_gene in clone.v_genes:
            for j_gene in clone.j_genes:
                for length in range(min_length, max_length + 1):
                    for entry in by_vj_length.get((v_gene, j_gene, length), ()):
                        key = (entry.v_gene, entry.j_gene, entry.cdr3_aa)
                        if key not in seen_candidates:
                            seen_candidates.add(key)
                            candidates.append(entry)

        best_distance = max_distance + 1
        best_entries: list[DatabaseEntry] = []
        for entry in candidates:
            distance = bounded_levenshtein(clone.cdr3_aa, entry.cdr3_aa, max_distance)
            if distance < best_distance:
                best_distance = distance
                best_entries = [entry]
            elif distance == best_distance and distance <= max_distance:
                best_entries.append(entry)
            if best_distance == 0:
                # Continue only to collect other exact database keys/annotations.
                continue

        if best_distance <= max_distance:
            matches.append(
                MatchRecord(
                    clone=clone,
                    distance=best_distance,
                    database_entries=tuple(best_entries),
                )
            )
        if progress_callback and (number == total or number % 250 == 0):
            progress_callback(number, total)

    matches.sort(
        key=lambda match: (
            match.distance,
            -match.clone.reads,
            match.clone.display_v_gene,
            match.clone.cdr3_aa,
        )
    )
    exact_summaries = tuple(
        _summarize([match for match in matches if match.distance == distance], f"LV{distance}")
        for distance in range(max_distance + 1)
    )
    cumulative_summaries = tuple(
        _summarize([match for match in matches if match.distance <= distance], f"≤LV{distance}")
        for distance in range(max_distance + 1)
    )
    return AnalysisResult(
        sample=sample,
        database=database,
        matches=tuple(matches),
        exact_summaries=exact_summaries,
        cumulative_summaries=cumulative_summaries,
    )

