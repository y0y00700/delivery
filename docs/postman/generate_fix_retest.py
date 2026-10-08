"""Select changed API behavior and its prerequisites; never run payment requests."""
import copy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
source = json.loads((OUT / 'delivery-5-1.postman_collection.json').read_text(encoding='utf-8'))
selected = {
    '01', '02', '03', '04', '07a', '07b', '07c', '07d', '09', '11',
    '14a', '14b', '15', '16', '17', '18', '19', '20a', '20b', '21a', '21b',
    '30', '34', '35', '37', '38', '39a', '39b',
}
items = []


def extra_request(id, name, method, path, code, role=None, body=None):
    requirements = ['menuId'] + ([role + 'Token'] if role else [])
    if id.startswith('D'):
        requirements.append('deleted')
    pre = """
const absent = REQUIRED.filter(k => !pm.collectionVariables.get(k));
if (absent.length) {
    pm.test.skip('BLOCKED: ' + absent.join(', '), function () {});
    pm.execution.skipRequest();
}
""".replace('REQUIRED', json.dumps(requirements))
    request = {
        'method': method, 'url': '{{baseUrl}}' + path, 'auth': {'type': 'noauth'},
        'header': [{'key': 'Accept', 'value': 'application/json'}],
        'description': '이번 수정에 직접 관련된 추가 검증. 기대 HTTP: ' + str(code),
    }
    if role:
        request['header'].append({'key': 'Authorization', 'value': '{{' + role + 'Token}}'})
    if body is not None:
        request['header'].append({'key': 'Content-Type', 'value': 'application/json'})
        request['body'] = {
            'mode': 'raw',
            'raw': json.dumps(body, ensure_ascii=False, indent=2).replace('"{{menuId}}"', '{{menuId}}'),
            'options': {'raw': {'language': 'json'}},
        }
    return {
        'name': id + ' ' + name, 'request': request,
        'event': [
            {'listen': 'prerequest', 'script': {'type': 'text/javascript', 'exec': pre.splitlines()}},
            {'listen': 'test', 'script': {'type': 'text/javascript', 'exec': [
                f"pm.test('{id} HTTP {code}', () => pm.response.to.have.status({code}));"
            ]}},
        ],
    }


def insert_checks(item, lines):
    script = next(event['script']['exec'] for event in item['event'] if event['listen'] == 'test')
    at = next(i for i, line in enumerate(script) if line.startswith('const records ='))
    script[at:at] = lines.strip().splitlines()


for original in source['item']:
    id = original['name'].split(' ', 1)[0]
    if id not in selected:
        continue
    item = copy.deepcopy(original)
    if id in {'18', '30'}:
        quantity = 2 if id == '18' else 1
        insert_checks(item, f"""
check('주문 ID 양의 정수 · 메뉴 · 수량 · 주소', () => {{
    pm.expect(body.orderId).to.be.a('number').above(0);
    pm.expect(Number.isInteger(body.orderId)).to.eql(true);
    pm.expect(body.menuId).to.eql(Number(pm.collectionVariables.get('menuId')));
    pm.expect(body.quantity).to.eql({quantity});
    pm.expect(body.deliveryAddr).to.eql('테스트 전용 가상주소 101호');
}});
""")
    if id == '30':
        insert_checks(item, """
check('두 주문의 ID 구분', () => pm.expect(String(body.orderId)).not.to.eql(String(pm.collectionVariables.get('orderId'))));
""")
    if id in {'39a', '39b'}:
        insert_checks(item, """
check('삭제 후 주문 상태 · 금액 · 수량 보존', () => {
    pm.expect(body).to.be.an('array').with.lengthOf(2);
    const first = body.find(o => String(o.orderId) === String(pm.collectionVariables.get('orderId')));
    const second = body.find(o => String(o.orderId) === String(pm.collectionVariables.get('cancelOrderId')));
    pm.expect(first.orderStatus).to.eql('ORDERED');
    pm.expect(first.orderPrice).to.eql(7000);
    pm.expect(first.quantity).to.eql(2);
    pm.expect(second.orderStatus).to.eql('ORDERED');
    pm.expect(second.orderPrice).to.eql(3500);
    pm.expect(second.quantity).to.eql(1);
    pm.expect(body.every(o => o.menuId == pm.collectionVariables.get('menuId'))).to.eql(true);
});
""")
    items.append(item)
    if id == '19':
        cases = [
            ('V1', 'menuId 누락 거절', 'menuId', None, True, 400),
            ('V2', 'menuId null 거절', 'menuId', None, False, 400),
            ('V3', 'quantity 누락 거절', 'quantity', None, True, 400),
            ('V4', 'quantity null 거절', 'quantity', None, False, 400),
            ('V5', '음수 수량 거절', 'quantity', -1, False, 400),
            ('V6', '주소 누락 거절', 'deliveryAddr', None, True, 400),
            ('V7', '주소 null 거절', 'deliveryAddr', None, False, 400),
            ('V8', '공백 주소 거절', 'deliveryAddr', '   ', False, 400),
            ('V9', '없는 메뉴 주문 거절', 'menuId', 9223372036854775807, False, 404),
        ]
        for key, name, field, value, omit, code in cases:
            body = {'menuId': '{{menuId}}', 'quantity': 2, 'deliveryAddr': '테스트 전용 가상주소 101호'}
            if omit:
                del body[field]
            else:
                body[field] = value
            items.append(extra_request(key, name, 'POST', '/api/order/', code, 'cust1', body))
    if id == '37':
        items.append(extra_request('D1', '비로그인 삭제 메뉴 조회 거절', 'GET', '/api/menus/{{menuId}}', 404))
        items.append(extra_request('D2', '삭제 메뉴 수정 거절', 'PUT', '/api/menus/{{menuId}}', 404, 'owner1',
                                   {'menuName': '{{menuName}}', 'menuDesc': '삭제 후 수정 금지 확인', 'price': 9999}))
        items.append(extra_request('D3', '삭제 메뉴 재삭제 거절', 'DELETE', '/api/menus/{{menuId}}', 404, 'owner1'))

assert len(items) == 40
assert all('/payments' not in item['request']['url'] for item in items)
assert all('/status' not in item['request']['url'] and '/cancel/' not in item['request']['url'] for item in items)
collection = {
    'info': {
        'name': 'Delivery 5-1 수정 부분 재검증 (결제 제외)',
        'description': (
            '기존 컬렉션의 관련 요청 28개와 추가 검증 12개, 총 40개. '
            '회원가입 4건 및 로그인 4건으로 독립된 데이터를 준비한다. '
            '201, 공개 메뉴 조회, 주문 입력 검증·ID·총액, 역할별 목록, '
            '삭제 메뉴 조회·수정·재삭제 404와 기존 주문 보존을 확인한다. '
            '결제·주문 취소·주문 상태 변경 API는 실행하지 않는다. '
            '이번 실행에서 생성한 메뉴 1건만 Soft Delete한다.'
        ),
        'schema': source['info']['schema'],
    },
    'variable': copy.deepcopy(source['variable']), 'item': items,
}
path = OUT / 'delivery-5-1-fix-retest.postman_collection.json'
path.write_text(json.dumps(collection, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Generated {len(items)} requests: {path.name}')
