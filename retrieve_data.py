import mysql.connector

# Database Info
host = 'qao3ibsa7hhgecbv.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
database = 'ckarluzwtzo4zjap'
username = 'ma4h494nauifz0bp'
password = 'bs5bbfj1xqildj67'

#initiate connection between python and MySQL
def connect():
    try:
        connection = mysql.connector.connect(host=host, database=database, user=username, password=password)
        if connection.is_connected():
            return connection
    except Exception as e:
        print("Error while connecting to MySQL database", e)
    return None


# close connection to MySQL database
def close_connection(connection):
    if connection.is_connected():
        connection.close()


# check if user with username and password exist
def check_records(username, connection):
    try:
        find_user = "SELECT * FROM users WHERE username IN ('" +str(username)+"')"

        cursor = connection.cursor()
        cursor.execute(find_user)
        row = cursor.fetchone()

        row_list = list(row)
        cursor.close()

        if len(row_list)!=0:
            return row_list
        
    except Exception as e:
        print("Error while retrieving user info", e)
    return []


# check if the username and password passed match
def verify_credentials(username, password, connection):
    try:
        find_user = "SELECT * FROM users WHERE username = '"+str(username)+"'"
        cursor = connection.cursor()
        cursor.execute(find_user)
        row = cursor.fetchone()

        row_list = list(row)
        cursor.close()

        if len(row_list)!=0:
            if row_list[1]==password:
                return row_list
    except Exception as e:
        print("Error while retrieving user info", e)
    return []


# Add user data to a database
def add_user(username, password, connection):
    try:
        stmt = "INSERT INTO users VALUES (%s, %s)"
        val = (str(username), str(password))
        cursor = connection.cursor()
        cursor.execute(stmt, val)
        connection.commit()
        cursor.close()
    except Exception as e:
        print("Failed to enter in user", e)