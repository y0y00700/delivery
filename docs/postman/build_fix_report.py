"""Keep a credential-free record of the targeted Postman CLI run."""
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/postman'
native = json.loads((ROOT / 'build/postman-results/fix-raw-report.json').read_text(encoding='utf-8-sig'))['run']
log = (ROOT / 'build/postman-results/fix-cli-output.log').read_text(encoding='utf-8-sig')
run_ids = set(re.findall(r'p51_[a-z0-9]+', log))
assert len(run_ids) == 1, 'Expected one run ID'
run_id = run_ids.pop()
entries = []
for execution in native['executions']:
    request = execution['requestExecuted']
    id, name = request['name'].split(' ', 1)
    response = execution.get('response')
    tests = execution.get('tests', [])
    if not response:
        outcome = 'NOT_EXECUTED'
    elif any(test['status'] == 'failed' for test in tests):
        outcome = 'FAIL'
    elif any(test['status'] == 'skipped' for test in tests) or not tests:
        outcome = 'INCOMPLETE'
    else:
        outcome = 'PASS'
    entries.append({
        'id': id, 'name': name, 'method': request['method'],
        'status': response.get('code') if response else None, 'outcome': outcome,
        'checks': [{'name': test['name'], 'status': test['status'],
                    'error': test.get('error', {}).get('message')} for test in tests],
    })

assert len(entries) == 40
counts = Counter(entry['outcome'] for entry in entries)
assert counts == {'PASS': 40} and not native.get('runError'), 'Inspect failures before documenting a successful run'
started = datetime.fromtimestamp(native['meta']['started'] / 1000, timezone(timedelta(hours=9)))
data = {
    'tool': 'Postman CLI 1.70.0', 'startedAt': started.isoformat(), 'runId': run_id,
    'scope': 'Changed behavior and prerequisites; no payment, cancel, or status-transition requests',
    'environment': {'baseUrl': 'http://localhost:8080', 'database': 'PostgreSQL 18.6',
                    'container': 'delivery-db', 'java': '21.0.12.1', 'springBoot': '4.1.1'},
    'nativeSummary': native['summary'], 'runError': native.get('runError'),
    'requestOutcomes': dict(counts), 'requests': entries,
}
(OUT / 'fix-results.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

rows = [f"| {e['id']} | {e['name']} | {e['status'] or '미실행'} | {e['outcome']} |" for e in entries]
assertions = native['summary']['tests']
old = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
previous_failures = sorted({int(re.match(r'\d+', e['id']).group()) for e in old['requests']
                            if e['outcome'] == 'FAIL' and not e['helper']})
passed_previous = [number for number in previous_failures
                   if (group := [e for e in entries if e['id'][0].isdigit()
                                 and int(re.match(r'\d+', e['id']).group()) == number])
                   and all(e['outcome'] == 'PASS' for e in group)]

report = f'''# 5-1. 수정 부분 재검증 결과 — 결제 제외

[문서 안내](./README.md) · [수정 전 전체 기록](./5-1-test-report.md) · [Postman 실행 자료](./postman/README.md)

실행 시각: {started.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Seoul)

실행 식별자: `{run_id}`

환경: Postman CLI 1.70.0 · Spring Boot 4.1.1 · Java 21.0.12.1 · Docker PostgreSQL 18.6

## 결과와 범위

변경 부분과 준비용 요청 **40개 중 {counts['PASS']}개 통과**. Assertion **{assertions['passed']}/{assertions['executed']}개 통과**, 실패 {assertions['failed']}개, 건너뜀 {assertions['skipped']}개다. 실제 HTTP 실행의 요청 오류는 {native['summary']['executedRequests']['errors']}개이며 소요 시간은 {native['meta']['duration'] / 1000:.3f}초다.

기존 컬렉션에서 관련 요청 28개를 선택하고 입력 검증·삭제 메뉴 관련 요청 12개를 추가했다. 로그인 4회는 테스트 준비용이다. 과제 전체 39개 시나리오를 다시 실행한 결과가 아니다.

이전 실패 시나리오 {len(previous_failures)}개 중 이번 실행에서 {len(passed_previous)}개가 통과했다: **{', '.join(map(str, passed_previous))}번**. 각 번호의 역할별 요청을 함께 확인했다. 최초 결과는 [기존 보고서](./5-1-test-report.md)에 보존했다.

**결제 구현·호출, 주문 취소·주문 상태 변경 테스트는 이번 범위에서 제외했다.** 이전에 선행 조건 부족으로 실행하지 못한 모든 항목을 검증했다고 해석하면 안 된다.

## 적용한 수정

| 파일 | 변경과 이유 |
|---|---|
| [RequestOrderCreateDto](../src/main/java/com/example/delivery/dto/order/RequestOrderCreateDto.java) | 숫자 필드의 NotBlank를 NotNull로 교체. quantity의 Min(1)과 주소의 NotBlank 유지. 서버가 결정하는 orderStatus 요청 필드 제거 |
| [UserController](../src/main/java/com/example/delivery/controller/UserController.java) | 회원가입 성공 200 → 201 |
| [MenuController](../src/main/java/com/example/delivery/controller/MenuController.java) | 메뉴 등록 성공 200 → 201 |
| [OrderController](../src/main/java/com/example/delivery/controller/OrderController.java) | 주문 생성 성공 200 → 201 |
| [WebSecurityConfig](../src/main/java/com/example/delivery/config/WebSecurityConfig.java) | GET 메뉴 단건 경로를 비로그인 공개 경로에 추가 |
| [MenuService](../src/main/java/com/example/delivery/service/MenuService.java) | 단건 조회·수정·삭제가 활성 메뉴만 조회하는 공통 메서드 사용. 삭제 메뉴는 404 |
| [ResponseOrderCreateDto](../src/main/java/com/example/delivery/dto/order/ResponseOrderCreateDto.java) | 생성된 주문의 orderId 반환 |
| [OrderService](../src/main/java/com/example/delivery/service/OrderService.java) | 저장된 주문의 ID를 응답 생성자에 전달 |

## 주요 확인 사항

- 회원 4명과 메뉴 1건 생성 성공은 201이었다.
- 비로그인 단건 조회는 활성 메뉴 200, 없는 메뉴·삭제 메뉴 404였다. 인증 없는 메뉴 등록은 403이었다.
- 정상 주문 2건은 201이며 서로 다른 양의 정수 orderId, ORDERED, 수량·주소·서버 계산 금액을 반환했다. 금액은 2개 주문 7000원, 1개 주문 3500원이었다.
- 수량 0·음수, 메뉴 ID·수량·주소 누락 및 null, 공백 주소는 400이었다. OWNER 주문은 403, 없는 메뉴·삭제 메뉴 주문은 404였다.
- 첫 주문 생성 후 고객·사장님 본인 목록은 1건, 다른 고객·사장님 목록은 0건이었다. 실패 요청이 주문을 추가하지 않은 것도 확인했다.
- 다른 사장님의 활성 메뉴 수정·삭제는 403, 본인 수정은 200, 최초 Soft Delete는 204였다. 삭제 메뉴 수정·재삭제는 404였다.
- 메뉴 삭제 이후에도 고객·사장님 목록에서 기존 주문 2건의 ID·메뉴 ID·금액·수량·ORDERED 상태가 보존됐다.

## 실행 상세

번호 01~39는 기존 과제 시나리오 식별자를 유지했고, V1~V9·D1~D3는 이번 수정의 추가 확인이다. 30번의 이름은 원본 컬렉션을 유지했지만 이번에는 주문 생성까지만 실행하고 취소하지 않았다.

| 식별자 | 요청 | 실제 HTTP | 판정 |
|---|---|---|---|
{chr(10).join(rows)}

## 실행 및 데이터 처리

- 수정 소스를 `gradlew.bat bootRun --console=plain`으로 컴파일·기동한 후 실제 localhost:8080 API로 테스트했다. 전체 JUnit 테스트는 실행하지 않았다.
- 최초 샌드박스 실행은 로컬 연결이 EACCES로 차단되어 API에 도달하지 못했다. 로컬 연결 권한을 확보한 뒤 실행한 실제 결과를 위에 기록했다.
- Postman CLI 실제 실행 종료 코드는 0이다. 클라우드 로그인·게시 없이 로컬 결과를 사용했다.
- 이번 실행에서 회원 4명, 메뉴 1건, 주문 2건을 생성했다. 테스트 메뉴만 Soft Delete했고 주문 2건은 ORDERED로 남았다. 기존 데이터 삭제나 주문 상태 강제 변경은 하지 않았다.
- 이번에 시작한 테스트 API 프로세스만 실행 경로를 확인한 후 종료했다. Docker DB는 유지했다.
- 기존 전체 테스트 보고서와 원본 컬렉션은 보존했다. 공유용 결과에는 JWT·비밀번호·요청 본문을 포함하지 않았다.

## 재현 자료

- [부분 재검증 컬렉션](./postman/delivery-5-1-fix-retest.postman_collection.json)
- [환경 파일](./postman/delivery-local.postman_environment.json)
- [컬렉션 생성 스크립트](./postman/generate_fix_retest.py)
- [개별 assertion 결과 JSON](./postman/fix-results.json)
- [보고서 생성 스크립트](./postman/build_fix_report.py)

API 서버 실행 후 프로젝트 루트에서 다음 PowerShell 명령을 사용한다.

```powershell
& '.\\build\\postman-cli\\postman-cli.exe' collection run 'docs/postman/delivery-5-1-fix-retest.postman_collection.json' `
  --environment 'docs/postman/delivery-local.postman_environment.json' `
  --no-report-events --timeout-request 10000 --timeout-script 10000 `
  --reporters cli,json `
  --reporter-json-export 'build/postman-results/fix-raw-report.json' `
  --reporter-json-omitAllHeadersAndBody
```
'''
(ROOT / 'docs/5-1-fix-retest-report.md').write_text(report, encoding='utf-8')
print(json.dumps({'runId': run_id, 'requests': dict(counts), 'assertions': assertions,
                  'previousFailedScenariosNowPassed': passed_previous}, ensure_ascii=False))
