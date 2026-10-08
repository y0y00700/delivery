package com.example.delivery.service;

import com.example.delivery.dto.order.RequestOrderCreateDto;
import com.example.delivery.dto.order.ResponseOrderCreateDto;
import com.example.delivery.dto.order.ResponseOrderListDto;
import com.example.delivery.entity.*;
import com.example.delivery.repository.MenuRepository;
import com.example.delivery.repository.OrderRepository;
import com.example.delivery.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final UserRepository userRepository;
    private final MenuRepository menuRepository;
    private final OrderRepository orderRepository;
    // 주문 생성
    // 수량 1이상, 배송 주소 필수 | 어기면 400 없거나 삭제된 메뉴면 404
    // 총액은 메뉴가격 * 수량
    // 주문자는 토큰에서 꺼내고, 처음 상태는 주문 요청 상태
    // OWNER 가 요청하면 403.
    @Transactional
    public ResponseOrderCreateDto createOrder(RequestOrderCreateDto requestOrderCreateDto, String loginId) {
        // 유저 조회
        User orderer = userRepository.findByLoginId(loginId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 유저입니다.")
        );

        // OWNER 요청 403
        if(orderer.getUserType().equals(UserType.OWNER)){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN,"사장님 계정은 주문 불가합니다.");
        }

        // 존재하지 않는 경우 404
        Menu menu = menuRepository.findByMenuIdAndDeletedAtIsNull(requestOrderCreateDto.getMenuId()).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 메뉴입니다.")
        );

        Order order = new Order(
            orderer,
            menu,
            OrderStatus.ORDERED,
            requestOrderCreateDto.getQuantity(),
            requestOrderCreateDto.getQuantity() * menu.getPrice(),
            requestOrderCreateDto.getDeliveryAddr()
        );

        Order savedOrder = orderRepository.save(order);

        return new ResponseOrderCreateDto(
                savedOrder.getOrderId(),
                savedOrder.getMenuId().getMenuId(),
                savedOrder.getOrderStatus(),
                savedOrder.getQuantity(),
                savedOrder.getDeliveryAddr(),
                savedOrder.getOrderPrice()
        );
    }

    @Transactional
    public List<ResponseOrderListDto> orderSearchAll(String loginId) {
        // 유저 조회
        User user = userRepository.findByLoginId(loginId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 유저입니다.")
        );

        // 조회 분리 (OWNER/CUSTOMER) Spring DATA JPA Query Methods
        if(user.getUserType().equals(UserType.OWNER)){
            List<Order> orders = orderRepository.findAllByMenuId_OwnerId_UserId(user.getUserId());
            List<ResponseOrderListDto> ordersDto = new ArrayList<>();
            for(Order o : orders){
                ResponseOrderListDto dto = new ResponseOrderListDto(
                    o.getOrderId(),
                    o.getMenuId().getMenuId(),
                    o.getOrderStatus(),
                    o.getQuantity(),
                    o.getDeliveryAddr(),
                    o.getOrderPrice()
                ) ;
                ordersDto.add(dto);
            }
            return ordersDto;
        }else if(user.getUserType().equals(UserType.CUSTOMER)){
            List<Order> orders = orderRepository.findByOdererId_UserId(user.getUserId());
            List<ResponseOrderListDto> ordersDto = new ArrayList<>();
            for(Order o : orders){
                ResponseOrderListDto dto = new ResponseOrderListDto(
                        o.getOrderId(),
                        o.getMenuId().getMenuId(),
                        o.getOrderStatus(),
                        o.getQuantity(),
                        o.getDeliveryAddr(),
                        o.getOrderPrice()
                ) ;
                ordersDto.add(dto);
            }
            return ordersDto;
        }else{
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "정상적인 접근이 아닙니다.(USER ROLE)");
        }
    }

    //본인 주문만 취소할 수 있다. 다른 손님의 주문이면 403
    //주문요청 상태일 때만 취소.
    //결제가 끝난 주문 등은 거절 (400 또는 409)
    //취소되면 상태가 주문취소로 상태 변경 (200 또는 204).
    @Transactional
    public void cancelOrder(Long orderId, String loginId){
        // 유저 조회
        User user = userRepository.findByLoginId(loginId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 유저입니다.")
        );

        Order order = orderRepository.findById(orderId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 주문입니다.")
        );

        if(!order.getOdererId().getUserId().equals(user.getUserId())){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN,"본인의 주문만 취소 가능합니다.");
        }

        if(!order.getOrderStatus().canTransitionTo(OrderStatus.CANCELED)){
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "주문요청 상태에서만 취소 가능합니다.");
        }
        order.cancel();
    }

    // 사용자·주문 조회
    // OWNER인지, 본인 메뉴의 주문인지 검사 → 아니면 403
    // 이번 API의 목표 상태가 ACCEPTED 또는 COMPLETED인지 검사
    // 현재 상태.canTransitionTo(nextStatus) 검사 → 불가능하면 400
    // 주문 상태 변경
    @Transactional
    public void updateOrderStatus(Long orderId,OrderStatus orderStatus, String loginId) {
        // 유저 조회
        User user = userRepository.findByLoginId(loginId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"존재하지 않는 유저입니다.")
        );

        if(!user.getUserType().equals(UserType.OWNER)){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN,"고객은 주문 상태 변경이 불가능합니다.");
        }

        // 주문 내역 조회
        Order order = orderRepository.findByOrderId(orderId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "해당 주문이 존재하지 않습니다.")
        );

        // 본인 주문 내역인지 조회
        Long ownerId = order.getMenuId().getOwnerId().getUserId();
        if(!ownerId.equals(user.getUserId())){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "사장님에게 주문한 메뉴만 상태변경이 가능합니다.");
        }

        boolean allowedTarget = orderStatus == OrderStatus.ACCEPTED || orderStatus == OrderStatus.COMPLETED;
        if(!order.getOrderStatus().canTransitionTo(orderStatus) || !allowedTarget){
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"해당 상태로 변경이 불가합니다.");
        }

        order.updateStatus(orderStatus);

    }
}
