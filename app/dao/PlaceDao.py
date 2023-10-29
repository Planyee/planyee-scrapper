from app.util.DatabaseConnection import DatabaseConnection
class PlaceDao:

    def save(place):
        # 커서 가져오기
        cursor = DatabaseConnection().cursor()

        # 이미 해당 값이 존재하는지 확인
        select_sql = "SELECT * FROM place JOIN place_category ON place.id = place_category.place_id JOIN category ON place_category.category_id = category.id WHERE place.name = %s AND category.name = %s"
        select_params = (place.name, place.category)
        cursor.execute(select_sql, select_params)
        exist = cursor.fetchone()

        if not exist:
            # 값이 존재하지 않으면 인서트
            insert_sql = """
                        INSERT INTO place (name, address, image_url, description, etc)
                        VALUES (%s, %s, %s, %s, %s)
                    """
            insert_params = (place.name, place.address, place.img_url, place.desc, place.info)
            cursor.execute(insert_sql, insert_params)
            place_id = cursor.lastrowid

            selectt_sql = "SELECT id FROM category WHERE name = %s"
            selectt_params = (place.category,)
            cursor.execute(selectt_sql, selectt_params)
            result = cursor.fetchone()
            category_id = result[0]

            insertt_sql = """
                        INSERT INTO place_category (place_id, category_id)
                        VALUES (%s, %s)
                    """
            insertt_params = (place_id, category_id)
            cursor.execute(insertt_sql, insertt_params)
