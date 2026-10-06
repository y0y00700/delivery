package com.example.delivery.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "orders")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Order extends BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long orderId;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name="orderer_id", nullable = false)
    private User odererId;
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name="menu_id", nullable = false)
    private Menu menuId;
    @Enumerated(EnumType.STRING)
    @Column(length = 10, nullable = false)
    private OrderStatus orderStatus = OrderStatus.ORDERED;
    @Column(nullable = false)
    private Long quantity;
    @Column(nullable = false)
    private Long orderPrice;

    public Order(User odererId, Menu menuId, Long quantity, Long orderPrice) {
        this.odererId = odererId;
        this.menuId = menuId;
        this.quantity = quantity;
        this.orderPrice = orderPrice;
    }

}
