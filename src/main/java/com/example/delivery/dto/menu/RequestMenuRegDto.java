package com.example.delivery.dto.menu;

import com.example.delivery.entity.User;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@Getter
public class RequestMenuRegDto {
    private Long menuId;
    @NotBlank(message = "메뉴 이름은 필수입니다.")
    private String menuName;
    private String menuDesc;
    @Min(value = 1, message = "가격은 1원 이상이어야 합니다.")
    private int price;
    //private User ownerId;
}
