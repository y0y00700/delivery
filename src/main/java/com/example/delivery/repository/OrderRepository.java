package com.example.delivery.repository;


import com.example.delivery.entity.Order;
import com.example.delivery.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import javax.swing.text.html.Option;
import java.util.List;
import java.util.Optional;

public interface OrderRepository extends JpaRepository<Order,Long> {
    List<Order> findByOdererId_UserId (Long userId);
    List<Order> findAllByMenuId_OwnerId_UserId(Long userId);
    //Optional<Order> findByOrderIdAndMenuId_OwnerId_UserId(Long orderId,Long ownerId);
    Optional<Order> findByOrderId(Long orderId);
}
