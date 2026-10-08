# Postman 테스트 자료와 실행 안내

[프로젝트 README](../../README.md) · [문서 안내](../README.md) · [최신 부분 재검증](../5-1-fix-retest-report.md)

기준: 2026-10-08. 저장된 결과는 **Postman CLI로 실제 Spring Boot API와 Docker PostgreSQL을 호출한 기록**이다.

## 컬렉션 선택

| 목적 | 컬렉션 | 범위 |
|---|---|---|
| 이번 수정 사항 확인 | [부분 재검증 컬렉션](./delivery-5-1-fix-retest.postman_collection.json) | 기존 관련 요청 28개 + 추가 검증 12개 = 40개. 로그인 4회는 준비용 |
| 과제 5-1 전체 시나리오 확인 | [전체 컬렉션](./delivery-5-1.postman_collection.json) | 과제 시나리오 39개를 역할별로 나눈 요청 47개 + 보조 요청 6개 = 53개 |

부분 컬렉션은 생성 응답 201, 주문 입력 검증·ID·총액, 공개 메뉴 단건 조회, 역할별 주문 목록, 삭제 메뉴 처리와 기존 주문 보존을 확인한다. 결제·주문 취소·주문 상태 변경 API를 호출하지 않는다.

전체 컬렉션의 `H` 접미사와 99번은 보조 요청이다. 결제는 미구현이므로 관련 요청을 통과로 처리하지 않고 `NOT_IMPLEMENTED`로 건너뛴다.

## 파일 안내

| 자료 | 용도 |
|---|---|
| [로컬 환경](./delivery-local.postman_environment.json) | `baseUrl=http://localhost:8080` |
| [전체 컬렉션 생성 원본](./generate_collection.py) | 전체 컬렉션과 로컬 환경 파일 생성 |
| [부분 컬렉션 생성 원본](./generate_fix_retest.py) | 전체 컬렉션에서 관련 요청 선택, 검증 12개 추가 |
| [수정 전 결과 JSON](./results.json) | 16:42 실행의 요청별 판정. [보고서](../5-1-test-report.md)와 대응 |
| [수정 후 결과 JSON](./fix-results.json) | 17:02 실행의 40개 요청·67개 assertion. [보고서](../5-1-fix-retest-report.md)와 대응 |
| [DB 확인 SQL](./db-checks.sql) / [조회 결과](./db-checks-result.txt) | 최초 실행 `p51_muz8avk3` 데이터의 읽기 전용 확인 |
| [최초 보고서 생성기](./build_report.py) / [재검증 보고서 생성기](./build_fix_report.py) | 각 실행의 로컬 CLI 산출물에서 공유용 JSON과 보고서 재구성 |

공유용 결과 JSON에는 JWT·비밀번호·요청 본문을 포함하지 않는다. `build/postman-results/` 아래 원본 CLI 산출물과 로컬 실행 파일은 Git 제외 대상이다.

## 저장된 실행 결과

| 실행 | 식별자 | 결과 |
|---|---|---|
| 수정 전 전체 테스트 | `p51_muz8avk3` | 과제 시나리오 39개: 통과 13 / 실패 14 / 선행 조건 미충족 8 / 결제 미구현 4 |
| 수정 후 부분 재검증 | `p51_muz90k12` | HTTP 요청 40개 통과, assertion 67개 통과, 실패·건너뜀 0 |

요청 수와 과제 시나리오 수는 다르다. 최신 결과는 부분 재검증이며, 전체 과제의 모든 시나리오가 통과한 결과로 해석하지 않는다.

## 실행 준비와 테스트 데이터

1. Java 21과 Docker PostgreSQL을 준비하고 프로젝트의 설정에 맞게 DB에 연결한다.
2. 프로젝트 루트에서 `.\gradlew.bat bootRun --console=plain`으로 API 서버를 시작한다.
3. 로컬 환경 파일의 `baseUrl`이 실행한 서버를 가리키는지 확인한다.
4. 선택한 컬렉션을 처음부터 끝까지 1회 실행한다.

두 컬렉션 모두 실행 시각으로 만든 `p51_` 접두사의 새 계정 4개와 메뉴 1개를 사용한다. 기존 계정·메뉴 ID를 지정하지 않으며 테스트 주소와 이메일은 가상 값이다. 삭제 요청은 이번에 생성한 메뉴의 Soft Delete다. 회원과 주문 행을 정리하는 DELETE SQL은 실행하지 않는다.

- 생성 성공은 **201**을 기대한다. 이전 응답 200도 후속 요청을 위한 ID 추출에 사용할 수 있지만 해당 assertion 실패는 그대로 남는다.
- 필요한 ID·토큰·상태가 없으면 `BLOCKED`로 건너뛴다. 건너뜀을 통과로 집계하지 않는다.
- 전체 컬렉션의 `paymentEnabled=false`는 결제 미구현 표시다. 결제 구현 후 실제 경로·요청·응답을 맞춘 뒤 활성화해야 한다.
- 부분 컬렉션의 30번은 원본 이름인 ‘취소용 새 주문’을 유지하지만 주문 생성만 수행한다. 이번 재검증의 주문 2건은 모두 ORDERED로 남았다.

## Postman CLI 실행

이 작업 환경에는 `build/postman-cli/postman-cli.exe`를 준비해 두었다. Git에는 포함되지 않으며 새 체크아웃이나 build 정리 후에는 [공식 설치 안내](https://learning.postman.com/docs/postman-cli/postman-cli-installation)를 따른다.

프로젝트 루트의 PowerShell에서 아래 명령으로 부분 컬렉션을 실행한다. 실행마다 별도 폴더를 만들어 이전 원본 결과를 보존한다.

```powershell
$postmanRunDir = Join-Path 'build/postman-results' ('manual-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $postmanRunDir -Force | Out-Null

& '.\build\postman-cli\postman-cli.exe' collection run 'docs/postman/delivery-5-1-fix-retest.postman_collection.json' `
  --environment 'docs/postman/delivery-local.postman_environment.json' `
  --no-report-events --timeout-request 10000 --timeout-script 10000 `
  --reporters cli,json `
  --reporter-json-export (Join-Path $postmanRunDir 'report.json') `
  --reporter-json-omitAllHeadersAndBody
```

전체 실행은 위 명령의 컬렉션 경로를 `docs/postman/delivery-5-1.postman_collection.json`으로 변경한다.

CLI의 종료 코드와 assertion 실패·건너뜀을 함께 확인한다. 저장된 두 실행은 로컬 파일을 사용했고 클라우드 로그인이나 게시를 하지 않았다. 공식 참고: [컬렉션 실행](https://learning.postman.com/docs/postman-cli/postman-cli-collections), [보고서 옵션](https://learning.postman.com/docs/postman-cli/postman-cli-reporters/).

Postman 앱에서도 선택한 컬렉션과 환경 파일을 Import한 뒤 실행할 수 있다. 이 저장소에 기록한 결과의 실행 도구는 CLI다.

## 결과 보존과 보고서 생성기

`build_report.py`는 `build/postman-results/raw-report.json` 및 `cli-output.log`를, `build_fix_report.py`는 `fix-raw-report.json` 및 `fix-cli-output.log`를 읽는다. 각 스크립트의 설명 문구와 집계 범위는 **기록된 2026-10-08 실행에 맞춘 것**이다.

새 실행 결과를 기존 파일에 덮어써서 역사적 보고서를 바꾸지 않는다. 새 실행은 별도 산출물로 남기고 결과에 맞게 보고서를 작성한다. 보고서 생성 스크립트를 재사용할 때도 입력 경로·집계 대상·설명 문구를 해당 실행에 맞춰야 한다.

## DB 확인 기록의 범위

최초 실행의 `DELIVERY_RUN_ID`를 psql의 `run_id` 변수로 전달하여 `db-checks.sql`을 실행했다. BCrypt 형식, 회원·메뉴 시각, 메뉴 Soft Delete, enum 컬럼 타입과 payments 테이블 부재를 확인했다.

당시 주문 생성은 실패하여 SQL 결과에 주문이 0건으로 남아 있다. 수정 후 주문 생성·역할별 조회·삭제 메뉴의 주문 보존은 API 재검증으로 확인했으며, 최초 SQL 결과를 수정 후 DB 스냅샷으로 취급하지 않는다. 상세 내용은 [테이블 명세의 DB 확인 범위](../4-2-table-spec.md#실제-db에서-확인한-범위)를 따른다.
