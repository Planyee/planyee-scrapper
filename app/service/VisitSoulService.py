import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.PlaceDao import PlaceDao
from app.model.Place import Place
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection

def visitSoulService():
    # ChromeDriver 가져오기
    driver = ChromeDriver()
    wait = WebDriverWait(driver, 20)

    categories = [["attractions", [68, "랜드마크"], [69, "고궁"], [70, "역사적 장소"], [71, "오래가게"], [966, "미술관&박물관"]],
                  ["nature", [80, "산"], [81, "강&계곡"], [82, "섬"], [83, "공원&정원"], [84, "식물원"]],
                  ["entertainment", [326, "문화"], [327, "휴식"], [328, "스포츠"], [329, "놀이공원&테마파크"], [330, "체험"]],
                  ["shopping", [48, "쇼핑몰&백화점"], [49, "면세점"], [50, "마켓"], [51, "뷰티"], [52, "한류&관광상품"]],
                  ["restaurants", [59, "카페&디저트"], [60, "주점"], [61, "한식"], [62, "중식"], [63, "일식"], [64, "아시아식"], [65, "서양식"], [66, "채식"], [67, "할랄"], [1460, "백년가게"]]]

    base_url = "https://korean.visitseoul.net/"

    # 대분류 가져오기
    for category in categories:
        category_suffix = category[0]
        subcategory_count = len(category) - 1

        # 소분류 가져오기
        for i in range(1, subcategory_count + 1):
            subcategory = category[i]

            # 분류된 정보 조회 url 생성
            url = base_url + category_suffix + '?srchCtgry=' + str(subcategory[0])

            # 웹 사이트에 접속
            driver.get(url)

            # 페이지 번호와 다음 페이지 링크를 초기화
            page_number = 1
            next_page_link = None

            while True:
                # 아이템 페이지에서 정보 추출
                items = driver.find_elements(By.CSS_SELECTOR, ".article-list li.item")

                for item in items:
                    try:
                        # DB 트랜잭션 시작
                        DatabaseConnection.startTransaction()

                        item_link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                        # 새로운 창에서 작업 세팅
                        driver.execute_script("window.open('', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.get(item_link)

                        # 제목 추출
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.h3.textcenter")))
                        title_element = driver.find_element(By.CSS_SELECTOR, "h3.h3.textcenter")
                        name = title_element.text
                        # print(name)

                        # 주소 정보 추출
                        wait.until(EC.presence_of_element_located((By.XPATH, '//dt[text()="주소"]/following-sibling::dd')))
                        address_element = driver.find_element(By.XPATH, '//dt[text()="주소"]/following-sibling::dd')
                        address = address_element.text
                        # print(address)

                        # 사진 정보 추출
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".owl-stage-outer .owl-stage .owl-item.active .item")))
                        image_path = driver.find_element(By.CSS_SELECTOR, ".owl-stage-outer .owl-stage .owl-item.active .item").get_attribute('style')
                        full_image_path = "https://korean.visitseoul.net" + re.search(r'url\(["\']?(.*?)["\']?\)', image_path).group(1)
                        # print(full_image_path)

                        # 장소 설명 추출
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text-area")))
                        description = driver.find_element(By.CSS_SELECTOR, ".text-area").text
                        # print(description)

                        # "detail-map-infor" 클래스 내의 모든 dt와 dd 태그를 찾습니다.
                        dt_elements = driver.find_elements(By.CSS_SELECTOR, ".detail-map-infor dt")
                        dd_elements = driver.find_elements(By.CSS_SELECTOR, ".detail-map-infor dd")
                        # dt와 dd의 값을 key와 value로 사용하여 dictionary를 생성합니다.
                        information = {}
                        for dt, dd in zip(dt_elements, dd_elements):
                            key = dt.text
                            value = dd.text
                            information[key] = value
                        # print(information)

                        #DB에 맞게 수정사항
                        place = Place(name, address, subcategory[1], full_image_path, description, information)

                        # DB저장
                        PlaceDao.save(place)

                        # 트랜잭션 커밋
                        DatabaseConnection.commitTransaction()
                        # print(place.name, " ", place.category)

                        # 원래 창으로 전환
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print(name, " ", subcategory, " 크롤링 실패")
                        # 원래 창으로 전환
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue


                # 페이지 번호 증가
                page_number += 1

                # 다음 페이지 링크 갱신
                try:
                    next_page_link = driver.find_element(By.XPATH, f"//a[@href='?curPage={page_number}&srchCtgry={subcategory[0]}']")
                    next_page_link = next_page_link.get_attribute("href")
                    driver.get(next_page_link)
                except:
                    break
