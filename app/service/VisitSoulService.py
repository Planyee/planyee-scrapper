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
    # 웹 사이트에 접속
    driver.get("https://korean.visitseoul.net")

    categories = ["attractions", "nature", "entertainment", "shopping", "restaurants"]
    wait = WebDriverWait(driver, 20)

    for category in categories:
        category_element = driver.find_element(By.CSS_SELECTOR, f"a[href*='{category}']")
        category_link = category_element.get_attribute("href")

        # 각 카테고리 페이지로 이동
        driver.get(category_link)

        # 페이지 번호와 다음 페이지 링크를 초기화
        page_number = 1
        next_page_link = None

        while True:
            # 아이템 페이지에서 정보 추출
            items = driver.find_elements(By.CSS_SELECTOR, ".article-list li.item")


            for item in items:
                # DB 트랜잭션 시작
                DatabaseConnection.startTransaction()

                item_link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                #새로운 창에서 작업 세팅
                driver.execute_script("window.open('', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(item_link)

                # 아이템 페이지가 로딩될 때까지 대기
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.h3.textcenter")))

                # 제목 추출
                title_element = driver.find_element(By.CSS_SELECTOR, "h3.h3.textcenter")
                name = title_element.text

                # 위도 경도 더미값 설정
                longitude = None
                latitude = None

                # 주소 정보 추출
                address_element = driver.find_element(By.XPATH, '//dt[text()="주소"]/following-sibling::dd')
                address = address_element.text

                place = Place(name, address, longitude, latitude)

                # DB저장
                PlaceDao.save(place)

                # 트랜잭션 커밋
                DatabaseConnection.commitTransaction()

                # 원래 창으로 전환
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # 페이지 번호 증가
            page_number += 1

            # 다음 페이지 링크 갱신
            next_page_link = driver.find_element(By.XPATH, f"//a[@href='?curPage={page_number}']")
            next_page_link = next_page_link.get_attribute("href")

            # 다음 페이지로 이동
            if next_page_link:
                driver.get(next_page_link)
            else:
                break









