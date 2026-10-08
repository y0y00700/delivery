package com.example.delivery.dto.order;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class RequestOrderCreateDto {
    @NotNull(message = "메뉴 ID는 필수입니다.")
    private Long menuId;

    @NotNull(message = "주문 수량은 필수입니다.")
    @Min(value = 1, message = "최소 주문 수량은 1입니다.")
    private Long quantity;

    @NotBlank(message = "배달 주소는 필수입니다.")
    private String deliveryAddr;
}
