package com.example.delivery.service;

import com.example.delivery.dto.menu.RequestMenuRegDto;
import com.example.delivery.dto.menu.ResponseMenuRegDto;
import com.example.delivery.entity.Menu;
import com.example.delivery.entity.User;
import com.example.delivery.entity.UserType;
import com.example.delivery.repository.MenuRepository;
import com.example.delivery.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.transaction.annotation.Transactional;


@Service
@RequiredArgsConstructor
public class MenuService {
    private final MenuRepository menuRepository;
    private final UserRepository userRepository;

    @Transactional
    public ResponseMenuRegDto register(RequestMenuRegDto requestMenuRegDto, String loginId){

        // 검증된 토큰의 loginId로 메뉴 주인을 조회
        User owner = userRepository.findByLoginId(loginId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.UNAUTHORIZED,
                        "인증된 사용자를 찾을 수 없습니다."
                ));
//        User owner = userRepository.findById(requestMenuRegDto.getOwnerId().getUserId()).orElseThrow(
//                () -> new ResponseStatusException(HttpStatus.NOT_FOUND,"해당 사용자를 찾을 수 없습니다.")
//        );
        //
        if(owner.getUserType() != UserType.OWNER){
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,"사장님만 메뉴를 등록 할 수 있습니다."
            );
        }

        // 한 가게에 동일 메뉴이름 중복 등록 x
        if(menuRepository.existsByOwnerIdAndMenuName(owner,requestMenuRegDto.getMenuName())){
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 동일한 메뉴이름으로 등록하신 제품이 있습니다.");
        };


        Menu menu = new Menu(
                requestMenuRegDto.getMenuName(),
                requestMenuRegDto.getMenuDesc(),
                requestMenuRegDto.getPrice(),
                owner
        );

        Menu savedMenu = menuRepository.save(menu);

        return new ResponseMenuRegDto(
                savedMenu.getMenuId(),
                savedMenu.getMenuName(),
                savedMenu.getMenuDesc(),
                savedMenu.getPrice(),
                owner.getUserId()
        );
    }

}
