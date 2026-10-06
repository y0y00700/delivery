package com.example.delivery.entity;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum OrderStatus {

    ORDERED("주문요청"),
    PAID("결제완료"),
    ACCEPTED("주문수락"),
    COMPLETED("배달완료"),
    CANCELED("주문취소");

    private final String description;

    public boolean canTransitionTo(OrderStatus nextStatus) {
        if (nextStatus == null) {
            return false;
        }

        return switch (this) {
            case ORDERED -> nextStatus == PAID || nextStatus == CANCELED;
            case PAID -> nextStatus == ACCEPTED;
            case ACCEPTED -> nextStatus == COMPLETED;
            case COMPLETED, CANCELED -> false;
        };
    }
}