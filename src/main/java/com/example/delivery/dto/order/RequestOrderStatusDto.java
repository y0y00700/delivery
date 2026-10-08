package com.example.delivery.dto.order;

import com.example.delivery.entity.OrderStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class RequestOrderStatusDto {

    @NotNull(message = "변경할 주문 상태를 입력해 주세요.")
    private OrderStatus orderStatus;
}