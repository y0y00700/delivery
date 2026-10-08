package com.example.delivery.controller;

import com.example.delivery.dto.menu.*;
import com.example.delivery.security.UserDetailsImpl;
import com.example.delivery.service.MenuService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

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

    // 메뉴 전체 조회(ALL)
    @GetMapping("/api/menus/")
    public ResponseEntity<List<ResponseMenuListDto>> retrieveListAll(){
        return ResponseEntity.ok(menuService.searchMenuAll());
    }

    // 메뉴 단건 조회
    @GetMapping("/api/menus/{menuId}")
    public ResponseEntity<ResponseMenuListDto> retrieveOne(@PathVariable Long menuId){
        return ResponseEntity.ok(menuService.searchMenuOne(menuId));
    }

    // 메뉴 수정
    @PutMapping("/api/menus/{menuId}")
    public ResponseEntity<ResponseMenuListDto> update(
            @PathVariable("menuId") Long menuId,
            @Valid @RequestBody RequestMenuUpdateDto requestMenuUpdateDto,
            @AuthenticationPrincipal UserDetailsImpl userDetails){
        return ResponseEntity.ok(menuService.menuUpdate(menuId, requestMenuUpdateDto, userDetails.getUsername()));
    }

    // 메뉴 삭제
    @DeleteMapping("/api/menus/{menuId}")
    public ResponseEntity<Void> delete(@PathVariable Long menuId,
                                       @AuthenticationPrincipal UserDetailsImpl userDetails){
        menuService.menuDelete(menuId,userDetails.getUsername());

        return ResponseEntity.noContent().build();
    }
}
