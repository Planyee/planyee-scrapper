from app.util.DatabaseConnection import DatabaseConnection

class PlaceDao:

    def save(place):
        db = DatabaseConnection()
        cursor = db.cursor()

        # 이미 해당 값이 존재하는지 확인
        cursor.execute("SELECT name FROM category WHERE name = %s", (place.name,))
        exist = cursor.fetchone()

        if exist is None:
            # 값이 존재하지 않으면 인서트
            insert_sql = """
                        INSERT INTO id ()
                        VALUES (%s)
                    """
            insert_params = (place.name)
            cursor.execute(insert_sql, insert_params)

        db.commit()
        cursor.close()