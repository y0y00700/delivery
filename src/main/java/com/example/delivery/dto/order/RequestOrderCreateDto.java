package com.example.delivery.dto.order;

import com.example.delivery.entity.Menu;
import com.example.delivery.entity.OrderStatus;
import com.example.delivery.entity.User;
import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

@Getter
@NoArgsConstructor
public class RequestOrderCreateDto {
    @NotBlank
    private Long menuId;
    @Enumerated(EnumType.STRING)
    private OrderStatus orderStatus;
    @NotBlank @Min(value = 1,message = "최소주문 수량은 1입니다.")
    private Long quantity;
    @NotBlank
    private String deliveryAddr;
}
