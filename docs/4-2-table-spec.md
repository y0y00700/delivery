# 4-2. 테이블 명세서

[문서 목록](./README.md) · [ERD](./4-1-erd.md)

기준: 2026-10-08 수정 후 소스. 테이블 정의는 엔티티 매핑을, 실행 증거는 아래의 DB 확인 범위를 기준으로 한다.

## 명세 기준

현재 엔티티 애너테이션과 Spring Boot 기본 명명 규칙을 기준으로 정리했다. 명시하지 않은 컬럼명은 camelCase를 snake_case로 변환한 예상 이름이다. `String`의 길이를 지정하지 않은 경우 `VARCHAR(255)`, `LocalDateTime`은 PostgreSQL의 `TIMESTAMP WITHOUT TIME ZONE` 계열로 표시한다. 실제 길이·정밀도·생성된 CHECK 제약은 DB의 DDL을 확인해야 한다.

현재 `ddl-auto: update`를 사용한다. 엔티티 정의가 바뀌어도 기존 DB 제약이 모두 같은 상태로 갱신된다고 단정할 수 없다. 아래 제약은 **현재 소스에 선언된 제약**이며 운영 중인 DB를 조회해 확정한 값이 아니다.

## 공통 시각 컬럼

`User`, `Menu`, `Order`는 `BaseEntity`를 상속한다. 아래 두 컬럼은 각 테이블에 실제 컬럼으로 포함되는 매핑이다.

| 컬럼 | Java 필드 / 타입 | PostgreSQL 타입 | 현재 선언된 제약 | 설명 |
|---|---|---|---|---|
| `created_at` | `createdAt` / LocalDateTime | TIMESTAMP WITHOUT TIME ZONE | NULL 허용, JPA 수정 대상 제외 | `@CreatedDate`로 생성 시각 기록 |
| `modified_at` | `modifiedAt` / LocalDateTime | TIMESTAMP WITHOUT TIME ZONE | NULL 허용 | `@LastModifiedDate`로 수정 시각 기록 |

`@EnableJpaAuditing`과 `AuditingEntityListener`가 설정되어 있다. 생성 시에는 두 값이 함께 채워지는 구성이지만, 현재 코드에는 `nullable = false`가 없어 **DB NOT NULL 보장은 선언하지 않은 상태**다. `updatable = false`는 JPA UPDATE에서 제외한다는 의미이며 DB의 수정 금지 제약은 아니다. 시각은 타임존이 없는 값이며 실행 환경의 시간대가 문서만으로 보장되지는 않는다.

## users — 회원

엔티티: [User.java](../src/main/java/com/example/delivery/entity/User.java)

| 컬럼 | Java 필드 / 타입 | PostgreSQL 타입 | 현재 선언된 제약 | 설명 |
|---|---|---|---|---|
| `user_id` | `userId` / Long | BIGINT | PK, IDENTITY 자동 생성 | 회원 내부 식별자 |
| `login_id` | `loginId` / String | VARCHAR(20) | NOT NULL, UNIQUE | 로그인 아이디 |
| `password` | `password` / String | VARCHAR(100) | NOT NULL | BCrypt 비밀번호 해시 |
| `user_name` | `userName` / String | VARCHAR(50) | NOT NULL | 사용자 이름. 프로젝트 추가 필드 |
| `email` | `email` / String | VARCHAR(250) | NOT NULL, UNIQUE | 이메일. 프로젝트 추가 필드 |
| `user_type` | `userType` / UserType | VARCHAR(10) | NOT NULL, EnumType.STRING | `CUSTOMER` 또는 `OWNER` |
| `created_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 생성 시각 |
| `modified_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 수정 시각 |

회원가입 요청에서 아이디는 공백 불가·4~20자, 비밀번호는 공백 불가·8자 이상, 이름은 공백 불가·50자 이하, 이메일은 공백 불가·이메일 형식·250자 이하로 검증한다. 비밀번호 길이 검증은 **입력 평문** 기준이고, DB에는 BCrypt 결과를 저장한다. DB 컬럼 길이가 곧 평문 비밀번호 최대 길이를 뜻하지는 않는다.

중복 아이디와 이메일은 서비스에서 먼저 검사하며 DB에도 UNIQUE를 선언했다. 동시 가입으로 서비스 검사를 모두 통과한 뒤 발생하는 DB 제약 예외를 `409`로 변환하는 공통 처리는 현재 없다.

## menus — 메뉴

엔티티: [Menu.java](../src/main/java/com/example/delivery/entity/Menu.java)

| 컬럼 | Java 필드 / 타입 | PostgreSQL 타입 | 현재 선언된 제약 | 설명 |
|---|---|---|---|---|
| `menu_id` | `menuId` / Long | BIGINT | PK, IDENTITY 자동 생성 | 메뉴 식별자 |
| `owner_id` | `ownerId` / User | BIGINT | NOT NULL, FK → users(user_id) | 메뉴를 등록한 사장님 |
| `menu_name` | `menuName` / String | VARCHAR(255), 기본 길이 | NOT NULL | 메뉴명 |
| `menu_desc` | `menuDesc` / String | VARCHAR(250) | NULL 허용 | 메뉴 설명 |
| `price` | `price` / int | INTEGER | NOT NULL | 메뉴 한 개 가격, 원 단위 |
| `deleted_at` | `deletedAt` / LocalDateTime | TIMESTAMP WITHOUT TIME ZONE | NULL 허용 | NULL이면 판매 중, 값이 있으면 삭제 처리 |
| `created_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 생성 시각 |
| `modified_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 수정 시각 |

복합 유일 제약: `uk_menus_owner_menu_name UNIQUE (owner_id, menu_name)`.

- 등록·수정 DTO는 `menuName`에 `@NotBlank`, `price`에 `@Min(1)`을 사용한다. 숫자 필드의 누락은 primitive `int` 기본값 0이 되어 검증에 실패한다.
- 가격 양수 CHECK는 소스에 별도로 선언하지 않았다. 현재 입력 검증과 DB NOT NULL은 다른 보장이다.
- 메뉴명과 설명에 DTO 최대 길이 검증은 없다. DB 길이보다 큰 입력은 DB 저장 단계에서 실패할 수 있다.
- 현재 유일 제약은 삭제된 메뉴도 포함한다. 같은 사장님이 삭제된 메뉴명을 재사용해도 중복으로 처리된다.
- 목록 조회와 단건 조회·수정·삭제는 `deleted_at IS NULL`을 적용한다. 삭제된 메뉴의 단건 조회·수정·재삭제는 404이며 기존 주문의 연결은 유지한다.

## orders — 주문

엔티티: [Order.java](../src/main/java/com/example/delivery/entity/Order.java)

| 컬럼 | Java 필드 / 타입 | PostgreSQL 타입 | 현재 선언된 제약 | 설명 |
|---|---|---|---|---|
| `order_id` | `orderId` / Long | BIGINT | PK, IDENTITY 자동 생성 | 주문 식별자 |
| `orderer_id` | `odererId` / User | BIGINT | NOT NULL, FK → users(user_id) | 주문한 회원. Java 필드명에 오탈자 있음 |
| `menu_id` | `menuId` / Menu | BIGINT | NOT NULL, FK → menus(menu_id) | 주문 메뉴 |
| `order_status` | `orderStatus` / OrderStatus | VARCHAR(10) | NOT NULL, EnumType.STRING | 아래 5개 주문 상태 |
| `quantity` | `quantity` / Long | BIGINT | NOT NULL | 주문 수량 |
| `order_price` | `orderPrice` / Long | BIGINT | NOT NULL | 주문 생성 당시 단가 × 수량, 원 단위 |
| `delivery_addr` | `deliveryAddr` / String | VARCHAR(255), 기본 길이 | NOT NULL | 배송 주소 |
| `created_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 생성 시각 |
| `modified_at` | BaseEntity 상속 | TIMESTAMP WITHOUT TIME ZONE | 위 공통 기준 | 수정 시각 |

| 저장 값 | 의미 | 허용되는 다음 상태 | 현재 HTTP 기능 |
|---|---|---|---|
| `ORDERED` | 주문요청 | `PAID`, `CANCELED` | 취소 API 있음. 결제 API 없음 |
| `PAID` | 결제완료 | `ACCEPTED` | 사장님 상태 변경 API 있음 |
| `ACCEPTED` | 주문수락 | `COMPLETED` | 사장님 상태 변경 API 있음 |
| `COMPLETED` | 배달완료 | 없음 | 최종 상태 |
| `CANCELED` | 주문취소 | 없음 | 최종 상태 |

상태 전환 규칙은 `OrderStatus.canTransitionTo()`와 서비스에서 처리한다. DB 트리거로 구현된 규칙은 아니다. 수량·금액의 양수 CHECK와 곱셈 오버플로 검사는 현재 선언되어 있지 않다.

주문 생성 DTO의 `menuId`, `quantity`는 `@NotNull`, 수량은 추가로 `@Min(1)`, 주소는 `@NotBlank`로 검증한다. 수정 후 Postman 실행에서 정상 주문 2건의 생성, 7000원·3500원의 총액, 역할별 조회와 메뉴 삭제 후 주문 보존을 확인했다. 이는 API를 통해 확인한 결과이며 주문 테이블의 모든 제약과 Auditing 컬럼을 직접 조회한 결과는 아니다.

## 미구현 payments 설계안

**현재 `Payment` 엔티티·Repository·Service·Controller는 없다. 아래는 과제 충족을 위한 제안이며 현재 DB 명세가 아니다.**

| 제안 컬럼 | 제안 Java 타입 | 제안 PostgreSQL 타입 | 제안 제약 | 설명 |
|---|---|---|---|---|
| `payment_id` | Long | BIGINT | PK, IDENTITY 자동 생성 | 결제 식별자 |
| `order_id` | Order | BIGINT | NOT NULL, FK → orders(order_id) | N:1, FetchType.LAZY |
| `payment_amount` | Long | BIGINT | NOT NULL, CHECK > 0 | 서버가 주문의 order_price를 복사 |
| `payment_method` | PaymentMethod | VARCHAR(10) | NOT NULL, 허용 값 CARD | 카드 결제만 지원 |
| `payment_status` | PaymentStatus | VARCHAR(20) | NOT NULL | 기본 기능에서 생성하는 값은 COMPLETED |
| `created_at` | LocalDateTime | TIMESTAMP WITHOUT TIME ZONE | NOT NULL | 생성 시각 |
| `modified_at` | LocalDateTime | TIMESTAMP WITHOUT TIME ZONE | NOT NULL | 수정 시각 |

기본 기능에서는 실제 PG를 호출하지 않고 성공 결제 기록만 저장한다. 결제 실패 이력이나 취소 상태를 추가한다면 상태 enum과 DB 제약을 함께 확장한다. 현재 존재하는 주문 상태 `COMPLETED`와 제안된 결제 상태 `COMPLETED`는 서로 다른 enum의 값이다.

중복 성공을 막는 제안:

1. 결제와 주문 취소가 동일 주문 행을 잠그고 현재 상태를 다시 확인하도록 구현한다.
2. `ORDERED`일 때만 결제 기록 저장과 주문 `PAID` 전환을 하나의 트랜잭션으로 실행한다. 실패하면 둘 다 롤백한다.
3. 아래와 같이 성공 결제에만 적용되는 부분 유일 인덱스를 보조 제약으로 둔다. 아직 적용하지 않은 DDL 예시다.

```sql
CREATE UNIQUE INDEX uk_payments_completed_order
    ON payments (order_id)
    WHERE payment_status = 'COMPLETED';
```

이 제약은 결제 기록 전체의 N:1 구조를 유지하면서 한 주문에 **동시에 유효한 성공 결제 한 건**만 허용한다. 취소 후 재결제 같은 도전 기능은 기존 결제 상태 변경과 주문 상태 정책까지 별도로 설계해야 하며, 기본 기능에는 포함하지 않는다.

## 실제 DB에서 확인한 범위

최초 테스트의 [읽기 전용 SQL](./postman/db-checks.sql)과 [조회 결과](./postman/db-checks-result.txt)는 실행 식별자 `p51_muz8avk3`의 데이터에 대한 기록이다.

| 확인 항목 | 확인한 결과 |
|---|---|
| DB 버전 | PostgreSQL 18.6, DB 이름 delivery |
| 회원 | 테스트 회원 4명의 BCrypt 형식, created_at·modified_at 기록 |
| 메뉴 | 테스트 메뉴 행 유지, deleted_at 저장, modified_at 변경 |
| enum 컬럼 타입 | users.user_type과 orders.order_status는 character varying |
| 결제 테이블 | payments 없음 |

당시 주문 생성이 실패해 주문 행은 0건이었다. 이후 [부분 재검증](./5-1-fix-retest-report.md)에서 API로 주문 생성·조회·보존을 확인했지만, 위 SQL 결과 파일은 최초 실행 기록으로 보존했다. 전체 DDL, 모든 컬럼 길이·제약, 주문의 시각 컬럼은 직접 대조하지 않았다.

## 전체 DDL을 추가로 비교할 때

psql에서 아래 읽기 전용 명령으로 확인할 수 있다. 이번 문서 정리에서는 실행하지 않았다.

```text
\d users
\d menus
\d orders
```

컬럼 타입·길이·NULL 허용·PK·FK·UNIQUE·enum CHECK를 비교한다. `payments`는 구현 이후에 확인한다.
