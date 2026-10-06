package com.example.delivery.entity;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum UserType {
    CUSTOMER("손님"),
    OWNER("사장님");

    private final String description;
}
