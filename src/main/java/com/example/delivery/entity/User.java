package com.example.delivery.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "users")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User extends BaseEntity{
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long userId;
    @Column(length = 20, nullable = false , unique = true)
    private String loginId;
    @Column(length=100,nullable = false)
    private String password;
    @Column(length=50,nullable = false)
    private String userName;
    @Column(length=250,unique = true,nullable = false)
    private String email;
    @Enumerated(EnumType.STRING)
    @Column(length=10, nullable = false)
    private UserType userType;

    public User(String loginId, String password, String userName, String email,UserType userType) {
        this.loginId = loginId;
        this.password = password;
        this.userName = userName;
        this.email = email;
        this.userType = userType;
    }
}
