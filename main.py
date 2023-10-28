from app.service.VisitSoulService import visitSoulService
from app.util.ChromeDriver import ChromeDriver
from app.util.DatabaseConnection import DatabaseConnection


def main():
    #convert()

    visitSoulService()

    # DB 연결 끊기
    # DatabaseConnection.close()

    # 셀레니움 웹 드라이버 종료
    # ChromeDriver().quit()

# def convert():
#     for i in range(240, 1674):
#         DatabaseConnection.startTransaction()
#         cursor = DatabaseConnection().cursor()
#         sql = """
#         SELECT address FROM place where id=(%s)
#         """
#         params = (i, )
#         cursor.execute(sql, params)


if __name__ == "__main__":
    main()
