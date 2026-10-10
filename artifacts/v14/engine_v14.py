#!/usr/bin/env python3
"""EARTH REALITY v14 deterministic sandbox event simulator.

Standard library only; never writes to the frozen v13 world-state.
The actors, locations, money and messages in demonstration cases are S-grade
synthetic assumptions, NOT verified details of residents or real institutions.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from decimal import Decimal
import copy
import hashlib
import heapq
import json


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def aware(value):
    when = datetime.fromisoformat(value) if isinstance(value, str) else value
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError('必须采用带时区的完整时间戳')
    return when


class SandboxEngine:
    """Priority-ordered discrete-event engine with hash-chained effect journal."""
    def __init__(self, baseline, people, balances_cents, locations, permissions=None):
        self.anchor = aware(baseline)
        self.people = set(people)
        self.permissions = copy.deepcopy(permissions or {})
        self.initial_state = {
            'balances_cents': copy.deepcopy(balances_cents),
            'locations': copy.deepcopy(locations),
            'busy_until': {},
            'transit': {},
            'knowledge': {person: [] for person in people},
            'transactions': [],
            'ledger': [],
            'approved': []
        }
        self.state = copy.deepcopy(self.initial_state)
        self.queue = []
        self.seq = 0
        self.event_ids = set()
        self.journal = []
        self.prev_hash = '0'*64
        self.current_time = self.anchor

    def schedule(self, event_id, when, kind, actor=None, priority=50, **payload):
        when = aware(when)
        if event_id in self.event_ids:
            raise ValueError(f'计划事件编号重复: {event_id}')
        if when < self.anchor:
            raise ValueError('测试事件不能早于测试锚点')
        self.event_ids.add(event_id)
        e = {'event_id': event_id, 'when': when.isoformat(), 'kind': kind,
             'actor': actor, 'payload': payload, 'priority': priority}
        heapq.heappush(self.queue, (when, priority, self.seq, e))
        self.seq += 1

    @staticmethod
    def apply_effect(state, effect):
        op=effect['op']
        if op=='set':
            state[effect['field']][effect['key']] = copy.deepcopy(effect['value'])
        elif op=='remove':
            state[effect['field']].pop(effect['key'], None)
        elif op=='add_knowledge':
            who=effect['person']
            item=effect['item']
            if item not in state['knowledge'][who]:
                state['knowledge'][who].append(item)
        elif op=='transfer':
            src,dst,cents,tid=effect['source'],effect['target'],effect['cents'],effect['transaction_id']
            state['balances_cents'][src] -= cents
            state['balances_cents'][dst] += cents
            state['transactions'].append(tid)
            state['ledger'].extend([
                {'tx':tid,'account':src,'delta_cents':-cents,'currency':'CNY'},
                {'tx':tid,'account':dst,'delta_cents':cents,'currency':'CNY'}])
        elif op=='approval':
            state['approved'].append({'actor':effect['actor'],'scope':effect['scope']})
        else:
            raise ValueError('未知效果: '+op)

    def _busy(self, actor, when):
        until=self.state['busy_until'].get(actor)
        return bool(until and when < aware(until))

    def _perform(self, e, when):
        kind, actor, p=e['kind'],e['actor'],e['payload']
        effects=[]
        if kind=='routine_check':
            if actor not in self.people: return False,'人物编号不存在',[]
            # Observational tick: never implies that an occupation/day's work took place.
            return True,'后台状态检查，不推定具体生活行为',[]
        if actor not in self.people:
            return False,'人物编号不存在',[]
        if kind=='activity':
            duration=p.get('minutes',0)
            place=p.get('location')
            if not isinstance(duration,int) or duration<0: return False,'活动时长无效',[]
            if self._busy(actor,when): return False,'时间被其他活动占用',[]
            if place is not None and self.state['locations'].get(actor)!=place:
                return False,'地点不符，禁止瞬间移动',[]
            effects.append({'op':'set','field':'busy_until','key':actor,
                            'value':(when+timedelta(minutes=duration)).isoformat()})
            return True,'活动登记',effects
        if kind=='travel':
            duration=p.get('minutes',0)
            origin=p.get('origin')
            target=p.get('destination')
            if not isinstance(duration,int) or duration<=0: return False,'旅行必须耗费正时间',[]
            if self._busy(actor,when): return False,'出行与活动冲突',[]
            if not target or origin==target or self.state['locations'].get(actor)!=origin:
                return False,'出发地不符或目标无效',[]
            arrival_at=(when+timedelta(minutes=duration)).isoformat()
            effects.extend([
                {'op':'set','field':'busy_until','key':actor,'value':arrival_at},
                {'op':'set','field':'transit','key':actor,'value':target}])
            self.schedule(e['event_id']+':arrive',arrival_at,'travel_arrive',actor,priority=10,destination=target)
            return True,'已出发，位置在抵达事件后更新',effects
        if kind=='travel_arrive':
            target=p.get('destination')
            if self.state['transit'].get(actor)!=target:
                return False,'没有相符的在途记录',[]
            effects.extend([
                {'op':'set','field':'locations','key':actor,'value':target},
                {'op':'remove','field':'transit','key':actor}])
            return True,'实际到达后改变地点',effects
        if kind=='message_send':
            recipient=p.get('recipient')
            lag=p.get('delay_minutes',1)
            topic=p.get('topic')
            if recipient not in self.people or recipient==actor: return False,'接收人无效',[]
            if not isinstance(lag,int) or lag<=0: return False,'消息传递延迟无效',[]
            if not topic: return False,'消息主题为空',[]
            self.schedule(e['event_id']+':deliver',when+timedelta(minutes=lag),'message_deliver',actor,
                          priority=20,recipient=recipient,topic=topic,origin_event=e['event_id'])
            return True,'已发送，接收者尚未知情',[]
        if kind=='message_deliver':
            recipient=p.get('recipient')
            if recipient not in self.people: return False,'接收人无效',[]
            effects.append({'op':'add_knowledge','person':recipient,'item':p['topic']})
            # A deliberately narrow hypothetical response policy, not a general claim
            # about any real/fictional person's psychology or guaranteed compliance.
            if recipient=='P006' and p['topic']=='shift_notice':
                self.schedule(e['event_id']+':policy_reply',when+timedelta(minutes=25),
                              'message_send','P006',recipient='P005',topic='shift_notice_ack',delay_minutes=10)
            return True,'接收者实际获得信息',effects
        if kind=='transfer':
            target=p.get('target')
            cents=p.get('cents')
            tx=p.get('transaction_id')
            if target not in self.state['balances_cents'] or actor not in self.state['balances_cents']:
                return False,'账户未知，不能将未知余额当作零',[]
            if target==actor or not isinstance(cents,int) or isinstance(cents,bool) or cents<=0:
                return False,'金额或收付款方无效',[]
            if not tx or tx in self.state['transactions']:
                return False,'交易编号重复或为空',[]
            if self.state['balances_cents'][actor]<cents:
                return False,'余额不足，不可透支',[]
            effects.append({'op':'transfer','source':actor,'target':target,
                            'cents':cents,'transaction_id':tx})
            return True,'双方账本同时过账',effects
        if kind=='approve':
            scope=p.get('scope')
            if scope not in self.permissions.get(actor,[]):
                return False,'权限不足，不能批准',[]
            effects.append({'op':'approval','actor':actor,'scope':scope})
            return True,'已按沙盒声明权限办理',effects
        return False,'未定义的事件类型',[]

    def run(self, until):
        until=aware(until)
        if until < self.current_time: raise ValueError('不可回退已运行的模拟时钟')
        while self.queue and self.queue[0][0] <= until:
            when,_,_,event=heapq.heappop(self.queue)
            self.current_time=when
            success,reason,effects=self._perform(event,when)
            if success:
                for effect in effects:
                    self.apply_effect(self.state,effect)
            entry={
                'event_id':event['event_id'], 'at':when.isoformat(),
                'kind':event['kind'], 'actor':event['actor'],
                'status':'completed' if success else 'rejected',
                'reason':reason,'effects':effects if success else [],
                'prev_hash':self.prev_hash,
            }
            entry['hash']=digest(entry)
            self.prev_hash=entry['hash']
            self.journal.append(entry)
        self.current_time=until
        return self

    def audit(self):
        problems=[]
        transactions={}
        for row in self.state['ledger']:
            transactions.setdefault((row['tx'],row['currency']),0)
            transactions[(row['tx'],row['currency'])]+=row['delta_cents']
        for tx,net in transactions.items():
            if net!=0: problems.append(f'不平衡交易: {tx}: {net}')
        if any(n<0 for n in self.state['balances_cents'].values()):
            problems.append('出现负余额')
        if sum(self.initial_state['balances_cents'].values())!=sum(self.state['balances_cents'].values()):
            problems.append('内部资金非守恒')
        replay=copy.deepcopy(self.initial_state)
        prev='0'*64
        for ent in self.journal:
            assert ent['prev_hash']==prev, '历史哈希链断裂'
            assert ent['hash']==digest({k:v for k,v in ent.items() if k!='hash'}), '历史被修改'
            prev=ent['hash']
            for effect in ent['effects']:
                self.apply_effect(replay,effect)
        if replay!=self.state:
            problems.append('不能由效果事件历史重建当前状态')
        return problems

    def report(self):
        success=sum(e['status']=='completed' for e in self.journal)
        rejected=[{'event_id':e['event_id'],'reason':e['reason']} for e in self.journal if e['status']=='rejected']
        return {
            'test_only':True, 'sandbox_anchor':self.anchor.isoformat(),
            'sandbox_end':self.current_time.isoformat(),
            'records':len(self.journal),'completed':success,'rejected':len(rejected),
            'rejection_examples':rejected,
            'transfers':len(self.state['transactions']),
            'knowledge_records':sum(len(v) for v in self.state['knowledge'].values()),
            'approved_actions':len(self.state['approved']),
            'initial_internal_total_cents':sum(self.initial_state['balances_cents'].values()),
            'final_internal_total_cents':sum(self.state['balances_cents'].values()),
            'audit_violations':self.audit(),
            'state_sha256':digest(self.state),
            'journal_final_sha256':self.prev_hash
        }