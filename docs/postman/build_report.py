"""Rebuild the historical initial-run report; narrative is specific to 2026-10-08."""
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'postman'
native = json.loads((ROOT / 'build/postman-results/raw-report.json').read_text(encoding='utf-8-sig'))['run']
log = (ROOT / 'build/postman-results/cli-output.log').read_text(encoding='utf-8-sig')
run_ids = sorted(set(re.findall(r'p51_[a-z0-9]+', log)))
assert len(run_ids) == 1, run_ids
run_id = run_ids[0]
entries = []
for execution in native['executions']:
    request = execution['requestExecuted']
    id, name = request['name'].split(' ', 1)
    tests = execution.get('tests', [])
    response = execution.get('response')
    if response:
        outcome = 'FAIL' if any(t['status'] == 'failed' for t in tests) else 'PASS'
        reason = '; '.join(t.get('error', {}).get('message', '') for t in tests if t['status'] == 'failed')
    else:
        reason = '; '.join(t['name'] for t in tests)
        outcome = 'NOT_IMPLEMENTED' if 'NOT_IMPLEMENTED' in reason else 'BLOCKED'
    entries.append({'id': id, 'name': name, 'helper': id.endswith('H') or id == '99',
                    'method': request['method'], 'status': response.get('code') if response else None,
                    'outcome': outcome, 'reason': reason,
                    'checks': [{'name': t['name'], 'status': t['status'],
                                'error': t.get('error', {}).get('message')} for t in tests]})

grouped = defaultdict(list)
for entry in entries:
    if not entry['helper']:
        grouped[int(re.match(r'\d+', entry['id']).group())].append(entry)
assert set(grouped) == set(range(1, 40))
step_outcomes = {}
for number, group in grouped.items():
    states = {e['outcome'] for e in group}
    step_outcomes[number] = next(s for s in ['FAIL','NOT_IMPLEMENTED','BLOCKED','PASS'] if s in states)

counts = Counter(e['outcome'] for e in entries)
steps = Counter(step_outcomes.values())
started = datetime.fromtimestamp(native['meta']['started']/1000, timezone(timedelta(hours=9)))
data = {'tool': 'Postman CLI 1.70.0', 'startedAt': started.isoformat(), 'runId': run_id,
        'environment': {'baseUrl': 'http://localhost:8080', 'database':'PostgreSQL 18.6',
                        'container':'delivery-db','java':'21.0.12.1','springBoot':'4.1.1'},
        'nativeSummary':native['summary'],'runError':native.get('runError'),
        'requestOutcomes':dict(counts),'assignmentStepOutcomes':dict(steps), 'requests':entries}
(OUT/'results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

labels={'PASS':'통과','FAIL':'실패','BLOCKED':'선행 조건 미충족','NOT_IMPLEMENTED':'미구현'}
rows=[]
for number in range(1,40):
    group=grouped[number]
    status=' / '.join(e['id']+': '+(str(e['status']) if e['status'] else '미실행') for e in group)
    names=' / '.join(e['name'] for e in group)
    if number in [1,2,3,4,11]: note='저장은 성공했으나 201 대신 200'
    elif number==14: note='비로그인 단건 조회가 403으로 차단됨'
    elif number in [17,18,19,30,38]: note='주문 생성 요청이 500. 후속 비즈니스 규칙을 확인할 수 없음'
    elif number in [20,21]: note='목록은 200. 주문 생성 실패로 본인 주문 1건 대신 빈 배열; 타 계정도 빈 배열. 데이터가 있을 때의 조회 범위는 미검증'
    elif number==37: note='삭제 표시 메뉴를 조회했지만 200'
    elif step_outcomes[number]=='NOT_IMPLEMENTED': note='결제 API가 없어 요청하지 않음'
    elif step_outcomes[number]=='BLOCKED': note='주문 ID 또는 필요한 상태를 만들지 못해 요청하지 않음'
    else: note='기대 상태 코드 및 해당 데이터 검증 통과'
    rows.append(f'| {number} | {names} | {status} | {labels[step_outcomes[number]]} | {note} |')

report=f'''# 5-1. 수정 전 전체 테스트 기록

[문서 안내](./README.md) · [수정 후 부분 재검증](./5-1-fix-retest-report.md) · [Postman 실행 자료](./postman/README.md)

> 이 문서는 2026-10-08 16:42의 수정 전 실행 기록이다. 아래 실패 수치와 원인 설명은 당시 상태를 보존한 것이며, 현재 구현 상태는 문서 안내와 수정 후 재검증 보고서를 기준으로 확인한다.

실행 시각: {started.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Seoul)

실행 도구: **Postman CLI 1.70.0** · 반복 1회 · 실제 HTTP 서버 및 Docker PostgreSQL 사용

실행 식별자: `{run_id}`

## 결과

과제 5-1의 **39개 시나리오 중 {steps['PASS']}개 통과, {steps['FAIL']}개 실패, {steps['BLOCKED']}개 선행 조건 미충족, {steps['NOT_IMPLEMENTED']}개 결제 미구현**이다. 실패는 요구사항 기준 판정이며, 실패 개수가 서로 다른 버그 개수를 의미하지 않는다.

| 집계 단위 | 결과 |
|---|---|
| 과제 원문 번호 1~39 | 통과 {steps['PASS']} / 실패 {steps['FAIL']} / 선행 조건 미충족 {steps['BLOCKED']} / 미구현 {steps['NOT_IMPLEMENTED']} |
| 역할별 분리 및 보조 요청 포함 53개 | 실제 HTTP 34개: 통과 {counts['PASS']} / 실패 {counts['FAIL']}; 미실행 19개: 선행 조건 미충족 {counts['BLOCKED']} / 미구현 {counts['NOT_IMPLEMENTED']} |
| Assertion 75개 | 통과 37 / 실패 19 / 건너뜀 19 |
| 네트워크·스크립트 실행 오류 | 0 |
| 소요 시간 | {native['meta']['duration']/1000:.3f}초 |

원문에서 여러 역할·동작을 한 번호로 묶은 경우 분리 호출했다. 하나라도 실패하면 해당 번호는 실패로 집계한다. 보조 요청 6개는 원문 39개 집계에 포함하지 않는다. 주문 생성 이후 단계는 DB에 가짜 주문·결제 상태를 넣어 통과시키지 않았다.

## 실행 환경과 변경 범위

- API: `http://localhost:8080`, Spring Boot 4.1.1, Java 21.0.12.1.
- DB: `delivery-db` 컨테이너, PostgreSQL **18.6**, 호스트 5432 → 컨테이너 5432, DB `delivery`.
- 서버가 꺼져 있어 당시 소스를 `gradlew.bat bootRun --console=plain`으로 시작해 검증했다. 테스트 종료 후 이번에 시작한 API 프로세스만 종료했고 Docker DB는 유지했다.
- 기능 소스는 수정하지 않았다. 테스트 회원 4명과 메뉴 1개를 API로 생성했고, 해당 메뉴만 Soft Delete했다. 기존 데이터 정리나 DB 상태 강제 변경은 하지 않았다.
- Postman 앱 실행을 시도한 뒤 사용자의 선택에 따라 CLI로 같은 컬렉션을 실행했다. 앱 UI의 Collection Runner에서 실행한 결과라고 표현하지 않는다.
- CLI 실행 파일은 공식 배포본을 `build/postman-cli`에 내려받아 `Postman, Inc.`의 유효한 서명을 확인했다. 시스템 PATH나 에이전트 설정은 수정하지 않았다.
- 로컬 컬렉션으로 실행했다. CLI에 클라우드 로그인 정보가 없어 클라우드 게시가 되지 않았으며 로컬 JSON 결과는 정상 생성됐다. 실패 assertion 때문에 종료 코드는 1이다.

## 필수 기능 12개 기준

| 기능 | 판정 | 확인 내용 |
|---|---|---|
| 1. 회원가입 | 일부 불일치 | 4명 저장·BCrypt·입력 검증·중복 거절 확인. 성공 코드 200 → 과제 기대 201 |
| 2. 로그인 | 통과 | 4명 JWT 발급, 잘못된 비밀번호 401, 발급 토큰으로 후속 API 호출 |
| 3. 메뉴 등록 | 일부 불일치 | OWNER 등록·CUSTOMER 거절·가격 검증 확인. 성공 코드 200 → 과제 기대 201 |
| 4. 메뉴 목록 | 통과 | 비로그인 목록 및 삭제 메뉴 제외 |
| 5. 메뉴 단건 조회 | 실패 | 비로그인 요청 403, 로그인 후 삭제 메뉴 조회 200 |
| 6. 메뉴 수정 | 5-1 범위 통과 | 본인 가격 3500원 수정, 다른 사장님 403, DB 수정 반영 |
| 7. 메뉴 삭제 | 5-1 범위 통과 | 다른 사장님 403, 본인 204, 행 유지 및 deleted_at 저장 |
| 8. 주문 생성 | 실패 | 정상·역할 위반·수량 0·삭제 메뉴 요청 모두 500 |
| 9. 주문 목록 | 부분 확인 | 4명 모두 빈 배열 200. 주문 생성 실패로 데이터가 있을 때의 역할별 분리는 미검증 |
| 10. 주문 취소 | 검증 불가 | 생성된 주문이 없어 선행 조건 미충족 |
| 11. 주문 상태 변경 | 검증 불가 | 생성된 주문 및 PAID 상태를 만들 수 없어 선행 조건 미충족 |
| 12. 결제 | 미구현 | 결제 엔티티·API가 없고 payments 테이블도 없음 |

## 주요 실패와 원인

1. **생성 응답 코드:** 회원가입 4회와 메뉴 등록이 200이다. 과제는 201을 요구한다. 당시 Controller의 `ResponseEntity.ok()`와 일치한다.
2. **비로그인 메뉴 단건 조회:** 기존·없는 ID 모두 403이다. Security 설정이 메뉴 목록 경로만 공개한다.
3. **주문 생성 500:** 정상 주문도 실패해 DB에 주문이 생기지 않았다. 소스상 `RequestOrderCreateDto`의 Long 필드에 문자열용 `@NotBlank`가 적용되어 있다. 숫자 필드의 검증을 수정한 후 HTTP로 재검증해야 한다. 주문 총액·주문 취소·역할별 주문 데이터 범위가 이번에 검증된 것은 아니다.
4. **삭제 메뉴 조회:** 삭제 후 인증된 단건 조회가 200이다. `MenuService.searchMenuOne()`은 `findById()`를 사용해 삭제 표시를 필터링하지 않는다.
5. **결제 미구현:** 원문 23·24·25·33번을 미구현으로 기록했다. 주문 상태를 PAID로 바꾸는 정상 API 흐름이 없다.

18번에는 생성 응답의 주문 ID 검사도 들어 있다. 이번에는 응답 자체가 500이므로 ID 누락을 별도의 실행 확인 버그로 세지 않는다. 당시 성공 DTO에 orderId가 없다는 점도 소스에서 확인했다. 이후 생성 응답에 ID를 추가했으며 수정 후 보고서에 검증 결과를 기록했다.

## 39개 시나리오 상세

| 번호 | 실행 내용 | 실제 HTTP | 판정 | 비고 |
|---|---|---|---|---|
{chr(10).join(rows)}

## ⑥ PostgreSQL 직접 확인

읽기 전용 트랜잭션에서 이번 실행의 데이터만 조회했다. [실행 SQL](./postman/db-checks.sql)과 [조회 결과](./postman/db-checks-result.txt)를 남겼다.

| 확인 항목 | 결과 |
|---|---|
| 비밀번호 BCrypt 저장 | 회원 4명 모두 BCrypt 형식·60자 확인. 해시 원문은 보고서에 저장하지 않음 |
| 생성·수정 시각 | 이번 회원 4명·메뉴 1개에 모두 기록됨. 주문은 0건이어서 주문 데이터의 시각은 미검증 |
| 메뉴 수정 시각 변경 | 메뉴 modified_at > created_at 확인 |
| 결제 7000원 기록 1건 | 미확인: payments 테이블 자체가 없음 |
| 역할·주문 상태 문자열 저장 | users.user_type과 orders.order_status는 character varying. 회원 역할 값 OWNER/CUSTOMER 확인. 주문은 0건이므로 저장된 enum 값 확인 불가 |
| 메뉴 Soft Delete | menu_id=1, 가격 3500원, 행이 남아 있고 deleted_at이 채워짐 |
| 주문 기록 보존 | 이번 실행 주문 0건. 삭제 메뉴의 기존 주문 보존은 검증 불가 |

남아 있는 테스트 데이터: 회원 `{run_id}_owner1`, `{run_id}_owner2`, `{run_id}_cust1`, `{run_id}_cust2`와 삭제 표시된 테스트 메뉴 1건. 테스트 결과 추적을 위해 회원과 메뉴 행은 유지했다.

## 재실행 자료

- [Postman 컬렉션](./postman/delivery-5-1.postman_collection.json)
- [로컬 환경](./postman/delivery-local.postman_environment.json)
- [실행 안내](./postman/README.md)
- [요청별 결과 JSON](./postman/results.json) — 요청 본문·JWT·비밀번호를 포함하지 않는 요약

원본 CLI 결과는 Git에서 제외되는 `build/postman-results/raw-report.json`과 `cli-output.log`에 있다. 스크립트 생성·실행에는 [Postman 공식 CLI 문서](https://learning.postman.com/docs/postman-cli/postman-cli-collections)와 [보고서 옵션](https://learning.postman.com/docs/postman-cli/postman-cli-reporters/)을 참고했다. 이번 결과는 이전 로컬 H2 테스트와 별도의 PostgreSQL 실행 결과다.
'''
(ROOT/'docs/5-1-test-report.md').write_text(report, encoding='utf-8')
print(json.dumps({'requests':dict(counts),'steps':dict(steps),'runId':run_id},ensure_ascii=False))
