package com.example.delivery.config;

import jakarta.servlet.DispatcherType;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http)
            throws Exception {

        http
                .authorizeHttpRequests(auth -> auth
                        // 오류 응답을 처리하는 내부 요청 허용
                        .dispatcherTypeMatchers(DispatcherType.ERROR).permitAll()

                        // 회원가입과 로그인은 인증 없이 허용
                        .requestMatchers(
                                HttpMethod.POST,
                                "/api/users/registry",
                                "/api/users/login"
                        ).permitAll()

                        // 나머지 요청은 인증 필요
                        .anyRequest().authenticated()
                )

                // 현재 두 API는 인증용 쿠키/세션을 만들지 않는 JSON API
                .csrf(csrf -> csrf.ignoringRequestMatchers(
                        "/api/users/registry",
                        "/api/users/login"
                ))

                // 세션에 인증 상태를 저장하지 않음
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )

                // 기본 로그인 화면과 HTTP Basic 인증 사용 안 함
                .formLogin(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)

                // 인증이 필요한 곳에 미인증 요청이 오면 401 반환
                .exceptionHandling(exception -> exception
                        .authenticationEntryPoint(
                                new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)
                        )
                );

        return http.build();
    }
}