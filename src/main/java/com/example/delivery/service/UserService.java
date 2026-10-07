package com.example.delivery.service;

import com.example.delivery.dto.user.UserRequestDto;
import com.example.delivery.dto.user.UserResponseDto;
import com.example.delivery.entity.User;
import com.example.delivery.jwt.JwtUtil;
import com.example.delivery.repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service

@RequiredArgsConstructor
public class UserService {
    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private final JwtUtil jwtUtil;

//    Spring Security -> Filter 영역에서 Control 하므로 제거(주석)
//    @Transactional
//    public UserLoginResponseDto login(UserLoginRequestDto userLoginRequestDto) {
//        // 존재하지 않는 아이디 체크
//        User loginUser = userRepository.findByLoginId(userLoginRequestDto.getLoginId()).orElseThrow(
//                () -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "ID 또는 PW 가 일치하지 않습니다.")
//        );
//        boolean passMatches = passwordEncoder.matches(
//                userLoginRequestDto.getPassword(),
//                loginUser.getPassword()
//        );
//        // 비밀번호 불일치 체크
//        if(!passMatches){
//            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,"ID 또는 PW 가 일치하지 않습니다.");
//        }
//
//        // 아이디·비밀번호가 맞으면 JWT를 발급 응답 본문이나 헤더 중 편한 곳에 반환 (200).
//        // 로그인 jwt 쿠키 생성 반환 상태코드 : 200
//        // 토큰 아이디 / 역할 / 만료시간
//
//        // JWT 생성 및 쿠키에 저장 후 Response 객체에 추가
//        String token = jwtUtil.createToken(loginUser.getLoginId(), loginUser.getUserType());
//
//        // response 객체에 넣을 필요 없으므로 생략
//        // jwtUtil.addJwtToCookie(token, res);
//
//        UserLoginResponseDto responseDto = new UserLoginResponseDto(
//                loginUser.getLoginId(),
//                loginUser.getUserName(),
//                loginUser.getEmail(),
//                loginUser.getUserType()
//        );
//        responseDto.setToken(token);
//
//        return responseDto;
//    }

    @Transactional
    public UserResponseDto register(UserRequestDto userRequestDto) {

        // Validation 체크
        // ID
        if (userRepository.findByLoginId(userRequestDto.getLoginId()).isPresent()) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "이미 사용 중인 ID입니다."
            );
        }
        // 이메일
        if (userRepository.findByEmail(userRequestDto.getEmail()).isPresent()) {
            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "이미 사용 중인 이메일입니다."
            );
        }

        // Bcrypt 암호화
        String encodePass = passwordEncoder.encode(userRequestDto.getPassword());

        User user = new User(
                userRequestDto.getLoginId(),
                encodePass,
                userRequestDto.getUserName(),
                userRequestDto.getEmail(),
                userRequestDto.getUserType()
        );

        User savedUser = userRepository.save(user);
        return new UserResponseDto(
                savedUser.getLoginId(),
                savedUser.getUserName(),
                savedUser.getEmail(),
                savedUser.getUserType()
               );
    }
}
