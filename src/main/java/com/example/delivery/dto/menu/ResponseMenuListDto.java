package com.example.delivery.dto.menu;

import com.example.delivery.entity.User;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class ResponseMenuListDto {
    private Long menuId;
    private String menuName;
    private String menuDesc;
    private int price;

    public ResponseMenuListDto(Long menuId, String menuName, String menuDesc, int price) {
        this.menuId = menuId;
        this.menuName = menuName;
        this.menuDesc = menuDesc;
        this.price = price;
    }


}
