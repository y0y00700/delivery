package com.example.delivery.controller;

import com.example.delivery.dto.user.UserRequestDto;
import com.example.delivery.dto.user.UserResponseDto;
import com.example.delivery.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
// 로그인이 필요한 요청은 Authorization: Bearer {토큰} 헤더로 보내고, 서버는 요청마다 필터에서 토큰을 검증
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

//    Spring Security Filter 영역에서 컨트롤 하므로 제거
//    @PostMapping("/api/users/login")
//    public ResponseEntity<UserLoginResponseDto> login(@RequestBody UserLoginRequestDto userLoginRequestDto){
//        return ResponseEntity.ok(userService.login(userLoginRequestDto));
//        헤더에 반환시,
//        return ResponseEntity.ok().header(HttpHeaders.AUTHORIZATION, result.getToken()).build();
//    }
}
