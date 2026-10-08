package com.example.delivery.dto.order;

import com.example.delivery.entity.OrderStatus;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ResponseOrderCreateDto {
    private Long menuId;
    private OrderStatus orderStatus;
    private Long quantity;
    private String deliveryAddr;
    private Long orderPrice;

    public ResponseOrderCreateDto(Long menuId, OrderStatus orderStatus, Long quantity, String deliveryAddr, Long orderPrice) {
        this.menuId = menuId;
        this.orderStatus = orderStatus;
        this.quantity = quantity;
        this.deliveryAddr = deliveryAddr;
        this.orderPrice = orderPrice;
    }
}
