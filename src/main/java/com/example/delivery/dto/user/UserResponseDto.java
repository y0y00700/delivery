package com.example.delivery.dto.user;

import com.example.delivery.entity.UserType;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class UserResponseDto {
        private String loginId;
        private String userName;
        private String email;
        private UserType userType;

    public UserResponseDto(String loginId, String userName, String email, UserType userType) {
        this.loginId = loginId;
        this.userName = userName;
        this.email = email;
        this.userType = userType;
    }
}
