package com.example.delivery.dto.menu;

import com.example.delivery.entity.User;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@NoArgsConstructor
@Getter
@Setter
public class ResponseMenuRegDto {
    private Long menuId;
    private String menuName;
    private String menuDesc;
    private int price;
    private Long ownerId;

    public ResponseMenuRegDto(Long menuId, String menuName, String menuDesc, int price, Long ownerId) {
        this.menuId = menuId;
        this.menuName = menuName;
        this.menuDesc = menuDesc;
        this.price = price;
        this.ownerId = ownerId;
    }
}
