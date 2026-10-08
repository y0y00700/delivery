# 4-3. API 명세서 · 요청/응답 예시

[문서 목록](./README.md) · [테이블 명세서](./4-2-table-spec.md)

기준: 2026-10-08 수정 후 소스. 기능별 실행 여부는 [검증 범위 표](./README.md#기능별-구현검증-범위)에서 확인한다.

**현재 코드 기준 명세다.** 1~11번은 구현된 경로이고, 12번 결제는 미구현 설계안이다. 응답 예시는 DTO와 처리 코드를 기준으로 구성한 예시이며 실서버 호출 결과가 아니다. 결제를 제외한 수정 사항을 반영했으며, 실제 검증 결과는 [수정 부분 재검증 보고서](./5-1-fix-retest-report.md)에 기록했다.

## 공통 규칙

| 항목 | 현재 기준 |
|---|---|
| 로컬 Base URL | `http://localhost:8080` — 별도 server.port 설정이 없는 기본 포트 기준 |
| 요청 형식 | 본문이 있으면 `Content-Type: application/json` |
| JSON 응답 | 객체 또는 배열을 직접 반환. 공통 `data` 래퍼 없음 |
| 인증 헤더 | `Authorization: Bearer {JWT}` |
| 토큰 응답 | 로그인 응답의 `token` 문자열에 **이미 `Bearer ` 접두사가 포함**됨 |
| 토큰 내용 | `sub`: loginId, `auth`: userType, `iat`: 발급 시각, `exp`: 만료 시각 |
| 토큰 설정 | HS256 서명, 유효 시간 60분, 갱신 API 없음 |
| 역할 | `CUSTOMER`, `OWNER` |
| 금액 | 정수, 원 단위. 주문 총액은 서버에서 계산 |
| 목록 | 페이징·검색·정렬 쿼리 파라미터 없음. 결과가 없으면 `[]`. 순서는 보장하지 않음 |
| 경로 변수 | `menuId`, `orderId`는 Long으로 바인딩. 숫자로 변환할 수 없으면 400 |
| 시각 필드 | 현재 성공 응답 DTO에는 createdAt·modifiedAt 필드가 없음 |

목록 경로 `/api/menus/`와 주문 생성 경로 `/api/order/`는 **끝의 `/`까지 코드 그대로 호출**한다. 끝의 슬래시를 생략한 별도 매핑은 없다.

예시의 `{OWNER_JWT}`, `{CUSTOMER_JWT}`는 `Bearer `를 제외한 토큰 본체를 뜻한다. 실제 로그인 응답의 `token` 값을 복사할 때는 헤더에 그 문자열을 그대로 넣는다. `Bearer Bearer ...`로 중복해서 붙이지 않는다. Postman의 Bearer Token 입력란을 사용한다면 접두사를 제거한 본체만 입력한다.

### 인증·오류 처리의 현재 제한

- 비로그인 공개 경로: `/api/users/**`, `GET /api/menus/`, `GET /api/menus/{menuId}`. 단, 해당 경로에 실제 매핑이 있어야 한다.
- 그 밖의 경로는 인증이 필요하다. 토큰을 보내지 않은 보호 API는 기본 보안 설정상 `403`이며, 별도의 `401` 진입점은 구현하지 않았다.
- 잘못된 아이디·비밀번호의 로그인은 로그인 필터가 **본문 없는 `401`**을 설정한다.
- 유효한 인증 이후 역할·소유권 위반은 서비스에서 `403`을 발생시킨다.
- 현재 `JwtAuthorizationFilter`는 만료·위조 토큰 검증 실패 시 오류 코드나 본문을 설정하지 않고 종료한다. 따라서 **빈 `200`처럼 보일 수 있으며 정상 인증 성공으로 해석하면 안 된다.** `Bearer `가 없는 헤더도 필터 예외 처리가 미비하다. 잘못된 토큰에 대한 일관된 실패 계약은 아직 없다.
- 현재 보안 설정은 `DispatcherType.ERROR`를 허용한다. `400·404·409`를 오류 디스패치에서 일괄 `403`으로 덮는 예전 문제와 구분한다.
- 공통 예외 응답 DTO와 `@RestControllerAdvice`는 없다. 아래 각 API의 실패 코드는 소스상 분기 기준이다. 기본 오류 본문은 처리 경로·프레임워크 설정에 따라 달라지며, 서비스의 예외 메시지가 JSON에 항상 포함되는 것은 아니다.
- DB 제약 예외를 `409`로 통일하는 처리는 없다. 동시에 들어온 중복 요청이나 DB 길이 제한 위반은 서비스 사전 검사와 다른 응답이 될 수 있다.

## API 목록

| 번호 | 기능 | Method | 현재 URL | 현재 권한 조건 | 코드상 성공 |
|---|---|---|---|---|---|
| 1 | 회원가입 | POST | `/api/users/registry` | 누구나 | 201 |
| 2 | 로그인 | POST | `/api/users/login` | 누구나 | 200 |
| 3 | 메뉴 등록 | POST | `/api/menus/registry` | OWNER | 201 |
| 4 | 메뉴 목록 조회 | GET | `/api/menus/` | 누구나 | 200 |
| 5 | 메뉴 단건 조회 | GET | `/api/menus/{menuId}` | 누구나 | 200 |
| 6 | 메뉴 수정 | PUT | `/api/menus/{menuId}` | OWNER + 본인 메뉴 | 200 |
| 7 | 메뉴 삭제 | DELETE | `/api/menus/{menuId}` | OWNER + 본인 메뉴 | 204 |
| 8 | 주문 생성 | POST | `/api/order/` | CUSTOMER | 201 |
| 9 | 주문 목록 조회 | GET | `/api/order/retrieve` | 로그인한 사용자, 역할별 범위 | 200 |
| 10 | 주문 취소 | PUT | `/api/order/cancel/{orderId}` | 로그인 + 본인 주문 검사 | 204 |
| 11 | 주문 상태 변경 | PATCH | `/api/order/{orderId}/status` | OWNER + 본인 메뉴 주문 | 204 |
| 12 | 결제 | POST | **미구현**, 제안: `/api/orders/{orderId}/payments` | 제안: CUSTOMER + 본인 주문 | 제안: 201 |

아래에서는 메뉴 `menuId=10`, 주문 `orderId=100`, 사장님 `ownerId=1`을 예시로 사용한다. 실제 ID는 저장 결과에 따라 다르다. 예시별 상태는 해당 절의 전제에 따른다.

## 1. 회원가입

`POST /api/users/registry` · 누구나 · 성공 `201 Created`

### 요청 필드

| 필드 | 타입 | 필수 | 현재 검증 / 설명 |
|---|---|---|---|
| `loginId` | String | O | 공백 불가, 4~20자, 중복 불가 |
| `password` | String | O | 공백 불가, 8자 이상, BCrypt 해시 저장 |
| `userName` | String | O | 공백 불가, 최대 50자 |
| `email` | String | O | 공백 불가, 이메일 형식, 최대 250자, 중복 불가 |
| `userType` | String(enum) | O | CUSTOMER 또는 OWNER |

### 요청 예시

```http
POST /api/users/registry HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "loginId": "owner1",
  "password": "Owner1234!",
  "userName": "김사장",
  "email": "owner1@example.com",
  "userType": "OWNER"
}
```

### 응답 예시

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "loginId": "owner1",
  "userName": "김사장",
  "email": "owner1@example.com",
  "userType": "OWNER"
}
```

응답 필드는 `loginId`, `userName`, `email`(String), `userType`(enum)이다. `userId`, 비밀번호, 토큰은 반환하지 않는다. 손님 가입은 별도 아이디·이메일과 `userType: "CUSTOMER"`를 사용한다.

| 실패 | 조건 |
|---|---|
| 400 | 요청 검증 실패, 잘못된 역할 값, 해석할 수 없는 JSON |
| 409 | 서비스 중복 검사에서 아이디 또는 이메일 중복 확인 |

생성 성공은 `201 Created`이며 저장된 회원의 공개 정보만 반환한다.

## 2. 로그인

`POST /api/users/login` · 누구나 · 성공 `200 OK`

Controller가 아니라 `JwtAuthenticationFilter`가 처리한다.

### 요청 필드

| 필드 | 타입 | 필요 여부 | 현재 처리 |
|---|---|---|---|
| `loginId` | String | 인증에 필요 | AuthenticationManager에 전달 |
| `password` | String | 인증에 필요 | 저장된 BCrypt 해시와 비교 |

`UserLoginRequestDto`에는 `userName`, `email`, `userType`도 선언되어 있지만 로그인 처리에서 사용하지 않는다. 보내지 않아도 된다. 이 DTO를 필터에서 직접 역직렬화하며 Bean Validation을 호출하지 않으므로 회원가입처럼 `@Valid` 검증이 적용되는 구조는 아니다.

### 요청 예시

```http
POST /api/users/login HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "loginId": "owner1",
  "password": "Owner1234!"
}
```

### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "loginId": "owner1",
  "userName": "김사장",
  "email": "owner1@example.com",
  "userType": "OWNER",
  "token": "Bearer {OWNER_JWT}"
}
```

회원가입 응답의 4개 필드에 `token`(String)이 추가된다. 예시의 토큰은 자리 표시자이며 사용할 수 있는 JWT가 아니다. 현재 응답은 본문에 토큰을 싣고, 별도 Authorization 응답 헤더나 인증 쿠키는 설정하지 않는다.

아이디가 없거나 비밀번호가 틀릴 때:

```http
HTTP/1.1 401 Unauthorized
```

본문은 없다. 잘못된 JSON을 읽을 때 발생하는 예외를 일관된 `400`으로 변환하는 처리는 현재 로그인 필터에 없다.

## 3. 메뉴 등록

`POST /api/menus/registry` · OWNER · 성공 `201 Created`

### 요청 필드

| 필드 | 타입 | 필수 | 현재 검증 / 설명 |
|---|---|---|---|
| `menuName` | String | O | 공백 불가 |
| `menuDesc` | String | X | 설명. 생략하면 null. DB 길이는 250이지만 DTO 길이 검증은 없음 |
| `price` | Integer | O | 1원 이상. 누락 시 0으로 검증 실패 |
| `menuId` | Long | X | DTO에 존재하지만 등록 로직에서 사용하지 않음. 보내지 않는 것을 권장 |

주인은 요청 Body가 아니라 인증된 `loginId`로 조회한 회원으로 결정한다. `ownerId`는 요청 필드가 아니다.

### 요청 예시

```http
POST /api/menus/registry HTTP/1.1
Host: localhost:8080
Authorization: Bearer {OWNER_JWT}
Content-Type: application/json

{
  "menuName": "김밥",
  "menuDesc": "기본 야채 김밥",
  "price": 3000
}
```

### 응답 예시

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "menuId": 10,
  "menuName": "김밥",
  "menuDesc": "기본 야채 김밥",
  "price": 3000,
  "ownerId": 1
}
```

`menuId`, `ownerId`는 Long, `price`는 Integer, 이름·설명은 String이며 설명은 null일 수 있다.

| 실패 | 조건 |
|---|---|
| 400 | 이름 공백, 가격 1 미만 등 요청 검증 실패 |
| 403 | 토큰 없음 또는 CUSTOMER 요청 |
| 409 | 같은 사장님의 같은 메뉴명 존재. 삭제된 메뉴도 포함 |

생성 성공은 `201 Created`다.

## 4. 메뉴 목록 조회

`GET /api/menus/` · 누구나 · 성공 `200 OK`

요청 Body·쿼리 파라미터가 없다. `deleted_at IS NULL`인 메뉴만 조회한다.

### 요청 예시

```http
GET /api/menus/ HTTP/1.1
Host: localhost:8080
```

### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "menuId": 10,
    "menuName": "김밥",
    "menuDesc": "기본 야채 김밥",
    "price": 3000
  }
]
```

각 항목은 `menuId`(Long), `menuName`(String), `menuDesc`(String 또는 null), `price`(Integer)다. 등록 응답과 달리 `ownerId`는 없다. 메뉴가 없으면 `200`과 `[]`를 반환한다. 이 DTO는 단건 조회와 수정 응답에도 사용된다.

## 5. 메뉴 단건 조회

`GET /api/menus/{menuId}` · 누구나 · 성공 `200 OK`

경로의 `menuId`만 사용한다. 요청 Body는 없다.

### 요청 예시

```http
GET /api/menus/10 HTTP/1.1
Host: localhost:8080
```

### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "menuId": 10,
  "menuName": "김밥",
  "menuDesc": "기본 야채 김밥",
  "price": 3000
}
```

| 실패 | 조건 |
|---|---|
| 400 | menuId를 Long으로 변환할 수 없음 |
| 404 | 해당 메뉴가 없거나 삭제됨 |

목록과 단건 GET 모두 비로그인 조회를 허용한다. `findByMenuIdAndDeletedAtIsNull()`로 조회하므로 없는 메뉴와 삭제된 메뉴는 404다.

## 6. 메뉴 수정

`PUT /api/menus/{menuId}` · OWNER + 본인 메뉴 · 성공 `200 OK`

경로의 `menuId`가 수정 대상이다. Body의 필드는 다음과 같다.

| 필드 | 타입 | 필수 | 현재 검증 / 설명 |
|---|---|---|---|
| `menuName` | String | O | 공백 불가 |
| `menuDesc` | String | X | 생략하면 null로 변경되므로 기존 설명을 유지하려면 값을 함께 전송 |
| `price` | Integer | O | 1원 이상 |

### 요청 예시

```http
PUT /api/menus/10 HTTP/1.1
Host: localhost:8080
Authorization: Bearer {OWNER_JWT}
Content-Type: application/json

{
  "menuName": "김밥",
  "menuDesc": "기본 야채 김밥",
  "price": 3500
}
```

### 응답 예시

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "menuId": 10,
  "menuName": "김밥",
  "menuDesc": "기본 야채 김밥",
  "price": 3500
}
```

| 실패 | 조건 |
|---|---|
| 400 | 요청 필드 검증 실패 또는 잘못된 경로 ID |
| 403 | 토큰 없음, CUSTOMER, 다른 사장님의 메뉴 |
| 404 | 해당 메뉴가 없거나 삭제됨 |
| 409 | 이름 변경 시 같은 사장님에게 동일 이름의 다른 메뉴가 존재 |

변경은 트랜잭션 안에서 저장되며 수정 시각은 Auditing 대상이다. 삭제된 메뉴는 404로 거절한다.

## 7. 메뉴 삭제

`DELETE /api/menus/{menuId}` · OWNER + 본인 메뉴 · 성공 `204 No Content`

경로의 `menuId`만 사용한다. 요청 Body는 없다.

### 요청 예시

```http
DELETE /api/menus/10 HTTP/1.1
Host: localhost:8080
Authorization: Bearer {OWNER_JWT}
```

### 응답 예시

```http
HTTP/1.1 204 No Content
```

응답 Body는 없다. DB 행을 DELETE하지 않고 `deleted_at`에 현재 시각을 저장한다. 기존 주문은 유지된다.

| 실패 | 조건 |
|---|---|
| 400 | 잘못된 경로 ID |
| 403 | 토큰 없음, CUSTOMER, 다른 사장님의 메뉴 |
| 404 | 해당 메뉴가 없거나 삭제됨 |

이미 삭제된 메뉴를 다시 삭제하면 404다. 기존 주문을 보존하기 위해 메뉴 행 자체는 삭제하지 않는다.

## 8. 주문 생성

`POST /api/order/` · CUSTOMER · 성공 `201 Created`

### 요청 필드

| 필드 | 타입 | 필수 | 현재 검증 / 설명 |
|---|---|---|---|
| `menuId` | Long | O | `@NotNull`. 없는 메뉴 또는 삭제 메뉴는 서비스에서 404 |
| `quantity` | Long | O | `@NotNull`, `@Min(1)` |
| `deliveryAddr` | String | O | `@NotBlank`, DB 길이 255, DTO 최대 길이 검증 없음 |

주문자·총액·주문 상태는 요청 필드에 없다. 주문자는 인증된 회원이고, 총액은 활성 메뉴의 가격 × 수량이며 초기 상태는 서버에서 ORDERED로 결정한다.

### 요청 예시

전제: 메뉴 10이 삭제되지 않았고 현재 가격이 3,500원이다.

```http
POST /api/order/ HTTP/1.1
Host: localhost:8080
Authorization: Bearer {CUSTOMER_JWT}
Content-Type: application/json

{
  "menuId": 10,
  "quantity": 2,
  "deliveryAddr": "서울시 예시구 예시로 10, 101호"
}
```

### 응답 예시

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "orderId": 100,
  "menuId": 10,
  "orderStatus": "ORDERED",
  "quantity": 2,
  "deliveryAddr": "서울시 예시구 예시로 10, 101호",
  "orderPrice": 7000
}
```

`orderId`, `menuId`, `quantity`, `orderPrice`는 Long, `orderStatus`는 enum, `deliveryAddr`는 String이다. 생성 응답의 `orderId`로 이후 주문 작업의 대상을 식별한다.

| 실패 | 조건 |
|---|---|
| 403 | 토큰 없음 또는 OWNER 계정의 주문 요청 |
| 400 | 메뉴 ID·수량·주소 누락 또는 null, 수량 1 미만, 주소 공백, 잘못된 JSON 타입 |
| 404 | Service 기준: 없는 메뉴·삭제된 메뉴 |

숫자 필드의 검증을 수정한 후 실제 PostgreSQL 대상 Postman 실행에서 정상 주문 201, 입력 오류 400, OWNER 403, 없는 메뉴·삭제 메뉴 404를 확인했다.

## 9. 주문 목록 조회

`GET /api/order/retrieve` · 로그인한 사용자 · 성공 `200 OK`

요청 Body·쿼리 파라미터가 없다. 로그인한 회원의 역할에 따라 조회 조건이 달라진다.

| 역할 | 조회 범위 | 현재 Query Method |
|---|---|---|
| CUSTOMER | 본인이 주문한 내역 | `findByOdererId_UserId(userId)` |
| OWNER | 본인이 소유한 메뉴로 들어온 주문 | `findAllByMenuId_OwnerId_UserId(userId)` |

### 요청 예시

```http
GET /api/order/retrieve HTTP/1.1
Host: localhost:8080
Authorization: Bearer {CUSTOMER_JWT}
```

### 응답 예시

전제: 해당 회원이 볼 수 있는 주문 100이 이미 DB에 있다.

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "orderId": 100,
    "menuId": 10,
    "orderStatus": "ORDERED",
    "quantity": 2,
    "deliveryAddr": "서울시 예시구 예시로 10, 101호",
    "orderPrice": 7000
  }
]
```

생성 응답과 같은 6개 필드(`orderId`, `menuId`, `orderStatus`, `quantity`, `deliveryAddr`, `orderPrice`)를 반환한다. 메뉴명·주문자 정보·결제 정보는 포함하지 않는다. OWNER도 같은 DTO 구조를 사용한다. 조회 대상이 없으면 `[]`다. 삭제된 메뉴에 연결된 주문과 취소·완료된 주문도 조회 범위에 포함된다.

토큰 없는 접근은 현재 `403`이다. 사용자 ID를 Body나 쿼리로 전달해 다른 사용자의 주문을 조회하는 기능은 없다.

## 10. 주문 취소

검증 상태: 구현은 존재하지만 최초 Postman 실행에서는 선행 조건 미충족으로 건너뛰었고, 수정 후 부분 재검증에서는 제외했다. 아래 예시는 현재 코드상 계약이다.

`PUT /api/order/cancel/{orderId}` · 로그인 + 본인 주문 · 성공 `204 No Content`

경로의 `orderId`만 사용한다. 요청 Body는 없다. 전제: 본인 주문 100이 `ORDERED` 상태다.

### 요청 예시

```http
PUT /api/order/cancel/100 HTTP/1.1
Host: localhost:8080
Authorization: Bearer {CUSTOMER_JWT}
```

### 응답 예시

```http
HTTP/1.1 204 No Content
```

본문은 없다. 주문 행을 삭제하지 않고 `order_status`를 `CANCELED`로 바꾼다. 변경 결과는 주문 목록으로 확인한다.

| 실패 | 조건 |
|---|---|
| 400 | ORDERED 이외의 상태, 이미 취소됨, 잘못된 경로 ID |
| 403 | 토큰 없음 또는 다른 회원의 주문 |
| 404 | 주문이 없음 |

**권한 구현의 정확한 범위:** 과제상 CUSTOMER 기능이다. 현재 `cancelOrder()`는 주문자 ID 일치 여부를 검사하며 CUSTOMER 역할을 별도로 검사하지 않는다. 정상 주문 생성 로직은 OWNER를 막지만, 취소 메서드 자체에 역할 검사가 있다고 문서화하지 않는다.

## 11. 주문 상태 변경

검증 상태: 구현은 존재하지만 두 차례 Postman 실행에서 이 흐름을 완료하지 않았다. 아래 예시는 현재 코드상 계약이며 결제 이후 흐름의 실행 성공을 뜻하지 않는다.

`PATCH /api/order/{orderId}/status` · OWNER + 본인 메뉴 주문 · 성공 `204 No Content`

### 요청 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `orderStatus` | String(enum) | O | 요청 대상은 ACCEPTED 또는 COMPLETED. 현재 상태와 전환 규칙도 만족해야 함 |

| 현재 상태 | 요청할 다음 상태 | 뜻 |
|---|---|---|
| PAID | ACCEPTED | 결제된 주문 수락 |
| ACCEPTED | COMPLETED | 배달 완료 |

### 요청 예시 — 주문 수락

전제: 본인 메뉴에 대한 주문 100이 이미 `PAID`다. **현재 결제 API가 없어 정상 API 흐름으로 이 전제에 도달하는 기능은 미구현이다.**

```http
PATCH /api/order/100/status HTTP/1.1
Host: localhost:8080
Authorization: Bearer {OWNER_JWT}
Content-Type: application/json

{
  "orderStatus": "ACCEPTED"
}
```

### 요청 예시 — 배달 완료

앞선 주문 수락이 반영된 이후 호출한다.

```http
PATCH /api/order/100/status HTTP/1.1
Host: localhost:8080
Authorization: Bearer {OWNER_JWT}
Content-Type: application/json

{
  "orderStatus": "COMPLETED"
}
```

### 두 요청의 성공 응답

```http
HTTP/1.1 204 No Content
```

본문은 없다. 변경된 상태는 주문 목록에서 확인한다.

| 실패 | 조건 |
|---|---|
| 400 | 상태 누락·알 수 없는 enum·불가능한 전환·허용되지 않은 목표 상태·잘못된 경로 ID |
| 403 | 토큰 없음, CUSTOMER, 다른 사장님 메뉴의 주문 |
| 404 | 주문이 없음 |

`ORDERED → ACCEPTED`, `PAID → COMPLETED`, 같은 상태로의 재요청과 최종 상태에서의 변경은 거절한다. `PAID`로 바꾸는 용도로 이 API를 사용할 수 없다.

## 12. 결제 — 미구현 설계안

**이 절은 현재 호출 가능한 API가 아니다.** 아래 경로·필드·상태 코드는 과제 요구사항을 구현하기 위한 제안이다.

제안: `POST /api/orders/{orderId}/payments` · CUSTOMER + 본인 주문 · 성공 `201 Created`

현재 주문 경로는 단수형 `/api/order`다. 위 제안은 과제의 복수형·하위 자원 규칙을 적용한 신규 설계이므로 기존 주문 경로와의 통일 여부를 구현 시 결정해야 한다.

### 제안 요청 필드

| 위치 / 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| Path / `orderId` | Long | O | 결제할 주문 |
| Body / `paymentMethod` | String(enum) | O | CARD만 허용 |

결제 금액, 주문자, 카드번호는 요청으로 받지 않는다. 서버가 저장된 주문 총액을 사용한다.

### 제안 요청 예시

```http
POST /api/orders/100/payments HTTP/1.1
Host: localhost:8080
Authorization: Bearer {CUSTOMER_JWT}
Content-Type: application/json

{
  "paymentMethod": "CARD"
}
```

### 제안 응답 예시

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "paymentId": 500,
  "orderId": 100,
  "paymentAmount": 7000,
  "paymentMethod": "CARD",
  "paymentStatus": "COMPLETED",
  "orderStatus": "PAID"
}
```

`paymentId`, `orderId`, `paymentAmount`는 Long, 나머지는 enum 문자열로 제안한다.

| 제안 실패 | 조건 |
|---|---|
| 400 | 결제 수단 누락·CARD 이외 값·현재 상태가 ORDERED가 아님·중복 결제 |
| 403 | 인증 없음, OWNER, 다른 고객의 주문. 인증 실패 401 구분을 추가하면 함께 조정 |
| 404 | 주문 없음 |

상태 충돌은 기존 주문 서비스와 맞춰 이 설계안에서는 `400`을 선택했다. 과제는 400 또는 409를 허용한다. 결제 성공 시 기록 저장과 주문 상태 변경을 하나의 트랜잭션으로 처리하고, 동시 결제·취소를 고려한 상태 재검사가 필요하다. [테이블 설계안](./4-2-table-spec.md#미구현-payments-설계안)을 참고한다.

## 현재 오류 응답의 예시

인증된 요청에서 없는 메뉴 9999를 조회하면 Service는 `404`를 발생시킨다. Spring Boot의 기본 오류 처리를 거친 JSON은 다음과 같은 형태일 수 있다. **공통 응답 DTO가 없어 아래 JSON을 고정된 계약으로 보장하지 않는다.**

```json
{
  "timestamp": "2026-10-08T05:00:00.000Z",
  "status": 404,
  "error": "Not Found",
  "path": "/api/menus/9999"
}
```

`message`, `code`, `fieldErrors`를 모든 오류에서 제공하는 기능은 아직 없다. 로그인 실패는 위 JSON이 아니라 빈 401이며, 인증 필터 오류에도 공통 처리가 필요하다.

## RESTful 규칙 및 과제와의 차이

아래 오른쪽 열은 개선 방향이며 현재 API 주소가 아니다.

| 현재 구현 | 과제 기준 / 개선 방향 |
|---|---|
| POST /api/users/registry → 201 | POST /api/users → 201 |
| POST /api/menus/registry → 201 | POST /api/menus → 201 |
| GET /api/menus/ | GET /api/menus로 표기 통일 가능 |
| POST /api/order/ → 201, orderId 포함 | POST /api/orders로 경로 통일 가능 |
| GET /api/order/retrieve | GET /api/orders |
| PUT /api/order/cancel/{orderId} | 예: PATCH /api/orders/{orderId}/cancel |
| PATCH /api/order/{orderId}/status | PATCH /api/orders/{orderId}/status |
| 결제 없음 | 결제 기록 저장 + 주문 PAID 변경 기능 추가 |

로그인은 현재 `/api/users/login`으로 유지해 명세했다. 경로 변경은 Controller 매핑뿐 아니라 로그인 필터 URL과 Security 허용 경로도 함께 맞춰야 한다. 이번 수정에서는 API 경로를 유지했다.

## 소스 근거

- [UserController.java](../src/main/java/com/example/delivery/controller/UserController.java), [UserService.java](../src/main/java/com/example/delivery/service/UserService.java)
- [MenuController.java](../src/main/java/com/example/delivery/controller/MenuController.java), [MenuService.java](../src/main/java/com/example/delivery/service/MenuService.java)
- [OrderController.java](../src/main/java/com/example/delivery/controller/OrderController.java), [OrderService.java](../src/main/java/com/example/delivery/service/OrderService.java)
- [요청·응답 DTO](../src/main/java/com/example/delivery/dto)
- [WebSecurityConfig.java](../src/main/java/com/example/delivery/config/WebSecurityConfig.java)
- [JwtAuthenticationFilter.java](../src/main/java/com/example/delivery/jwt/JwtAuthenticationFilter.java), [JwtAuthorizationFilter.java](../src/main/java/com/example/delivery/jwt/JwtAuthorizationFilter.java), [JwtUtil.java](../src/main/java/com/example/delivery/jwt/JwtUtil.java)
