package com.example.delivery.repository;

import com.example.delivery.entity.Menu;
import com.example.delivery.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MenuRepository extends JpaRepository<Menu,Long> {
    Optional<Menu> findByMenuName(String menuName);
    // 동일 메뉴 이름 중복 체크
    boolean existsByOwnerIdAndMenuName(User ownerId, String menuName);
}
