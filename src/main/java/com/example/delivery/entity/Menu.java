package com.example.delivery.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(
        name = "menus",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_menus_owner_menu_name",
                        columnNames = {"owner_id", "menu_name"}
                )
        }
)
public class Menu extends BaseEntity{
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long menuId;
    @Column(name="menu_name", nullable = false)
    private String menuName;
    @Column(length = 250)
    private String menuDesc;
    @Column(nullable = false)
    private int price;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name="owner_id", nullable = false)
    private User ownerId;
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    public Menu(String menuName, String menuDesc, int price, User ownerId) {
        this.menuName = menuName;
        this.menuDesc = menuDesc;
        this.price = price;
        this.ownerId = ownerId;
    }

    // 필드 변경 용 메서드 추가
    public void update(String menuName, String menuDesc, int price) {
        this.menuName = menuName;
        this.menuDesc = menuDesc;
        this.price = price;
    }

    // 상태 변경용 메서드 (삭제시,)
    public void softDelete(){
        this.deletedAt = LocalDateTime.now();
    }

}
