package com.example.delivery.dto;

import com.example.delivery.entity.UserType;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class UserRequestDto {
    @NotBlank @Size(min=4,max=20)
    private String loginId;
    @NotBlank @Size(min=8)
    private String password;
    @NotBlank @Size(max=50)
    private String userName;
    @NotBlank @Email @Size(max=250)
    private String email;
    @NotNull
    private UserType userType;
}