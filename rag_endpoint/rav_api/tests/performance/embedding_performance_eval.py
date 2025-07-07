import json
from datetime import datetime

from rav_api.rav_endpoint.classes import Document
from rav_api.rav_endpoint.main import (
    process_user_question,
    generate_embedding,
    retrieve_documents,
)


def parse_srt_timestamp(ts: str) -> float:
    dt = datetime.strptime(ts, "%H:%M:%S,%f")
    return dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1e6


def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def compute_total_overlap(
    expected: list[tuple[float, float]], outputted: list[tuple[float, float]]
) -> float:
    total = 0.0
    for e_start, e_end in expected:
        for o_start, o_end in outputted:
            overlap_start = max(e_start, o_start)
            overlap_end = min(e_end, o_end)
            if overlap_start < overlap_end:
                total += overlap_end - overlap_start
    return total


def compare_time_stamps(
    expected_time_stamps: list[tuple[str, str, str]],
    outputted_time_stamps: list[tuple[str, str, str]],
) -> None:
    def group_by_namespace(
        timestamps: list[tuple[str, str, str]]
    ) -> dict[str, list[tuple[float, float]]]:
        grouped = {}
        for ns, start, end in timestamps:
            if not start or not end:
                continue
            start_sec = parse_srt_timestamp(start)
            end_sec = parse_srt_timestamp(end)
            grouped.setdefault(ns, []).append((start_sec, end_sec))
        return grouped

    expected_grouped = group_by_namespace(expected_time_stamps)
    outputted_grouped = group_by_namespace(outputted_time_stamps)

    total_expected = 0.0
    total_matched = 0.0

    for namespace, expected_intervals in expected_grouped.items():
        output_intervals = outputted_grouped.get(namespace, [])
        merged_expected = merge_intervals(expected_intervals)
        merged_output = merge_intervals(output_intervals)

        ns_expected_duration = sum(e - s for s, e in merged_expected)
        ns_overlap = compute_total_overlap(merged_expected, merged_output)

        total_expected += ns_expected_duration
        total_matched += ns_overlap

        print(
            f"[{namespace}] Coverage: {ns_overlap:.2f}s / {ns_expected_duration:.2f}s = "
            f"{ns_overlap / ns_expected_duration:.2%}"
            if ns_expected_duration
            else f"[{namespace}] No expected duration"
        )

    overall_coverage = total_matched / total_expected if total_expected else 0
    print(
        f"\nOverall coverage: {total_matched:.2f}s / {total_expected:.2f}s = {overall_coverage:.2%}"
    )


class ChunkRetrievalEvaluator:
    def __init__(self):
        with open("query_pairs.json", "r") as f:
            self.test_data = json.load(f)

    def run(self):
        for i, case in enumerate(self.test_data):
            print(f"\n=== Case {i+1} ===")
            user_question = case["query"]
            expected_data: list[tuple[str, str, str]] = case["time_stamps"]

            user_id = "test_user"
            processed = process_user_question(user_question)
            embedding = generate_embedding(processed, user_id)
            documents: list[Document] = retrieve_documents(embedding, user_id)

            result_data = [
                (
                    doc.metadata.get("namespace", ""),
                    doc.metadata.get("start", ""),
                    doc.metadata.get("end", ""),
                )
                for doc in documents
            ]
            compare_time_stamps(expected_data, result_data)


if __name__ == "__main__":
    ChunkRetrievalEvaluator().run()
