import time

import requests

from app.service.VisitSoulService import visitSoulService
from app.settings import TMAP_KEY
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection


def main():
    crawling()
    # convertAddressToCoordinate()



def crawling():
    visitSoulService()
    # DB 연결 끊기
    DatabaseConnection.close()
    # 셀레니움 웹 드라이버 종료
    ChromeDriver().quit()



def convertAddressToCoordinate():
    for i in range(754, 1919):
        try:
            DatabaseConnection.startTransaction()
            cursor = DatabaseConnection().cursor()
            sql = """
            SELECT address FROM place where id=(%s)
            """
            params = (i, )
            cursor.execute(sql, params)
            address = cursor.fetchone()
            url = f"https://apis.openapi.sk.com/tmap/geo/convertAddress?version=1&searchTypCd=NtoO&reqAdd={address}&reqMulti=S&resCoordType=WGS84GEO"
            headers = {
                "accept": "application/json",
                "appKey": TMAP_KEY
            }
            response = requests.get(url, headers=headers).json()
            # print(response)
            latitude = response["ConvertAdd"]["newAddressList"]["newAddress"][0]["newLat"]
            longitude = response["ConvertAdd"]["newAddressList"]["newAddress"][0]["newLon"]
            sqll = """
                    UPDATE place SET latitude = (%s), longitude = (%s) WHERE id = (%s)
                    """
            paramss = (latitude, longitude, i,)
            cursor.execute(sqll, paramss)
            DatabaseConnection.commitTransaction()
            time.sleep(1)
        except:
            print(address)



if __name__ == "__main__":
    main()
