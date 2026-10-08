package com.example.delivery.service;

import com.example.delivery.dto.menu.RequestMenuRegDto;
import com.example.delivery.dto.menu.RequestMenuUpdateDto;
import com.example.delivery.dto.menu.ResponseMenuListDto;
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

import java.util.ArrayList;
import java.util.List;


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
        }

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
    // 목록 조회 누구나
    // 삭제된 메뉴 빼고 보여준다.
    @Transactional
    public List<ResponseMenuListDto> searchMenuAll() {
        List<Menu> menus = menuRepository.findAllByDeletedAtIsNull();
        List<ResponseMenuListDto> rmlds = new ArrayList<>();
        for(Menu m : menus){
            ResponseMenuListDto rmld = new ResponseMenuListDto(
                    m.getMenuId(),
                    m.getMenuName(),
                    m.getMenuDesc(),
                    m.getPrice()
            );
            rmlds.add(rmld);
        }
        return rmlds;
    }

    // 메뉴 단건 조회
    @Transactional
    public ResponseMenuListDto searchMenuOne(Long menuId) {
        Menu menu = findActiveMenu(menuId);

        return new ResponseMenuListDto(
                menu.getMenuId(),
                menu.getMenuName(),
                menu.getMenuDesc(),
                menu.getPrice()
        );
    }

    // 메뉴 수정
    @Transactional
    public ResponseMenuListDto menuUpdate(Long menuId, RequestMenuUpdateDto requestMenuUpdateDto, String loginId) {

        User owner = userRepository.findByLoginId(loginId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.UNAUTHORIZED,
                        "인증된 사용자를 찾을 수 없습니다."
                ));

        if(owner.getUserType() != UserType.OWNER){
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,"사장님만 메뉴를 등록 할 수 있습니다."
            );
        }


        Menu menu = findActiveMenu(menuId);

        // 본인 메뉴만 수정 가능
        if (!menu.getOwnerId().getUserId().equals(owner.getUserId())) {
            throw new ResponseStatusException(
                    HttpStatus.FORBIDDEN,
                    "본인의 메뉴만 수정할 수 있습니다."
            );
        }

        // 이름이 바뀌는 경우 중복 검사
        if (!menu.getMenuName().equals(requestMenuUpdateDto.getMenuName())
                && menuRepository.existsByOwnerIdAndMenuName(
                owner, requestMenuUpdateDto.getMenuName())) {

            throw new ResponseStatusException(
                    HttpStatus.CONFLICT,
                    "이미 등록한 메뉴 이름입니다."
            );
        }

        // 조회한 엔티티의 값을 변경
        menu.update(
                requestMenuUpdateDto.getMenuName(),
                requestMenuUpdateDto.getMenuDesc(),
                requestMenuUpdateDto.getPrice()
        );

        return new ResponseMenuListDto(
                menu.getMenuId(),
                menu.getMenuName(),
                menu.getMenuDesc(),
                menu.getPrice()
        );
    }

    @Transactional
    public void menuDelete(Long menuId, String loginId) {
        User owner = userRepository.findByLoginId(loginId).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "인증된 사용자를 찾을 수 없습니다.")
        );

        if(owner.getUserType() != UserType.OWNER){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "사장님만 메뉴를 삭제 할 수 있습니다.");
        }

        Menu menu = findActiveMenu(menuId);

        if(!menu.getOwnerId().getUserId().equals(owner.getUserId())){
            throw new ResponseStatusException(HttpStatus.FORBIDDEN , "본인의 메뉴만 삭제 할 수 있습니다.");
        }
        menu.softDelete();
    }

    private Menu findActiveMenu(Long menuId) {
        return menuRepository.findByMenuIdAndDeletedAtIsNull(menuId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "해당 메뉴가 존재하지 않습니다."
                ));
    }
}
