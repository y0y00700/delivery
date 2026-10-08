package com.example.delivery.controller;

import com.example.delivery.dto.order.RequestOrderCreateDto;
import com.example.delivery.dto.order.RequestOrderStatusDto;
import com.example.delivery.dto.order.ResponseOrderCreateDto;
import com.example.delivery.dto.order.ResponseOrderListDto;
import com.example.delivery.security.UserDetailsImpl;
import com.example.delivery.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class OrderController {
    private final OrderService orderService;
    // 주문 생성
    @PostMapping("/api/order/")
    public ResponseEntity<ResponseOrderCreateDto> createOrder(@Valid @RequestBody RequestOrderCreateDto requestOrderCreateDto
                                                            , @AuthenticationPrincipal UserDetailsImpl userDetails){
        return ResponseEntity.ok(orderService.createOrder(requestOrderCreateDto,userDetails.getUsername()));
    }

    // 주문 목록 조회
    @GetMapping("/api/order/retrieve")
    public ResponseEntity<List<ResponseOrderListDto>> searchOrder(@AuthenticationPrincipal UserDetailsImpl userDetails){
        return ResponseEntity.ok(orderService.orderSearchAll(userDetails.getUsername()));
    }

    // 주문 취소 (CUSTOMER)
    @PutMapping("/api/order/cancel/{orderId}")
    public ResponseEntity<Void> cancelOrder(@PathVariable Long orderId,
                                            @AuthenticationPrincipal UserDetailsImpl userDetails){
        orderService.cancelOrder(orderId, userDetails.getUsername());
        return ResponseEntity.noContent().build();
    }

    // 주문 상태 변경 (OWNER)
    @PatchMapping("/api/order/{orderId}/status")
    public ResponseEntity<Void> updateOrder(
            @PathVariable("orderId") Long orderId,
            @Valid @RequestBody RequestOrderStatusDto requestDto,
            @AuthenticationPrincipal UserDetailsImpl userDetails
    ) {
        orderService.updateOrderStatus(
                orderId,
                requestDto.getOrderStatus(),
                userDetails.getUsername()
        );
        return ResponseEntity.noContent().build(); // 204
    }

}
