package com.example.delivery.dto.user;

import com.example.delivery.entity.UserType;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class UserLoginRequestDto {
    @NotBlank
    private String loginId;
    @NotBlank
    private String password;
    private String userName;
    private String email;
    @NotBlank
    private UserType userType;
}
