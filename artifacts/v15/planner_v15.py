#!/usr/bin/env python3
"""v15 limited-rationality planner: explicitly hypothetical S-grade profiles.

Uses the v14 event engine unchanged. Plans are not executed historical events.
No player is created, no real NPC balances or schedule are inferred.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import copy
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v14"))
from engine_v14 import SandboxEngine, aware, canonical, digest


class DecisionSandbox:
    """Deterministic utility scoring, prerequisite/availability and reservation checks."""
    MIN_SCORE = 14

    def __init__(self, event_engine: SandboxEngine, profiles: dict):
        self.events = event_engine
        self.profiles = copy.deepcopy(profiles)  # explicitly S-grade fixture only
        self.decisions = []
        self.reservations = {}
        self.seen_candidate_ids = set()
        self.last_decision_at = None

    @staticmethod
    def score(option: dict) -> int:
        # Arbitrary ordinal weights, NOT a human psychology measurement.
        for name in ("necessity", "urgency", "preference", "effort"):
            value = option.get(name, 0)
            if type(value) is not int or not 0 <= value <= 5:
                raise ValueError("utility components must be integers 0..5")
        return (5 * option.get("necessity", 0)
                + 4 * option.get("urgency", 0)
                + 2 * option.get("preference", 0)
                - option.get("effort", 0))

    @staticmethod
    def overlaps(a, b):
        return a[0] < b[1] and b[0] < a[1]

    def _reason(self, option, now):
        actor = option["actor"]
        profile = self.profiles.get(actor)
        if actor not in self.events.people or profile is None:
            return "unknown_or_unmodelled_actor"
        start = aware(option["start"])
        if start < now or start < self.events.current_time:
            return "start_in_past"
        if option["kind"] not in ("activity", "message_send"):
            return "unsupported_action_requires_separate_approval"
        if option.get("requires_knowledge") and option["requires_knowledge"] not in self.events.state["knowledge"][actor]:
            return "missing_knowledge"
        if option.get("requires_calendar"):
            day = start.date().isoformat()
            if profile.get("calendar", {}).get(day) != option["requires_calendar"]:
                return "calendar_unconfirmed"
        if option.get("requires_stock_below") is not None:
            stock = profile.get("inventory_units")
            if stock is None:
                return "inventory_unknown"
            if stock >= option["requires_stock_below"]:
                return "stock_trigger_not_met"
        if option.get("required_skill") not in (None, *profile.get("skills", [])):
            return "required_skill_missing"
        if option.get("cost_cents", 0):
            cost = option["cost_cents"]
            if type(cost) is not int or cost < 0:
                return "invalid_cost"
            balance = self.events.state["balances_cents"].get(actor)
            if balance is None:
                return "balance_unknown"
            if balance < cost:
                return "insufficient_sandbox_balance"
        if self.score(option) < self.MIN_SCORE and not option.get("commitment"):
            return "low_priority_no_action"
        if option["kind"] == "activity":
            minutes = option.get("minutes")
            if type(minutes) is not int or minutes <= 0:
                return "invalid_duration"
            end = start + timedelta(minutes=minutes)
            location = option.get("location")
            if location is None or self.events.state["locations"].get(actor) != location:
                return "location_unconfirmed"
            if actor in self.events.state["transit"] or self.events._busy(actor, start):
                return "already_busy_or_travelling"
            if any(self.overlaps((start, end), r) for r in self.reservations.get(actor, [])):
                return "reservation_conflict"
        elif option["kind"] == "message_send":
            recipient = option.get("recipient")
            lag = option.get("delay_minutes")
            if recipient not in self.events.people or recipient == actor:
                return "invalid_recipient"
            if type(lag) is not int or lag <= 0:
                return "invalid_delivery_delay"
            if not option.get("topic"):
                return "invalid_message_topic"
        return None

    def decide(self, now, options: list[dict]):
        now = aware(now)
        if now < self.events.current_time:
            raise ValueError("decision cannot go backwards behind executed event time")
        if self.last_decision_at is not None and now < self.last_decision_at:
            raise ValueError("decision clock cannot go backwards")
        self.last_decision_at = now
        ordered = sorted(options, key=lambda o:
                         (-int(bool(o.get("commitment"))), -self.score(o),
                          o["actor"], o["id"]))
        batch = []
        for option in ordered:
            uid = option["id"]
            if uid in self.seen_candidate_ids:
                raise ValueError("duplicate candidate ID")
            self.seen_candidate_ids.add(uid)
            reason = self._reason(option, now)
            record = {"candidate_id": uid, "actor": option["actor"],
                      "decision_at": now.isoformat(), "proposed_start": option["start"],
                      "utility": self.score(option),
                      "choice": "declined" if reason else "scheduled",
                      "reason": reason or "prerequisites_satisfied",
                      "fixture_grade": "S",
                      "reservation_only": True}
            if not reason:
                payload = {}
                if option["kind"] == "activity":
                    payload = {"minutes":option["minutes"], "location":option["location"]}
                    start = aware(option["start"])
                    end = start + timedelta(minutes=option["minutes"])
                    self.reservations.setdefault(option["actor"], []).append((start, end))
                else:
                    payload = {"recipient":option["recipient"], "topic":option["topic"],
                               "delay_minutes":option["delay_minutes"]}
                self.events.schedule("V15:"+uid, option["start"], option["kind"],
                                     option["actor"], **payload)
            self.decisions.append(record)
            batch.append(record)
        return batch

    def audit(self):
        problems = self.events.audit()
        ids = [x["candidate_id"] for x in self.decisions]
        if len(ids) != len(set(ids)):
            problems.append("duplicate decision candidate ID")
        for person, slots in self.reservations.items():
            for i, x in enumerate(slots):
                if any(self.overlaps(x, y) for y in slots[i+1:]):
                    problems.append("reservation overlap: "+person)
        for d in self.decisions:
            if d["choice"]=="scheduled" and "V15:"+d["candidate_id"] not in self.events.event_ids:
                problems.append("accepted option missing from engine queue")
        return problems

    def report(self):
        choices = {"scheduled":0, "declined":0}
        for d in self.decisions:
            choices[d["choice"]] += 1
        return {"test_only":True, "planner_version":"15.0", "choices":choices,
                "decision_count":len(self.decisions),
                "decision_sha256":digest(self.decisions),
                "event_report":self.events.report(), "audit_violations":self.audit(),
                "no_automatic_payment":True,
                "source_class":"S synthetic profile; no actual NPC life inferred"}
