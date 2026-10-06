package com.example.delivery.controller;

import com.example.delivery.dto.UserLoginRequestDto;
import com.example.delivery.dto.UserLoginResponseDto;
import com.example.delivery.dto.UserRequestDto;
import com.example.delivery.dto.UserResponseDto;
import com.example.delivery.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
    // 회원가입
    // 실패시 각 상태코드 반환 아이디 4~20 | 비밀번호 8자 이상 실패시, 400
    // 중복된 아이디 가입 x 409
    // 비밀번호는 BCrypt로 암호화
    @PostMapping("/api/users/registry")
    public ResponseEntity<UserResponseDto> register(@Valid @RequestBody UserRequestDto userRequestDto){
        return ResponseEntity.ok(userService.register(userRequestDto));
    }

    // 로그인 jwt 쿠키 생성 반환 상태코드 : 200
    // 토큰 아이디 / 역할 / 만료시간
    // 존재하지 않는 아이디 or 비밀번호 틀리면 401
    @PostMapping("/api/users/login")
    public ResponseEntity<UserLoginResponseDto> login(@RequestBody UserLoginRequestDto userLoginRequestDto){
        return ResponseEntity.ok(userService.login(userLoginRequestDto));
//        헤더에 반환시,
//        return ResponseEntity.ok().header(HttpHeaders.AUTHORIZATION, result.getToken()).build();
    }
}
