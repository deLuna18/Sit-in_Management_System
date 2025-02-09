from sqlite3 import connect,Row

database:str = 'usermanagement.db'

def getprocess(sql: str, params: tuple = ()) -> list:
    db = connect(database)
    cursor: object = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql, params)
    data: list = cursor.fetchall()
    db.close()
    return [dict(row) for row in data] 
    
def postprocess(sql: str, params: tuple = ()) -> bool:
    db = connect(database)
    cursor: object = db.cursor()
    cursor.execute(sql, params)
    db.commit()
    db.close()
    return cursor.rowcount > 0
    
def get_all_users() -> list:
    sql = "SELECT * FROM users"
    return getprocess(sql)

def get_username(username: str) -> list:
    sql = "SELECT * FROM users WHERE username = ?"
    return getprocess(sql, (username,))

def register_user(lastname: str, firstname: str, middlename: str, 
                  course: str, year_level: str, email_address: str, 
                  username: str, password: str) -> bool:
                  
    if get_username(username):
        return False  
        
    sql = "INSERT INTO users (lastname, firstname, middlename, course, year_level, email_address, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    return postprocess(sql, (lastname, firstname, middlename, course, year_level, email_address, username, password))

