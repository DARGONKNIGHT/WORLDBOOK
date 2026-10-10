#!/usr/bin/env python3
"""Cross-domain v17-v26 S-only scenario. Writes evidence, never official data."""
from pathlib import Path
import json
from datetime import datetime,timedelta,timezone
from realism_layers import *

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
ORIGINAL=ROOT/"artifacts/v14/official_world_state_frozen_v13.json"
TZ=timezone(timedelta(hours=8))
T=datetime(2026,10,9,9,0,tzinfo=TZ)
when=lambda m:(T+timedelta(minutes=m)).isoformat()

def run():
    official=ORIGINAL.read_bytes()
    lock=IntegrationV26(official)
    transcript=[]
    def log(version,name,data):
        record=lock.record(f"v{version}-{name}",f"v{version}",data)
        transcript.append(record)
    # 17: fully synthetic timetable, not actual Beijing departure / vehicle.
    gt=TransitV17()
    gt.add("S_TEST_TRIP_1","S_STOP_A","S_STOP_B",when(10),when(35))
    gt.add("S_TEST_TRIP_2","S_STOP_B","S_STOP_C",when(43),when(60))
    log(17,"synthetic_two_leg",gt.via("S_STOP_A","S_STOP_B","S_STOP_C",when(0),5))
    # 18: grounded OSM village point, *not* claimed a school/shop/hospital.
    osm=PlacesV18()
    osm.add("OSM:6410843713","place",40.1880155,116.7077492,
            "R_OSM","data/derived/manifest.json","前礼务村")
    log(18,"real_anchor_unknown_hours",osm.get("OSM:6410843713"))
    # 19: amounts and individuals purely invented test accounts.
    h=HousingV19({"S_TENANT":120000,"S_LANDLORD":20000})
    h.lease("S_LEASE","S_TENANT","S_LANDLORD","S_TEST_PROPERTY",30000)
    before=sum(h.balances.values())
    result=h.pay("S_LEASE","2026-10")
    assert sum(h.balances.values())==before
    log(19,"rent_atomic",{"event":result,"balances":h.balances})
    # 20: quotation vs dispatch vs payment.
    s=CommerceV20({"S_BOX":6},{"S_BUYER":30000,"S_SELLER":0})
    s.quote("S_QUOTE","S_SELLER","S_BUYER","S_BOX",2,2000)
    log(20,"quote_not_contract",s.orders["S_QUOTE"].copy())
    s.accept("S_QUOTE");s.dispatch("S_QUOTE");s.receive("S_QUOTE")
    log(20,"goods_received_payment_pending",s.orders["S_QUOTE"].copy())
    s.pay("S_QUOTE")
    log(20,"payment_separate",{"order":s.orders["S_QUOTE"],"balances":s.balances})
    # 21: cannot infer tax withholding; explicit synthetic amount.
    labor=EmploymentV21({"S_EMPLOYER":90000})
    labor.hire("S_CONTRACT","S_WORKER","S_EMPLOYER","S_TEST_FACTORY",30000)
    log(21,"payslip_only_explicit_withholding",labor.payroll("S_CONTRACT","2026-10",2500))
    # 22: separate request, evidence, capacity and responsible verifier.
    service=ServicesV22();service.provider("S_CLASS","education",1,"S_REGISTRAR")
    service.request("S_APPLY","S_CLASS","S_STUDENT",{"grade":"S_TEST"})
    log(22,"service_approved_with_capacity",{"status":service.decide("S_APPLY","S_REGISTRAR",True),
                                             "capacity_remaining":service.providers["S_CLASS"]["capacity"]})
    # 23: a separate synthetic procedure, not actual governmental approval.
    adm=AdministrationV23();adm.office("S_OFFICE",["S_AUTHORIZED"],"S_FAKE_RULE","2026-01-01")
    adm.file("S_CASE","S_OFFICE","S_APPLICANT",when(0),{"docs":"S_FAKE"})
    log(23,"limited_approval",{"status":adm.decide("S_CASE","S_AUTHORIZED",True,"S_TEST_EVIDENCE")})
    # 24: delayed, recipient-only, still an unverified rumor.
    info=InformationV24()
    info.send("S_MESSAGE","S_FROM","S_TO","S_UNVERIFIED_REPORT",when(1),20)
    info.deliver("S_MESSAGE",when(21)); info.read("S_MESSAGE","S_TO",when(22))
    log(24,"recipient_only_rumor",info.knowledge["S_TO"])
    # 25: statistical publication barrier; no direct cash mutation.
    macro=MacroeconomyV25()
    macro.record("S_INDEX","S_REGION","S_COST","2025-12-31",when(30),100,"S_UNIT","S_SOURCE")
    assert macro.as_known("S_INDEX",when(0)) is None
    log(25,"hypothetical_exposure_no_payment",macro.expose("S_INDEX","S_ACTOR",10,0.3,when(31)))
    # 26: cross-layer replayable digest; original remains byte-for-byte identical.
    report=lock.summary(ORIGINAL.read_bytes())
    report.update({"versions_completed":list(range(17,27)),"test_fixture":"S_ONLY",
                   "external_data":[{"id":"qianliwu_beijing_osm_local_graph_2026_10_01",
                                    "reality":"R_OSM_PLACE_POINT_ONLY; not R transit/housing/commerce"}],
                   "no_automatic_life_or_live_market_simulation":True,
                   "source_baseline":"GitHub artifacts/v14/official_world_state_frozen_v13.json"})
    log(26,"integrated_frozen_check",report.copy())
    report=lock.summary(ORIGINAL.read_bytes())
    report.update({"versions_completed":list(range(17,27)),"test_fixture":"S_ONLY",
                   "external_data":[{"id":"qianliwu_beijing_osm_local_graph_2026_10_01",
                                     "reality":"R_OSM_PLACE_POINT_ONLY; no real timetables"}],
                   "no_automatic_life_or_live_market_simulation":True,
                   "source_baseline":"GitHub artifacts/v14/official_world_state_frozen_v13.json"})
    (BASE/"simulation_evidence.json").write_text(json.dumps(transcript,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (BASE/"simulation_summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2))
