#!/usr/bin/env python3
"""v17-v26 realistic WORLD BOOK domains, standard library, S sandbox by default.

These are explicit process models, NOT complete Chinese-law, human decision,
public transit, healthcare, market-price, or legal-eligibility simulators.
For each real data input preserve its source, publication date and license.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
import hashlib, json
from pathlib import Path


def dt(s):
    x=datetime.fromisoformat(s) if isinstance(s,str) else s
    if not isinstance(x,datetime) or x.tzinfo is None or x.utcoffset() is None:
        raise ValueError("timezone-aware datetime required")
    return x


def must(ok,why):
    if not ok:
        raise ValueError(why)


def money(value):
    must(type(value) is int and value >= 0,"amount must be nonnegative integer cents")
    return value


def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,
              sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


class TransitV17:
    """GTFS-like static trips and optional walking transfer time, NOT actual schedules."""
    def __init__(self):
        self.trips={}
    def add(self,trip_id,from_stop,to_stop,departure,arrival,grade="S_FIXTURE",available=True):
        must(trip_id not in self.trips,"duplicate trip")
        d,a=dt(departure),dt(arrival)
        must(a>d,"nonpositive travel time")
        must(grade in ("S_FIXTURE","R_VERIFIED_SCHEDULE"),"missing provenance grade")
        must(from_stop!=to_stop,"identical transit stops")
        self.trips[trip_id]=dict(id=trip_id,origin=from_stop,destination=to_stop,
                                 departure=d.isoformat(),arrival=a.isoformat(),
                                 grade=grade,available=available)
    def direct(self,origin,destination,not_before):
        req=dt(not_before)
        found=[]
        for t in self.trips.values():
            if t["origin"]==origin and t["destination"]==destination and t["available"] and dt(t["departure"])>=req:
                found.append(t.copy())
        return sorted(found,key=lambda t:(t["arrival"],t["departure"],t["id"]))
    def via(self,origin,transfer,destination,not_before,minimum_transfer_minutes=5):
        must(type(minimum_transfer_minutes) is int and minimum_transfer_minutes>=0,"invalid transfer")
        results=[]
        for first in self.direct(origin,transfer,not_before):
            threshold=dt(first["arrival"])+timedelta(minutes=minimum_transfer_minutes)
            for second in self.direct(transfer,destination,threshold):
                results.append(dict(legs=[first["id"],second["id"]],arrive=second["arrival"],
                                    provenance="S_OR_MIXED_NOT_TICKETED",booked=False))
        return sorted(results,key=lambda t:(t["arrive"],t["legs"]))


class PlacesV18:
    """Separate evidenced geometry from fictional facilities and actual eligibility."""
    def __init__(self):self.places={}
    def add(self,code,kind,latitude,longitude,source_grade,source_ref,public_name=None):
        must(code not in self.places,"duplicate place id")
        must(-90<=latitude<=90 and -180<=longitude<=180,"bad coordinates")
        must(source_grade in ("R_OSM","S_TEST"),"grade unknown")
        must(bool(source_ref),"source reference required")
        self.places[code]=dict(id=code,kind=kind,lat=latitude,lon=longitude,
               source_grade=source_grade,source_ref=source_ref,
               display_name=public_name,open_status="U",capacity="U")
    def get(self,code):return self.places.get(code)
    def query(self,kind):
        return [p.copy() for p in self.places.values() if p["kind"]==kind]


class HousingV19:
    """Tenure, residency and matched rent transfers, only when balances are known."""
    def __init__(self,balances=None):
        self.balances=dict(balances or {})
        self.leases={}
        self.rent_paid=set()
    def lease(self,id,tenant,landlord,property_id,rent_cents):
        must(id not in self.leases and tenant!=landlord,"invalid lease")
        money(rent_cents)
        must(bool(property_id),"property id required")
        self.leases[id]=dict(tenant=tenant,landlord=landlord,property=property_id,
                             rent_cents=rent_cents,status="active")
    def pay(self,id,month):
        must(id in self.leases and self.leases[id]["status"]=="active","no active lease")
        key=(id,month)
        must(key not in self.rent_paid,"rent already paid")
        row=self.leases[id];src,dst=row["tenant"],row["landlord"]
        must(src in self.balances and dst in self.balances,"unknown account cannot be debited")
        must(self.balances[src]>=row["rent_cents"],"insufficient funds")
        self.balances[src]-=row["rent_cents"]
        self.balances[dst]+=row["rent_cents"]
        self.rent_paid.add(key)
        return {"lease":id,"period":month,"cash_transfer":row["rent_cents"],"currency":"CNY"}


class CommerceV20:
    """Quote≠order≠shipment≠delivery≠payment; no automatic invoice settlement."""
    def __init__(self,inventory,balances):
        self.inventory=dict(inventory)
        self.balances=dict(balances)
        self.orders={}
    def quote(self,id,seller,buyer,item,qty,unit_cents):
        must(id not in self.orders and seller!=buyer,"bad quote")
        must(type(qty) is int and qty>0,"bad qty")
        money(unit_cents)
        self.orders[id]=dict(seller=seller,buyer=buyer,item=item,qty=qty,
                             price=qty*unit_cents,contract="quotation",
                             shipment="not_dispatched",payment="unpaid")
    def accept(self,id):
        row=self.orders[id]
        must(row["contract"]=="quotation","invalid quote transition")
        row["contract"]="confirmed"
    def dispatch(self,id):
        row=self.orders[id]
        must(row["contract"]=="confirmed" and row["shipment"]=="not_dispatched","not ready")
        must(self.inventory.get(row["item"],0)>=row["qty"],"insufficient inventory")
        self.inventory[row["item"]]-=row["qty"]
        row["shipment"]="in_transit"
    def receive(self,id):
        row=self.orders[id]
        must(row["shipment"]=="in_transit","shipment not in transit")
        row["shipment"]="received"
    def pay(self,id):
        row=self.orders[id]
        must(row["contract"]=="confirmed" and row["payment"]=="unpaid","not payable")
        src,dst=row["buyer"],row["seller"]
        must(src in self.balances and dst in self.balances,"unknown account")
        must(self.balances[src]>=row["price"],"insufficient funds")
        self.balances[src]-=row["price"];self.balances[dst]+=row["price"]
        row["payment"]="paid"


class EmploymentV21:
    """Explicit gross, withheld and net amounts. No guessed tax/insurance rates."""
    def __init__(self,employer_funds):
        self.employer_funds=dict(employer_funds)
        self.employees={}
        self.paid=set()
    def hire(self,id,person,employer,site,gross_cents):
        money(gross_cents)
        must(id not in self.employees and bool(site),"invalid contract")
        self.employees[id]=dict(person=person,employer=employer,
                                site=site,gross=gross_cents,status="active")
    def payroll(self,id,period,withheld_cents=None):
        must(id in self.employees,"unknown labor contract")
        row=self.employees[id];must(row["status"]=="active","not employed")
        must((id,period) not in self.paid,"wage paid twice")
        must(withheld_cents is not None,"unknown withholding; cannot invent tax")
        money(withheld_cents);must(withheld_cents<=row["gross"],"withholding too large")
        employer=row["employer"]
        must(employer in self.employer_funds,"unknown employer funds")
        must(self.employer_funds[employer]>=row["gross"],"employer cannot pay")
        self.employer_funds[employer]-=row["gross"]
        self.paid.add((id,period))
        return dict(person=row["person"],gross=row["gross"],
                    withheld=withheld_cents,net=row["gross"]-withheld_cents,
                    withheld_disposition="U_PENDING_REMITTANCE",
                    rule_grade="S_SUPPLIED_FIGURE_NOT_LEGAL_TAX_CALCULATION")


class ServicesV22:
    """Capacity and evidence-dependent school/medical queue, never implied admission."""
    def __init__(self):
        self.providers={}
        self.requests={}
    def provider(self,id,kind,capacity,decision_actor):
        must(id not in self.providers and kind in ("education","medical"),"bad provider")
        must(capacity is None or (type(capacity) is int and capacity>=0),"bad capacity")
        self.providers[id]=dict(kind=kind,capacity=capacity,verifier=decision_actor)
    def request(self,id,provider,person,evidence=None):
        must(id not in self.requests and provider in self.providers,"bad application")
        self.requests[id]=dict(provider=provider,person=person,
                  evidence=evidence,status="pending")
    def decide(self,id,actor,eligible):
        row=self.requests[id];p=self.providers[row["provider"]]
        must(row["status"]=="pending","already decided")
        must(actor==p["verifier"],"authority missing")
        must(row["evidence"] is not None and type(eligible) is bool,
             "missing eligibility evidence")
        if not eligible: row["status"]="rejected"
        elif p["capacity"] is None: row["status"]="awaiting_capacity"
        elif p["capacity"]==0: row["status"]="waitlisted"
        else:
            p["capacity"]-=1;row["status"]="accepted"
        return row["status"]


class AdministrationV23:
    """Procedural authorization. Public law applicability is verified outside this model."""
    def __init__(self):
        self.offices={};self.dockets={}
    def office(self,id,authorizers,rule_id,rule_effective_date):
        self.offices[id]=dict(authorizers=set(authorizers),rule=rule_id,
                              effective=date.fromisoformat(rule_effective_date))
    def file(self,id,office,applicant,at,evidence=None):
        must(id not in self.dockets and office in self.offices,"bad filing")
        must(dt(at).date()>=self.offices[office]["effective"],"rule not yet effective")
        self.dockets[id]=dict(office=office,applicant=applicant,at=dt(at).isoformat(),
                              evidence=evidence,status="submitted")
    def decide(self,id,actor,approve,reason):
        row=self.dockets[id];o=self.offices[row["office"]]
        must(actor in o["authorizers"],"unauthorized public approval")
        must(row["status"]=="submitted" and row["evidence"] is not None,
             "unverified dossier")
        must(type(approve) is bool and bool(reason),"reason required")
        row["status"]="approved" if approve else "denied"
        row["reason"]=reason
        return row["status"]


class InformationV24:
    """Send, deliver, read; rumors never upgraded to verified fact by repeating them."""
    def __init__(self):
        self.messages={};self.knowledge={}
    def send(self,id,sender,recipient,content,at,latency_minutes=0,grade="S_UNVERIFIED"):
        must(id not in self.messages and recipient!=sender,"bad message")
        must(type(latency_minutes) is int and latency_minutes>=0,"bad delay")
        must(grade in ("S_UNVERIFIED","R_VERIFIED_PUBLIC","S_CONFIRMED_SIMULATION"),
             "invalid provenance")
        self.messages[id]=dict(sender=sender,recipient=recipient,content=content,
             sent=dt(at).isoformat(),due=(dt(at)+timedelta(minutes=latency_minutes)).isoformat(),
             status="in_flight",grade=grade)
    def deliver(self,id,at):
        row=self.messages[id]
        must(row["status"]=="in_flight" and dt(at)>=dt(row["due"]),"not delivered yet")
        row["status"]="delivered"
    def read(self,id,actor,at):
        row=self.messages[id]
        must(row["recipient"]==actor,"recipient boundary")
        must(row["status"]=="delivered" and dt(at)>=dt(row["due"]),"not in inbox")
        row["status"]="read"
        self.knowledge.setdefault(actor,[]).append(
            {"content":row["content"],"grade":row["grade"],"message_id":id})


class MacroeconomyV25:
    """Macro references cannot change individual cash without declared micro exposure."""
    def __init__(self):self.series={};self.influences=[]
    def record(self,id,region,metric,period,published,value,unit,source):
        must(id not in self.series and bool(source),"missing data provenance")
        must(date.fromisoformat(period)<=dt(published).date(),"published before measured")
        self.series[id]=dict(region=region,metric=metric,period=period,
             published=dt(published).isoformat(),value=value,unit=unit,source=source)
    def as_known(self,id,at):
        d=self.series[id]
        return d.copy() if dt(d["published"])<=dt(at) else None
    def expose(self,id,actor,reference,coefficient,at):
        must(self.as_known(id,at) is not None,"not published yet")
        must(coefficient is not None and reference is not None,"unquantified exposure")
        must(type(coefficient) in (int,float) and type(reference) in (int,float),
             "invalid modeled exposure")
        record=dict(signal=id,actor=actor,reference=reference,
                    assumed_coefficient=coefficient,impact_estimate=reference*coefficient,
                    grade="S_HYPOTHETICAL_NOT_SETTLED")
        self.influences.append(record)
        return record


class IntegrationV26:
    """Test-only state guard. No mutable connection to official world state."""
    def __init__(self,official_snapshot_bytes):
        self.original=bytes(official_snapshot_bytes)
        self.official_sha=hashlib.sha256(self.original).hexdigest()
        obj=json.loads(self.original)
        must(obj["game_started"] is False and obj["player_character"] is None and
             obj["game_clock_time"] is None and obj["actual_game_events"]==[],
             "official world is not frozen")
        must(len(obj["people"])==31,"unexpected NPC count")
        self.events=[];self.ids=set()
    def record(self,event_id,module,entry,grade="S_TEST"):
        must(event_id not in self.ids,"duplicate cross-system event")
        must(grade=="S_TEST","official event injection denied")
        self.ids.add(event_id)
        event=dict(id=event_id,system=module,detail=entry,grade=grade)
        self.events.append(event)
        return event
    def summary(self,official_snapshot_bytes):
        must(hashlib.sha256(official_snapshot_bytes).hexdigest()==self.official_sha,
             "official world modified")
        return dict(test_only=True,event_count=len(self.events),
                    digest=fingerprint(self.events),
                    official_sha256=self.official_sha,
                    official_game_events_written=0,
                    comprehensive_real_life_simulation=False)
