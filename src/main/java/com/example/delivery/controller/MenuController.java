package com.example.delivery.controller;

import com.example.delivery.dto.menu.RequestMenuRegDto;
import com.example.delivery.dto.menu.ResponseMenuRegDto;
import com.example.delivery.security.UserDetailsImpl;
import com.example.delivery.service.MenuService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class MenuController {
    private final MenuService menuService;
    // 메뉴 등록
    @PostMapping("/api/menus/registry")
    public ResponseEntity<ResponseMenuRegDto> regist(@Valid @RequestBody RequestMenuRegDto requestMenuRegDto
            , @AuthenticationPrincipal UserDetailsImpl userDetails){
        return ResponseEntity.ok(menuService.register(requestMenuRegDto,userDetails.getUsername()));
    }

}
