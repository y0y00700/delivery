# 5-1. 수정 부분 재검증 결과 — 결제 제외

[문서 안내](./README.md) · [수정 전 전체 기록](./5-1-test-report.md) · [Postman 실행 자료](./postman/README.md)

실행 시각: 2026-10-08 17:02:18 (Asia/Seoul)

실행 식별자: `p51_muz90k12`

환경: Postman CLI 1.70.0 · Spring Boot 4.1.1 · Java 21.0.12.1 · Docker PostgreSQL 18.6

## 결과와 범위

변경 부분과 준비용 요청 **40개 중 40개 통과**. Assertion **67/67개 통과**, 실패 0개, 건너뜀 0개다. 실제 HTTP 실행의 요청 오류는 0개이며 소요 시간은 6.812초다.

기존 컬렉션에서 관련 요청 28개를 선택하고 입력 검증·삭제 메뉴 관련 요청 12개를 추가했다. 로그인 4회는 테스트 준비용이다. 과제 전체 39개 시나리오를 다시 실행한 결과가 아니다.

이전 실패 시나리오 14개 중 이번 실행에서 14개가 통과했다: **1, 2, 3, 4, 11, 14, 17, 18, 19, 20, 21, 30, 37, 38번**. 각 번호의 역할별 요청을 함께 확인했다. 최초 결과는 [기존 보고서](./5-1-test-report.md)에 보존했다.

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
| 01 | owner1 회원가입 | 201 | PASS |
| 02 | owner2 회원가입 | 201 | PASS |
| 03 | cust1 회원가입 | 201 | PASS |
| 04 | cust2 회원가입 | 201 | PASS |
| 07a | owner1 로그인 및 토큰 저장 | 200 | PASS |
| 07b | owner2 로그인 및 토큰 저장 | 200 | PASS |
| 07c | cust1 로그인 및 토큰 저장 | 200 | PASS |
| 07d | cust2 로그인 및 토큰 저장 | 200 | PASS |
| 09 | 토큰 없는 메뉴 등록 | 403 | PASS |
| 11 | owner1 김밥 3000원 등록 | 201 | PASS |
| 14a | 비로그인 김밥 단건 조회 | 200 | PASS |
| 14b | 비로그인 없는 메뉴 조회 | 404 | PASS |
| 15 | 다른 OWNER 메뉴 수정 거절 | 403 | PASS |
| 16 | 본인 김밥 가격 3500원 수정 | 200 | PASS |
| 17 | OWNER 주문 생성 거절 | 403 | PASS |
| 18 | cust1 김밥 2개 주문 | 201 | PASS |
| 19 | 수량 0 주문 거절 | 400 | PASS |
| V1 | menuId 누락 거절 | 400 | PASS |
| V2 | menuId null 거절 | 400 | PASS |
| V3 | quantity 누락 거절 | 400 | PASS |
| V4 | quantity null 거절 | 400 | PASS |
| V5 | 음수 수량 거절 | 400 | PASS |
| V6 | 주소 누락 거절 | 400 | PASS |
| V7 | 주소 null 거절 | 400 | PASS |
| V8 | 공백 주소 거절 | 400 | PASS |
| V9 | 없는 메뉴 주문 거절 | 404 | PASS |
| 20a | cust1 주문 목록 범위 | 200 | PASS |
| 20b | cust2 주문 목록 범위 | 200 | PASS |
| 21a | owner1 주문 목록 범위 | 200 | PASS |
| 21b | owner2 주문 목록 범위 | 200 | PASS |
| 30 | 취소용 새 주문 1개 | 201 | PASS |
| 34 | 다른 OWNER 메뉴 삭제 거절 | 403 | PASS |
| 35 | 본인 메뉴 Soft Delete | 204 | PASS |
| 37 | 삭제된 메뉴 단건 조회 거절 | 404 | PASS |
| D1 | 비로그인 삭제 메뉴 조회 거절 | 404 | PASS |
| D2 | 삭제 메뉴 수정 거절 | 404 | PASS |
| D3 | 삭제 메뉴 재삭제 거절 | 404 | PASS |
| 38 | 삭제된 메뉴 주문 거절 | 404 | PASS |
| 39a | cust1 삭제 메뉴의 기존 주문 유지 | 200 | PASS |
| 39b | owner1 삭제 메뉴의 기존 주문 유지 | 200 | PASS |

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
& '.\build\postman-cli\postman-cli.exe' collection run 'docs/postman/delivery-5-1-fix-retest.postman_collection.json' `
  --environment 'docs/postman/delivery-local.postman_environment.json' `
  --no-report-events --timeout-request 10000 --timeout-script 10000 `
  --reporters cli,json `
  --reporter-json-export 'build/postman-results/fix-raw-report.json' `
  --reporter-json-omitAllHeadersAndBody
```
