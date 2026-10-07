package com.example.delivery.entity;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum UserType {
    CUSTOMER("손님"),
    OWNER("사장님");

    private final String description;

    public String getAuthority() {
        return this.description;
    }

    public static class Authority {
        public static final String CUSTOMER = "CUSTOMER";
        public static final String OWNER = "OWNER";
    }

}
