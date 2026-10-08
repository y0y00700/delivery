package com.example.delivery.dto.menu;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor

public class RequestMenuUpdateDto {
    @NotBlank(message = "메뉴 이름은 필수입니다.")
    private String menuName;
    private String menuDesc;
    @Min(value = 1, message = "가격은 1원 이상이어야 합니다.")
    private int price;
}
