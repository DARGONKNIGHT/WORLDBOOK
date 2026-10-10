#!/usr/bin/env python3
"""Deterministic v15 S-only illustration: Friday schedule, messages and refusal.

No real calendars, bank balances, inventory, salaries, traffic, or persons inferred.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from planner_v15 import DecisionSandbox, SandboxEngine

BASE=Path(__file__).resolve().parent
FROZEN=BASE.parent/"v14"/"official_world_state_frozen_v13.json"
TZ=timezone(timedelta(hours=8))
ANCHOR=datetime(2026,10,9,9,0,tzinfo=TZ)
def at(minutes=0):
    return (ANCHOR+timedelta(minutes=minutes)).isoformat()

def option(id, actor, minute, kind="activity", **fields):
    return {"id":id,"actor":actor,"start":at(minute),"kind":kind,
            "necessity":fields.pop("necessity",3),
            "urgency":fields.pop("urgency",2),
            "preference":fields.pop("preference",2),
            "effort":fields.pop("effort",1),**fields}

def build():
    people=[f"P{i:03d}" for i in range(1,32)]
    engine=SandboxEngine(ANCHOR,people,
        balances_cents={"P002":90000,"P005":50000,"P006":20000,"P014":50000},
        locations={"P002":"S_TEST_SHOP","P005":"S_TEST_FACTORY",
                   "P006":"S_TEST_HOME","P011":"S_TEST_SCHOOL",
                   "P014":"S_TEST_WORKSHOP"})
    profiles={
        "P002":{"inventory_units":2,"skills":["shopkeeper"],
                "calendar":{"2026-10-09":"workday"}},
        "P005":{"skills":["technician"],"calendar":{"2026-10-09":"workday"}},
        "P006":{"skills":["accountant"],"calendar":{"2026-10-09":"private_day"}},
        "P011":{"skills":["teacher"],"calendar":{"2026-10-09":"workday"}},
        "P014":{"skills":["repair"],"calendar":{"2026-10-09":"workday"}},
    }
    return DecisionSandbox(engine,profiles)

def run_case():
    p=build()
    first=[
        option("store_stocktake","P002",5,minutes=40,location="S_TEST_SHOP",
               necessity=5,urgency=5,requires_stock_below=3),
        option("store_break_conflict","P002",20,minutes=30,location="S_TEST_SHOP",
               necessity=3,urgency=3),
        option("shop_repair_question","P002",12,"message_send",recipient="P014",
               topic="test_repair_question",delay_minutes=28,requires_stock_below=3),
        option("workshop_prior_commitment","P014",10,minutes=65,
               location="S_TEST_WORKSHOP",commitment=True,necessity=5),
        option("technician_shift_notice","P005",12,"message_send",recipient="P006",
               topic="test_shift_notice",delay_minutes=20),
        option("school_prep","P011",15,minutes=30,location="S_TEST_SCHOOL",
               required_skill="teacher",requires_calendar="workday",necessity=4),
        option("premature_family_reply","P006",20,"message_send",recipient="P005",
               topic="test_shift_ack",delay_minutes=10,requires_knowledge="test_shift_notice"),
        option("premature_quote","P014",25,"message_send",recipient="P002",
               topic="test_repair_quote",delay_minutes=20,requires_knowledge="test_repair_question"),
        option("cash_unknown_course","P011",65,minutes=30,location="S_TEST_SCHOOL",
               cost_cents=70000),
        option("low_value_no_action","P005",90,minutes=15,location="S_TEST_FACTORY",
               necessity=0,urgency=0,preference=0,effort=5),
        option("no_unauthorized_purchase","P002",100,"transfer",recipient="P014",
               cost_cents=1000),
    ]
    p.decide(ANCHOR,first)
    p.events.run(ANCHOR+timedelta(minutes=45))
    second=[
        option("family_ack_after_delivery","P006",55,"message_send",recipient="P005",
               topic="test_shift_ack",delay_minutes=10,requires_knowledge="test_shift_notice"),
        option("quote_after_delivery","P014",80,"message_send",recipient="P002",
               topic="test_repair_quote",delay_minutes=20,requires_knowledge="test_repair_question"),
        option("excess_cost","P002",120,minutes=10,location="S_TEST_SHOP",
               cost_cents=200000),
        option("unconfirmed_saturday_school","P011",1500,minutes=20,location="S_TEST_SCHOOL",
               requires_calendar="workday"),
    ]
    p.decide(ANCHOR+timedelta(minutes=45),second)
    p.events.run(ANCHOR+timedelta(minutes=90))
    third=[
        option("technician_ack_review","P005",95,minutes=20,
               location="S_TEST_FACTORY",requires_knowledge="test_shift_ack"),
        option("too_early_quote_review","P002",95,minutes=15,
               location="S_TEST_SHOP",requires_knowledge="test_repair_quote")
    ]
    p.decide(ANCHOR+timedelta(minutes=90),third)
    p.events.run(ANCHOR+timedelta(minutes=105))
    last=[option("quote_review_after_receipt","P002",120,minutes=25,
                 location="S_TEST_SHOP",requires_knowledge="test_repair_quote")]
    p.decide(ANCHOR+timedelta(minutes=105),last)
    p.events.run(ANCHOR+timedelta(days=1))
    assert not p.audit(),p.audit()
    return p

def generate():
    before=FROZEN.read_bytes()
    official=json.loads(before)
    assert official["game_started"] is False
    assert official["player_character"] is None
    assert official["game_clock_time"] is None
    assert len(official["people"])==31
    p=run_case()
    assert FROZEN.read_bytes()==before
    summary=p.report()
    summary["official_frozen_sha256"]=hashlib.sha256(before).hexdigest()
    summary["official_game_events_written"]=0
    summary["notes"]="Plans/messages/locations/inventory/balances are S-only fixture; neither historical acts nor verified schedules."
    (BASE/"sandbox_v15_decisions.json").write_text(
        json.dumps(p.decisions,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (BASE/"sandbox_v15_journal.json").write_text(
        json.dumps(p.events.journal,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (BASE/"sandbox_v15_summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    print(json.dumps(generate(),ensure_ascii=False,indent=2))
