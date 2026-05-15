#!/usr/bin/env python3
"""Local dry-run harness for Ylopo event processing logic.

This does not call production APIs. It validates scoring, priority, and required actions.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

SCORING = {
    "SHOWING_REQUEST": 30,
    "REQUEST_INFORMATION": 25,
    "PRIORITY_LEAD_EVENT": 25,
    "REGISTRATION": 20,
    "FAVORITE_LISTING": 20,
    "SAVED_SEARCH": 15,
}

EVENT_TAGS = {
    "REGISTRATION": "ylopo_registration",
    "SHOWING_REQUEST": "ylopo_showing_request",
    "REQUEST_INFORMATION": "ylopo_request_info",
    "FAVORITE_LISTING": "ylopo_favorited",
    "VIEW_LISTING_DETAIL": "ylopo_listing_view",
    "SEARCH": "ylopo_search",
    "SAVED_SEARCH": "ylopo_saved_search",
    "PRIORITY_LEAD_EVENT": "ylopo_priority",
    "STATS_UPDATE": "ylopo_stats_update",
    "CONTACT_INFO_UPDATED": "ylopo_contact_updated",
    "NOTE": "ylopo_note",
    "TAG": "ylopo_tag_update",
}


def score_event(evt: Dict[str, Any]) -> int:
    score = SCORING.get(evt.get("eventType"), 0)
    lead = evt.get("lead", {})
    if int(lead.get("lastSessionListingsViewed", 0) or 0) >= 5:
        score += 10
    if int(lead.get("lastSessionListingsSaved", 0) or 0) >= 1:
        score += 10
    if int(lead.get("lastSessionShowingInfoRequests", 0) or 0) >= 1:
        score += 10
    return score


def priority_from_score(score: int) -> str:
    if score >= 70:
        return "HOT"
    if score >= 40:
        return "WARM"
    return "COLD"


def process_event(evt: Dict[str, Any]) -> Dict[str, Any]:
    score = score_event(evt)
    priority = priority_from_score(score)
    event_type = evt.get("eventType", "UNKNOWN")
    tags: List[str] = []
    if event_type in EVENT_TAGS:
        tags.append(EVENT_TAGS[event_type])
    tags.append({"HOT": "ylo-hot-lead", "WARM": "ylo-warm-lead", "COLD": "ylo-cold-lead"}[priority])

    return {
        "eventType": event_type,
        "score": score,
        "priority": priority,
        "tags": tags,
        "createTask": priority == "HOT",
        "createInternalSms": priority == "HOT",
        "createOrUpdateOpportunity": True,
        "createInternalNote": True,
    }


def run_tests() -> None:
    tests = [
        {"eventType": "REGISTRATION", "lead": {"lastSessionListingsViewed": 1}},
        {"eventType": "SHOWING_REQUEST", "lead": {"lastSessionListingsViewed": 7, "lastSessionListingsSaved": 1}},
        {"eventType": "FAVORITE_LISTING", "lead": {"lastSessionListingsSaved": 2}},
        {"eventType": "PRIORITY_LEAD_EVENT", "lead": {"lastSessionShowingInfoRequests": 2}},
        {"eventType": "STATS_UPDATE", "lead": {"lastSessionListingsViewed": 5}},
    ]

    for i, t in enumerate(tests, start=1):
        result = process_event(t)
        print(f"TEST {i}: {result['eventType']} => score={result['score']} priority={result['priority']} tags={','.join(result['tags'])}")


if __name__ == "__main__":
    run_tests()
