package com.example.delivery.repository;

import com.example.delivery.entity.Menu;
import com.example.delivery.entity.User;
import jakarta.validation.constraints.NotBlank;
import org.springframework.data.jpa.repository.JpaRepository;

import java.lang.ScopedValue;
import java.util.List;
import java.util.Optional;

public interface MenuRepository extends JpaRepository<Menu,Long> {
    Optional<Menu> findByMenuName(String menuName);
    // 동일 메뉴 이름 중복 체크
    boolean existsByOwnerIdAndMenuName(User ownerId, String menuName);
    // 삭제시, NULL 조건 (전체 조회)
    List<Menu> findAllByDeletedAtIsNull();
    // 단건 조회시,
    Optional<Menu> findByMenuIdAndDeletedAtIsNull(Long menuId);

    //Optional<Menu> findByMenuId(Menu menuId);
}
