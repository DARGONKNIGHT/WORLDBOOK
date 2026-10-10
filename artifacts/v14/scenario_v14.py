#!/usr/bin/env python3
"""Thirty-day S-grade test fixture. Never writes canonical world state."""
from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import json
from engine_v14 import SandboxEngine, digest

BASE=Path(__file__).resolve().parent
FROZEN=BASE/'official_world_state_frozen_v13.json'
ANCHOR=datetime.fromisoformat('2026-10-09T09:00:00+08:00') # test clock ONLY


def build_fixture():
    official=json.loads(FROZEN.read_text(encoding='utf-8'))
    assert official['game_clock_time'] is None and not official['game_started']
    ids=[p['id'] for p in official['people']]
    assert len(ids)==31 and len(set(ids))==31
    eng=SandboxEngine(ANCHOR,ids,
        balances_cents={'P002':200000,'P014':50000,'P015':30000},
        locations={'P002':'TEST_SHOP','P005':'TEST_FACTORY','P006':'TEST_HOME_006',
                   'P014':'TEST_HOME_014','P015':'TEST_WORKSPACE_015'},
        permissions={'P014':['repair_approval']})
    # Routine-check events perform NO work, money transfers or social actions.
    for day in range(30):
        t=ANCHOR+timedelta(days=day,hours=11)
        for i in range(1,16):
            eng.schedule(f'CORE-CHECK-{day:02d}-{i:03d}',t,'routine_check',f'P{i:03d}',priority=90)
        if day%7==0:
            for i in range(16,32):
                eng.schedule(f'CAND-CHECK-{day:02d}-{i:03d}',t,'routine_check',f'P{i:03d}',priority=90)
    eng.schedule('STORE-OPEN',ANCHOR,'activity','P002',minutes=180,location='TEST_SHOP')
    eng.schedule('ACTIVITY-CONFLICT',ANCHOR+timedelta(minutes=30),'activity','P002',minutes=60,location='TEST_SHOP')
    eng.schedule('FAMILY-SHIFT-NOTE',ANCHOR+timedelta(minutes=20),'message_send','P005',
                 recipient='P006',topic='shift_notice',delay_minutes=20)
    d1=ANCHOR+timedelta(days=1)
    eng.schedule('REPAIR-TRAVEL',d1-timedelta(hours=1),'travel','P014',origin='TEST_HOME_014',
                 destination='TEST_SITE_A',minutes=40)
    eng.schedule('IN-TRANSIT-ACTIVITY',d1-timedelta(minutes=40),'activity','P014',minutes=20,location='TEST_SITE_A')
    eng.schedule('REPAIR-ARRIVAL-ACTIVITY',d1-timedelta(minutes=15),'activity','P014',minutes=60,location='TEST_SITE_A')
    eng.schedule('WRONG-LOCATION',ANCHOR+timedelta(days=2),'activity','P014',minutes=20,location='TEST_SHOP')
    eng.schedule('PAY-REPAIR',ANCHOR+timedelta(days=3),'transfer','P002',target='P014',cents=8000,transaction_id='TX-REPAIR-001')
    eng.schedule('PAY-PARTNER',ANCHOR+timedelta(days=4),'transfer','P014',target='P015',cents=3000,transaction_id='TX-TECH-001')
    eng.schedule('DUPLICATE-PAYMENT',ANCHOR+timedelta(days=5),'transfer','P002',target='P014',cents=8000,transaction_id='TX-REPAIR-001')
    eng.schedule('OVERDRAW',ANCHOR+timedelta(days=6),'transfer','P015',target='P014',cents=9000000,transaction_id='TX-OVERDRAW')
    eng.schedule('UNAUTHORIZED-APPROVAL',ANCHOR+timedelta(days=7),'approve','P005',scope='repair_approval')
    eng.schedule('AUTHORIZED-APPROVAL',ANCHOR+timedelta(days=8),'approve','P014',scope='repair_approval')
    eng.schedule('SECOND-PAYMENT',ANCHOR+timedelta(days=10),'transfer','P002',target='P014',cents=1200,transaction_id='TX-REPAIR-002')
    return eng


def execute_and_write():
    frozen_before=FROZEN.read_bytes()
    eng=build_fixture()
    eng.run(ANCHOR+timedelta(days=30))
    assert FROZEN.read_bytes()==frozen_before, '正式存档发生变化'
    assert not eng.audit(), eng.audit()
    # Unknown identity values remain unknown in official archive.
    canonical=json.loads(FROZEN.read_text(encoding='utf-8'))
    assert canonical['player_character'] is None and canonical['game_clock_time'] is None
    assert canonical['actual_game_events']==[] and canonical['scheduled_game_events']==[]
    assert all(p['cash_balance_cny'] is None for p in canonical['people'])
    report=eng.report()
    report['official_frozen_state_sha256']=__import__('hashlib').sha256(frozen_before).hexdigest()
    report['official_game_events_written']=0
    report['sandbox_assumptions']='所有金钱、位置、通信、权限、计划与选择仅为S级测试输入'
    (BASE/'sandbox_30day_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'sandbox_30day_journal.json').write_text(json.dumps(eng.journal,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'sandbox_30day_final_state.json').write_text(json.dumps(eng.state,ensure_ascii=False,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    print(json.dumps(execute_and_write(),ensure_ascii=False,indent=2))
