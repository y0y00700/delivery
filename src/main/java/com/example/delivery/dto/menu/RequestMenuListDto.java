package com.example.delivery.dto.menu;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class RequestMenuListDto {
    private Long menuId;
    private String menuName;
    private String menuDesc;
    private int price;
}
