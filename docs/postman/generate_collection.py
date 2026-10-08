"""Build a reusable Postman collection for assignment 5-1. No HTTP requests."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
items = []

INIT = r'''
const runId = 'p51_' + Date.now().toString(36);
pm.collectionVariables.set('runId', runId);
pm.collectionVariables.set('runResults', '[]');
['menuId','orderId','cancelOrderId','orderCreated','cancelOrderCreated','paid','accepted','completed','canceled','deleted',
 'owner1Token','owner2Token','cust1Token','cust2Token'].forEach(k => pm.collectionVariables.unset(k));
['owner1','owner2','cust1','cust2'].forEach(k => pm.collectionVariables.set(k,runId+'_'+k));
pm.collectionVariables.set('menuName', 'P51 김밥 ' + runId);
pm.collectionVariables.set('password', 'P51test!2026');
console.log('DELIVERY_RUN_ID', runId);
'''

PRE = r'''
const requirements = CONFIG.requires || [];
const absent = requirements.filter(k => !pm.collectionVariables.get(k));
let reason = '';
let state = 'BLOCKED';
if (CONFIG.payment && pm.collectionVariables.get('paymentEnabled') !== 'true') {
  state = 'NOT_IMPLEMENTED'; reason = '결제 API 미구현. 구현 후 paymentEnabled와 결제 요청 경로를 설정하세요.';
} else if (absent.length) {
  reason = '선행 조건 미충족: ' + absent.join(', ');
}
if (reason) {
  const records = JSON.parse(pm.collectionVariables.get('runResults') || '[]');
  records.push({id: CONFIG.id, name: CONFIG.name, outcome: state, reason});
  pm.collectionVariables.set('runResults', JSON.stringify(records));
  console.warn(CONFIG.id + ' ' + state + ': ' + reason);
  pm.test.skip(CONFIG.id + ' ' + state + ': ' + reason, function(){});
  pm.execution.skipRequest();
}
'''

POST_HEAD = r'''
let body;
try { body = pm.response.json(); } catch (_) { body = null; }
const checks = [];
function check(label, fn) {
  let error = '';
  try { fn(); } catch (e) { error = e.message || String(e); }
  checks.push({name: label, pass: !error, error});
  pm.test(CONFIG.id + ' ' + label, function () { if (error) throw new Error(error); });
}
check('HTTP ' + CONFIG.codes.join(' / '), () => pm.expect(pm.response.code).to.be.oneOf(CONFIG.codes));
'''

POST_TAIL = r'''
const records = JSON.parse(pm.collectionVariables.get('runResults') || '[]');
records.push({id: CONFIG.id, name: CONFIG.name, status: pm.response.code,
  outcome: checks.every(c => c.pass) ? 'PASS' : 'FAIL', checks});
pm.collectionVariables.set('runResults', JSON.stringify(records));
'''

def add(id, name, method, path, codes, role=None, body=None, requires=(), extra='', payment=False, init=False):
    reqs = list(requires)
    if role:
        reqs.append(role+'Token')
    cfg = dict(id=id, name=name, codes=codes, requires=reqs, payment=payment)
    config = 'const CONFIG = '+json.dumps(cfg, ensure_ascii=False)+';\n'
    request = {'method': method, 'header': [{'key':'Accept','value':'application/json'}],
               'auth': {'type':'noauth'}, 'url':'{{baseUrl}}'+path,
               'description': '과제 5-1 '+id+' — '+name+'\n기대 HTTP: '+str(codes)}
    if role:
        request['header'].append({'key':'Authorization','value':'{{'+role+'Token}}'})
    if body is not None:
        request['header'].append({'key':'Content-Type','value':'application/json'})
        request['body']={'mode':'raw','raw':json.dumps(body,ensure_ascii=False,indent=2),'options':{'raw':{'language':'json'}}}
    items.append({'name': id+' '+name, 'request':request, 'event':[
      {'listen':'prerequest','script':{'type':'text/javascript','exec':((INIT if init else '')+config+PRE).splitlines()}},
      {'listen':'test','script':{'type':'text/javascript','exec':(config+POST_HEAD+extra+POST_TAIL).splitlines()}}
    ]})

def user(role):
    return {'loginId':'{{'+role+'}}','password':'{{password}}','userName':'P51 '+role,
            'email':'{{'+role+'}}@example.com','userType':'OWNER' if role.startswith('owner') else 'CUSTOMER'}

def menu(price=3000):
    return {'menuName':'{{menuName}}','menuDesc':'Postman 5-1 테스트 데이터','price':price}

def order(qty=2):
    return {'menuId':'{{menuId}}','quantity':qty,'deliveryAddr':'테스트 전용 가상주소 101호'}

for i,role in enumerate(['owner1','owner2','cust1','cust2'],1):
    add(f'{i:02}',role+' 회원가입','POST','/api/users/registry',[201],body=user(role),init=i==1,
        extra="check('비밀번호 미노출', () => pm.expect(JSON.stringify(body)).not.to.match(/password/i));")
add('05','중복 아이디 회원가입','POST','/api/users/registry',[409],body=user('owner1'))
short=user('cust2'); short.update(loginId='{{runId}}_bad',email='{{runId}}_bad@example.com',password='123')
add('06','비밀번호 3자 거절','POST','/api/users/registry',[400],body=short)
for suffix,role in zip('abcd',['owner1','owner2','cust1','cust2']):
    add('07'+suffix,role+' 로그인 및 토큰 저장','POST','/api/users/login',[200],
        body={'loginId':'{{'+role+'}}','password':'{{password}}'},
        extra=r"""
check('JWT 발급', () => pm.expect(body && body.token).to.match(/^Bearer [^.]+\.[^.]+\.[^.]+$/));
if (pm.response.code === 200 && body && typeof body.token === 'string') {
  pm.collectionVariables.set('ROLEToken',body.token.startsWith('Bearer ') ? body.token : 'Bearer '+body.token);
}
""".replace('ROLE',role))
add('08','틀린 비밀번호 로그인','POST','/api/users/login',[401],body={'loginId':'{{owner1}}','password':'Wrong1234!'})
add('09','토큰 없는 메뉴 등록','POST','/api/menus/registry',[401,403],body=menu())
add('10','CUSTOMER 메뉴 등록 거절','POST','/api/menus/registry',[403],role='cust1',body=menu())
add('11','owner1 김밥 3000원 등록','POST','/api/menus/registry',[201],role='owner1',body=menu(),extra="""
check('메뉴 ID 및 가격', () => { pm.expect(body.menuId).to.be.a('number'); pm.expect(body.price).to.eql(3000); });
if ([200,201].includes(pm.response.code) && body && body.menuId) pm.collectionVariables.set('menuId',body.menuId);
""")
add('12','가격 0원 메뉴 등록 거절','POST','/api/menus/registry',[400],role='owner1',body=menu(0))
add('13','비로그인 메뉴 목록','GET','/api/menus/',[200],requires=['menuId'],extra="""
check('김밥 노출', () => pm.expect(body.some(m => m.menuId == pm.collectionVariables.get('menuId'))).to.eql(true));
""")
add('14a','비로그인 김밥 단건 조회','GET','/api/menus/{{menuId}}',[200],requires=['menuId'],extra="""
check('메뉴 일치', () => pm.expect(body.menuId).to.eql(Number(pm.collectionVariables.get('menuId'))));
""")
add('14b','비로그인 없는 메뉴 조회','GET','/api/menus/9223372036854775807',[404])
add('15','다른 OWNER 메뉴 수정 거절','PUT','/api/menus/{{menuId}}',[403],role='owner2',body=menu(3500),requires=['menuId'])
add('16','본인 김밥 가격 3500원 수정','PUT','/api/menus/{{menuId}}',[200],role='owner1',body=menu(3500),requires=['menuId'],
    extra="check('가격 3500원', () => pm.expect(body.price).to.eql(3500));")
add('17','OWNER 주문 생성 거절','POST','/api/order/',[403],role='owner1',body=order(),requires=['menuId'])
add('18','cust1 김밥 2개 주문','POST','/api/order/',[201],role='cust1',body=order(),requires=['menuId'],extra="""
check('총액 7000원 · ORDERED', () => { pm.expect(body.orderPrice).to.eql(7000); pm.expect(body.orderStatus).to.eql('ORDERED'); });
check('생성된 주문 ID 반환', () => pm.expect(body && body.orderId).to.be.a('number'));
if ([200,201].includes(pm.response.code) && body && body.orderStatus === 'ORDERED') {
  pm.collectionVariables.set('orderCreated',true);
  if (body.orderId) pm.collectionVariables.set('orderId',body.orderId);
}
""")
resolver="""
check('이번 실행 주문 식별', () => {
  const matches=body.filter(o => o.menuId == pm.collectionVariables.get('menuId') && o.quantity === QTY && o.orderStatus === 'ORDERED');
  pm.expect(matches.length).to.eql(1);
  pm.collectionVariables.set('KEY',matches[0].orderId);
});
"""
add('18H','보조: 생성 응답 ID 누락 시 목록에서 확인','GET','/api/order/retrieve',[200],role='cust1',requires=['orderCreated'],extra=resolver.replace('QTY','2').replace('KEY','orderId'))
add('19','수량 0 주문 거절','POST','/api/order/',[400],role='cust1',body=order(0),requires=['menuId'])
for id,role,count in [('20a','cust1',1),('20b','cust2',0),('21a','owner1',1),('21b','owner2',0)]:
    add(id,role+' 주문 목록 범위','GET','/api/order/retrieve',[200],role=role,
        extra=f"check('주문 {count}건', () => pm.expect(body).to.be.an('array').with.lengthOf({count}));"+
        ("check('이번 메뉴만 조회', () => pm.expect(body.every(o => o.menuId == pm.collectionVariables.get('menuId'))).to.eql(true));" if count else ''))
add('22','결제 전 주문 수락 거절','PATCH','/api/order/{{orderId}}/status',[400,409],role='owner1',body={'orderStatus':'ACCEPTED'},requires=['orderId'])
pay='/api/orders/{{orderId}}/payments'
add('23','남의 주문 결제 거절','POST',pay,[403],role='cust2',body={'paymentMethod':'CARD'},requires=['orderId'],payment=True)
add('24','cust1 카드 결제','POST',pay,[201],role='cust1',body={'paymentMethod':'CARD'},requires=['orderId'],payment=True,extra="""
check('결제 금액 7000원 · PAID', () => { pm.expect(body.paymentAmount).to.eql(7000); pm.expect(body.orderStatus).to.eql('PAID'); });
if (pm.response.code===201 && body && body.orderStatus==='PAID') pm.collectionVariables.set('paid',true);
""")
add('25','동일 주문 재결제 거절','POST',pay,[400,409],role='cust1',body={'paymentMethod':'CARD'},requires=['orderId','paid'],payment=True)
add('26','결제 후 주문 취소 거절','PUT','/api/order/cancel/{{orderId}}',[400,409],role='cust1',requires=['orderId','paid'])
add('27','다른 OWNER 주문 수락 거절','PATCH','/api/order/{{orderId}}/status',[403],role='owner2',body={'orderStatus':'ACCEPTED'},requires=['orderId','paid'])
add('28a','본인 주문 수락','PATCH','/api/order/{{orderId}}/status',[200,204],role='owner1',body={'orderStatus':'ACCEPTED'},requires=['orderId','paid'],extra="if ([200,204].includes(pm.response.code)) pm.collectionVariables.set('accepted',true);")
statecheck="check('저장 상태 STATE', () => { const o=body.find(o => o.orderId == pm.collectionVariables.get('KEY')); pm.expect(o.orderStatus).to.eql('STATE'); });"
add('28aH','보조: 주문수락 저장 확인','GET','/api/order/retrieve',[200],role='owner1',requires=['orderId','accepted'],extra=statecheck.replace('STATE','ACCEPTED').replace('KEY','orderId'))
add('28b','본인 주문 배달완료','PATCH','/api/order/{{orderId}}/status',[200,204],role='owner1',body={'orderStatus':'COMPLETED'},requires=['orderId','accepted'],extra="if ([200,204].includes(pm.response.code)) pm.collectionVariables.set('completed',true);")
add('28bH','보조: 배달완료 저장 확인','GET','/api/order/retrieve',[200],role='owner1',requires=['orderId','completed'],extra=statecheck.replace('STATE','COMPLETED').replace('KEY','orderId'))
add('29','배달완료 후 재수락 거절','PATCH','/api/order/{{orderId}}/status',[400,409],role='owner1',body={'orderStatus':'ACCEPTED'},requires=['orderId','completed'])
add('30','취소용 새 주문 1개','POST','/api/order/',[201],role='cust1',body=order(1),requires=['menuId'],extra="""
check('ORDERED · 3500원', () => { pm.expect(body.orderStatus).to.eql('ORDERED'); pm.expect(body.orderPrice).to.eql(3500); });
if ([200,201].includes(pm.response.code) && body && body.orderStatus==='ORDERED') {
  pm.collectionVariables.set('cancelOrderCreated',true);
  if (body.orderId) pm.collectionVariables.set('cancelOrderId',body.orderId);
}
""")
add('30H','보조: 취소할 주문 ID 확인','GET','/api/order/retrieve',[200],role='cust1',requires=['cancelOrderCreated'],extra=resolver.replace('QTY','1').replace('KEY','cancelOrderId'))
add('31','다른 CUSTOMER 주문 취소 거절','PUT','/api/order/cancel/{{cancelOrderId}}',[403],role='cust2',requires=['cancelOrderId'])
add('32','본인 ORDERED 주문 취소','PUT','/api/order/cancel/{{cancelOrderId}}',[200,204],role='cust1',requires=['cancelOrderId'],extra="if ([200,204].includes(pm.response.code)) pm.collectionVariables.set('canceled',true);")
add('32H','보조: 주문취소 저장 확인','GET','/api/order/retrieve',[200],role='cust1',requires=['cancelOrderId','canceled'],extra=statecheck.replace('STATE','CANCELED').replace('KEY','cancelOrderId'))
add('33','취소된 주문 결제 거절','POST','/api/orders/{{cancelOrderId}}/payments',[400,409],role='cust1',body={'paymentMethod':'CARD'},requires=['cancelOrderId','canceled'],payment=True)
add('34','다른 OWNER 메뉴 삭제 거절','DELETE','/api/menus/{{menuId}}',[403],role='owner2',requires=['menuId'])
add('35','본인 메뉴 Soft Delete','DELETE','/api/menus/{{menuId}}',[200,204],role='owner1',requires=['menuId'],extra="if ([200,204].includes(pm.response.code)) pm.collectionVariables.set('deleted',true);")
add('36','삭제 후 메뉴 목록에서 제외','GET','/api/menus/',[200],requires=['menuId','deleted'],extra="check('김밥 제외', () => pm.expect(body.some(m => m.menuId == pm.collectionVariables.get('menuId'))).to.eql(false));")
add('37','삭제된 메뉴 단건 조회 거절','GET','/api/menus/{{menuId}}',[404],role='cust1',requires=['menuId','deleted'])
add('38','삭제된 메뉴 주문 거절','POST','/api/order/',[404],role='cust1',body=order(1),requires=['menuId','deleted'])
for suffix,role in [('a','cust1'),('b','owner1')]:
    add('39'+suffix,role+' 삭제 메뉴의 기존 주문 유지','GET','/api/order/retrieve',[200],role=role,requires=['orderId','cancelOrderId','deleted'],extra="""
check('기존 주문 2건 유지', () => {
  const ids=body.map(o=>String(o.orderId));
  pm.expect(ids).to.include(String(pm.collectionVariables.get('orderId')));
  pm.expect(ids).to.include(String(pm.collectionVariables.get('cancelOrderId')));
});
""")
add('99','보조: 실행 결과 집계 (읽기 전용)','GET','/api/menus/',[200])
items[-1]['event'][1]['script']['exec'] += [
  "console.log('DELIVERY_5_1_REPORT', pm.collectionVariables.get('runResults'));",
  "console.log('DELIVERY_RUN_ID', pm.collectionVariables.get('runId'));"
]

# Current DTO requires numeric JSON. Keep IDs as numeric variable substitutions.
for item in items:
    body=item['request'].get('body')
    if body:
        body['raw']=body['raw'].replace('"{{menuId}}"','{{menuId}}')

collection={'info':{'name':'Delivery 5-1 필수 기능 검증','description':
    '과제 5-1의 39개 시나리오. 현재 코드 URL 사용, 기대값은 과제 기준. 테스트 계정 4개와 메뉴 1개를 새로 만들며 해당 테스트 메뉴만 Soft Delete합니다. 결제 미구현 및 선행 조건 실패는 건너뛰고 보고합니다. 서버 기능 코드를 수정하거나 DB에 주문 상태를 강제로 주입하지 않습니다.',
    'schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},
    'variable':[{'key':'baseUrl','value':'http://localhost:8080','type':'string'},
                {'key':'paymentEnabled','value':'false','type':'string'}], 'item':items}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'delivery-5-1.postman_collection.json').write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'delivery-local.postman_environment.json').write_text(json.dumps({'name':'Delivery Local','values':[
 {'key':'baseUrl','value':'http://localhost:8080','enabled':True}], '_postman_variable_scope':'environment'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Generated {len(items)} requests (39 scenarios split by role, plus helpers).')
