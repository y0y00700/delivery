package com.example.delivery.dto.order;

import com.example.delivery.entity.OrderStatus;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class ResponseOrderListDto {
    private Long orderId;
    private Long menuId;
    private OrderStatus orderStatus;
    private Long quantity;
    private String deliveryAddr;
    private Long orderPrice;

    public ResponseOrderListDto(Long orderId, Long menuId, OrderStatus orderStatus, Long quantity, String deliveryAddr, Long orderPrice) {
        this.orderId = orderId;
        this.menuId = menuId;
        this.orderStatus = orderStatus;
        this.quantity = quantity;
        this.deliveryAddr = deliveryAddr;
        this.orderPrice = orderPrice;
    }

}
