#!/usr/bin/env python3
"""v13.0 basic worldbook consistency checks; Python 3, standard library only.

Scope: machine-checkable metadata, NPC registry, links, event freeze and ledger invariants.
Not a legal auditor, a live-world simulator or a source verification crawler.
"""
from __future__ import annotations
import copy
import datetime as dt
import json
import pathlib
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation

BASE = pathlib.Path(__file__).resolve().parent
STATE = BASE / 'world_state_v13.json'
ALLOWED_GRADES = {'R', 'S', 'U'}
ALLOWED_EVENT_STATES = {'candidate','scheduled','in_progress','completed','cancelled','failed','unverified'}


def _date(value, label, errors):
    if value is None: return None
    try: return dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        errors.append(f'{label} 日期格式无效: {value!r}')
        return None


def validate(state):
    errors, warnings = [], []
    baseline = _date(state.get('baseline_game_date'), 'baseline_game_date', errors)
    if state.get('schema_version') != '13.0': errors.append('schema_version 不是 13.0')
    if state.get('worldbook_versions_inherited') != list(range(2,13)): errors.append('版本继承链不是 v2-v12')
    if state.get('phase') != 'worldbuilding_frozen' or state.get('game_started') is not False:
        errors.append('不处于世界书冻结状态')
    if state.get('game_clock_time') is not None: errors.append('游戏时刻未授权设定')
    if state.get('player_character') is not None: errors.append('擅自创建玩家角色')
    if state.get('player_home_location') is not None: errors.append('擅自指定玩家住所')
    geo = state.get('geography', {})
    if (geo.get('country'), geo.get('city'), geo.get('district_observation'), geo.get('town_observation'), geo.get('village_observation')) != ('中国','北京市','顺义区','北小营镇','前礼务村'):
        errors.append('观察样本的地理继承关系被破坏')
    if geo.get('observation_only') is not True: errors.append('观察样本误被设为玩家位置')
    if geo.get('selection_history',{}).get('reproducible') is not False:
        errors.append('无随机种子却声明抽样过程可复现')
    if geo.get('selection_history',{}).get('random_seed') is not None:
        warnings.append('出现v6未保存过的随机种子，请核对是否事后补写')

    people=state.get('people', [])
    ids=[p.get('id') for p in people]
    expected={f'P{i:03d}' for i in range(1,32)}
    if len(people)!=31 or set(ids)!=expected or len(set(ids))!=31:
        errors.append('人物必须为唯一的P001-P031，共31名')
    by_id={p.get('id'):p for p in people}
    counts=Counter(p.get('tier') for p in people)
    if counts != {'core':15,'candidate':16}: errors.append('人物精度分层必须为核心15人+候选16人')
    for p in people:
        ident=p.get('id')
        if not p.get('name'): errors.append(f'{ident} 缺少姓名')
        if p.get('fact_grade') != 'S': errors.append(f'{ident} 虚构人物被冒充为现实事实')
        age=p.get('age_years_at_baseline')
        if not isinstance(age,int) or not 0 <= age <= 120: errors.append(f'{ident} 年龄无效')
        if p.get('birth_date') is not None:
            birthday=_date(p['birth_date'],ident+' 生日',errors)
            if birthday and baseline and birthday>baseline: errors.append(f'{ident} 出生日期晚于世界基准')
            if p.get('date_precision') != 'day': errors.append(f'{ident} 已有生日但精度标签未更新')
        if p.get('birth_date') is None and p.get('date_precision') != 'age_year_only':
            errors.append(f'{ident} 未知生日的精度标记错误')
        if p.get('cash_balance_cny') is not None and not isinstance(p['cash_balance_cny'],(int,float)):
            errors.append(f'{ident} 资金不是数值或未知')
    if sum(p.get('birth_date') is None for p in people):
        warnings.append('31名虚构人物仅有整数年龄，真实生日均未设定')
    if sum(p.get('cash_balance_cny') is None for p in people):
        warnings.append('31名虚构人物的现金余额仍为未知，不可当成0元')
    if by_id.get('P010',{}).get('known_location_note') != '在外省生活，具体省份未知':
        errors.append('周玉兰的外省省份不得被未经设定擅自确定')

    groups=state.get('groups',[])
    if {g.get('id') for g in groups} != {'F01','F02','F03','F04','F05'} or len(groups)!=5:
        errors.append('原有5组关系网络编号不一致')
    sizes={'F01':4,'F02':3,'F03':3,'F04':3,'F05':2}
    membership=[]
    for g in groups:
        gid=g.get('id')
        members=g.get('members',[])
        if gid in sizes and len(members) != sizes[gid]: errors.append(f'{gid} 人员数量错误')
        membership.extend(members)
        if len(set(members)) != len(members): errors.append(f'{gid} 重复列入成员')
        if gid in ('F04','F05') and g.get('type') == 'family_network':
            errors.append(f'{gid} 非家庭关系网络被误设为家庭')
        if g.get('co_residence_confirmed') is True: warnings.append(f'{gid} 同住事实原版本未确认')
    if set(membership) != {f'P{i:03d}' for i in range(1,16)} or len(membership)!=15:
        errors.append('原有15名核心NPC未正确且唯一地分配至五个关系组')
    for p in people:
        if p.get('tier')=='core' and p.get('group_id') not in sizes: errors.append(f"{p['id']} 缺少所属关系组")
        if p.get('tier')=='candidate' and p.get('group_id') is not None: errors.append(f"{p['id']} 不能被事后强制加入原5组")
        if p.get('tier')=='core':
            g=next((g for g in groups if g['id']==p.get('group_id')), None)
            if g and p['id'] not in g['members']: errors.append(f"{p['id']} 人物归属与关系组名单冲突")
    rels=state.get('relationships',[])
    rel_unique=set()
    for r in rels:
        a,b,kind=r.get('source_id'),r.get('target_id'),r.get('kind')
        if a not in by_id or b not in by_id or a==b: errors.append(f'无效关系端点: {a}->{b}')
        key=(a,b,kind)
        if key in rel_unique: errors.append(f'重复关系: {key}')
        rel_unique.add(key)
        if r.get('fact_grade')!='S': errors.append(f'模拟关系错误标记为现实: {key}')
        if kind=='parent_of' and a in by_id and b in by_id:
            if by_id[a]['age_years_at_baseline'] - by_id[b]['age_years_at_baseline'] < 12:
                warnings.append(f'父母子女年龄差需人工复核: {a}->{b}')
        if kind=='spouse' and a in by_id and b in by_id:
            if by_id[a].get('marital_status')!='已婚' or by_id[b].get('marital_status')!='已婚': errors.append(f'配偶关系婚姻标记冲突: {a}-{b}')

    sources=state.get('sources', [])
    sid=[s.get('id') for s in sources]
    if len(sid)!=len(set(sid)): errors.append('来源编号重复')
    for s in sources:
        if s.get('grade') not in ALLOWED_GRADES: errors.append(f"{s.get('id')} 来源类型不合法")
        pub=_date(s.get('published_on'), s.get('id','?')+' published_on', errors)
        ref=_date(s.get('reference_period'), s.get('id','?')+' reference_period', errors)
        if pub and baseline and pub>baseline: errors.append(f"{s.get('id')} 使用了游戏基准日期之后发布的数据")
        if s.get('grade')=='R' and (not s.get('url') or not s.get('scope') or pub is None):
            errors.append(f"{s.get('id')} 已核实现实事实缺少来源、范围或发布日期")
        if ref and baseline and ref>baseline and pub and pub<=baseline:
            warnings.append(f"{s.get('id')} 属于基准日期时已公布的未来日程，非已发生历史")
        if s.get('grade')=='U' and s.get('verification')=='publication_date_not_confirmed_for_baseline':
            warnings.append(f"{s.get('id')} 基准时点公开状态未被确认，保持待核")

    events=state.get('actual_game_events', [])
    sched=state.get('scheduled_game_events', [])
    if events or sched: errors.append('世界书冻结期间不允许出现实际游戏历史事件或已安排游戏事件')
    ev_ids=[e.get('event_id') for e in events+sched]
    if len(ev_ids)!=len(set(ev_ids)): errors.append('事件编号重复')
    for e in events+sched:
        if e.get('status') not in ALLOWED_EVENT_STATES: errors.append('事件状态非法')
        occured=_date(e.get('occurred_on'), 'event.occurred_on', errors)
        if occured and baseline and occured>baseline: errors.append('游戏事件发生在未授权推进的未来')
    ledger=state.get('financial_ledger',[])
    transactions={}
    for row in ledger:
        tx=row.get('transaction_id')
        cur=row.get('currency')
        if not tx or not cur: errors.append('资金分录缺少交易编号或货币');continue
        try: delta=Decimal(str(row['delta']))
        except (KeyError,InvalidOperation): errors.append('资金分录金额无效');continue
        transactions[(tx,cur)]=transactions.get((tx,cur), Decimal('0'))+delta
    for (tx,cur),total in transactions.items():
        if total != 0: errors.append(f'交易{tx}({cur})借贷不平衡: {total}')
    if ledger: errors.append('世界书冻结期不应出现已执行资金分录')
    return errors,warnings


def run_selftests(state):
    tests=[]
    cases=[
        ('正常冻结档案', None, False),
        ('重复人物编号',lambda d:d['people'].__setitem__(1,dict(d['people'][1],id='P001')), True),
        ('偷建玩家角色',lambda d:d.__setitem__('player_character',{'name':'未授权'}),True),
        ('世界日期后发生事件',lambda d:d['actual_game_events'].append({'event_id':'E-BAD','occurred_on':'2026-10-11','status':'completed'}),True),
        ('资金守恒异常',lambda d:d['financial_ledger'].append({'transaction_id':'TX-BAD','currency':'CNY','delta':'100.00'}),True),
        ('未经确认指定母亲省份',lambda d:d['people'][9].__setitem__('known_location_note','山东省'),True),
        ('冒用玩家住址',lambda d:d.__setitem__('player_home_location','前礼务村'),True),
    ]
    for name,modify,should_fail in cases:
        candidate=copy.deepcopy(state)
        if modify:modify(candidate)
        errs,_=validate(candidate)
        passed=bool(errs)==should_fail
        tests.append((name, passed, errs[:2]))
    return tests


def main():
    data=json.loads(STATE.read_text(encoding='utf-8'))
    errs,warns=validate(data)
    tests=run_selftests(data)
    print(f'主存档审计：{len(errs)} 个错误，{len(warns)} 个提示')
    for item in errs: print('ERROR',item)
    for item in warns:print('NOTE ',item)
    print(f'自检用例：{sum(x[1] for x in tests)}/{len(tests)} 通过')
    for name,passed,issues in tests:
        print(('PASS' if passed else 'FAIL'),name, '; '.join(issues))
    return 0 if not errs and all(x[1] for x in tests) else 1


if __name__=='__main__':
    sys.exit(main())