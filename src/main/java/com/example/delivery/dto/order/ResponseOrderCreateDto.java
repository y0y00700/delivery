package com.example.delivery.dto.order;

import com.example.delivery.entity.Menu;
import com.example.delivery.entity.OrderStatus;
import com.example.delivery.entity.User;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ResponseOrderCreateDto {
    private Menu menuId;
    private OrderStatus orderStatus;
    private Long quantity;
    private String deliveryAddr;
    private Long orderPrice;

    public ResponseOrderCreateDto(Menu menuId, OrderStatus orderStatus, Long quantity, String deliveryAddr, Long orderPrice) {
        this.menuId = menuId;
        this.orderStatus = orderStatus;
        this.quantity = quantity;
        this.deliveryAddr = deliveryAddr;
        this.orderPrice = orderPrice;
    }
}
