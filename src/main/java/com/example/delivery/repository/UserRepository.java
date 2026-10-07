package com.example.delivery.repository;

import com.example.delivery.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.lang.ScopedValue;
import java.util.Optional;


public interface UserRepository extends JpaRepository<User,Long> {
    Optional<User> findByLoginId(String loginId);
    Optional<User> findByEmail(String email);

    <T> ScopedValue<T> findByUsername(String username);

    //<T> ScopedValue<T> findByUserId(Long userId);
}
