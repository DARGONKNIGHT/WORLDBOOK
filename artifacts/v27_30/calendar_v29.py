#!/usr/bin/env python3
"""v29 GTFS-compatible service-day gate for *provided* dated static feeds.

No Beijing transit GTFS has been ingested. All sample routes S fixtures.
GTFS can express 25:10:00 (next civil day, service day unchanged). A matched
OSM bus stop does NOT create any boarding service without verified feed data.
"""
from __future__ import annotations
from datetime import date,datetime,timedelta,timezone
import re
VALID_ID=re.compile(r"^[A-Za-z0-9_-]+$")
def gtfs_seconds(v):
    parts=v.split(":")
    if len(parts)!=3 or any(not p.isdigit() for p in parts):
        raise ValueError("GTFS time must be HH:MM:SS")
    h,m,s=map(int,parts)
    if not 0<=h<=47 or not 0<=m<=59 or not 0<=s<=59:
        raise ValueError("GTFS hours 0..47 only; minutes and seconds 0..59")
    return h*3600+m*60+s
class CalendarV29:
    def __init__(self):self.services={};self.exceptions={}
    def add_service(self,id,start,end,weekdays,grade="S_FIXTURE",source=None):
        if id in self.services:raise ValueError("duplicate service_id")
        a,b=date.fromisoformat(start),date.fromisoformat(end)
        if a>b or any(x not in range(7) for x in weekdays):
            raise ValueError("invalid calendar")
        if grade=="R_VERIFIED_SCHEDULE" and not source:
            raise ValueError("verified timetable requires provenance")
        self.services[id]={"from":a,"to":b,"days":set(weekdays),"grade":grade,
                           "source":source}
    def exception(self,id,day,action):
        day=date.fromisoformat(day)
        if action not in ("add","remove"):raise ValueError("bad calendar exception")
        key=id,day
        if key in self.exceptions:raise ValueError("duplicate service/date exception")
        self.exceptions[key]=action
    def service_active(self,id,day):
        """None = no feed-defined service. False = explicit not active."""
        day=date.fromisoformat(day)
        if (id,day) in self.exceptions:
            return self.exceptions[(id,day)]=="add"
        if id not in self.services:return None
        obj=self.services[id]
        return obj["from"]<=day<=obj["to"] and day.weekday() in obj["days"]
    def departure(self,id,service_day,hhmmss,offset_minutes=480):
        eligible=self.service_active(id,service_day)
        if eligible is None:return {"status":"U_NO_VERIFIED_SERVICE_CALENDAR"}
        if not eligible:return {"status":"NO_SCHEDULED_SERVICE_IN_PROVIDED_FEED"}
        t=date.fromisoformat(service_day)
        if type(offset_minutes) is not int or not -720<=offset_minutes<=840:
            raise ValueError("invalid known timezone offset")
        start=datetime(t.year,t.month,t.day,tzinfo=timezone(timedelta(minutes=offset_minutes)))
        dep=start+timedelta(seconds=gtfs_seconds(hhmmss))
        grade=self.services[id]["grade"] if id in self.services else "S_FIXTURE_EXCEPTION_ONLY"
        return {"status":"SCHEDULED_IN_PROVIDED_FEED","local_departure":dep.isoformat(),
                "service_date":service_day,"grade":grade,
                "real_time_arrival":"U","booking_state":"U"}
