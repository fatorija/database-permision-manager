#!/usr/bin/env python3

import logging
import random
import string
import yaml
import mysql.connector
import psycopg2


def get_users_list_yml_file():
    with open("config.yaml", 'r') as stream:
        return yaml.safe_load(stream)['users']


def get_random_string(length=31):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def create_postgres_user(user_name, password):
    return f"CREATE USER "{user_name}f" WITH ENCRYPTED PASSWORD '{password}';"

def grant_user_access_based_on_user_type_postgres(user_name, user_type, schema):
    if user_type == "Admin":
        return f"grant all privileges on {schema} test to {user_name};"
    elif user_type == "Backend":
        return f"grant select, insert, update, delete on all tables in schema {schema} to {user_name}"
    else:
        return f"grant select on all tables in schema {schema} to {user_name}"

def create_user_with_password(userName, password):
    return f"CREATE USER '{userName}'@'%' IDENTIFIED BY '{password}';"


def grant_user_permissions_based_on_user_type(userName, userType):
    if userType == "Admin":
        return f"GRANT ALTER,ALTER ROUTINE,CREATE,CREATE ROUTINE,CREATE TEMPORARY TABLES,CREATE USER,CREATE VIEW," \
               f"DELETE,DROP,EVENT,EXECUTE,INDEX,INSERT,LOCK TABLES,PROCESS,REFERENCES,RELOAD,REPLICATION CLIENT," \
               f"REPLICATION SLAVE,SELECT,SHOW DATABASES,SHOW VIEW,TRIGGER,UPDATE ON *.* TO '{userName}'@'%'; "
    elif userType == "Backend":
        return f"GRANT ALTER,ALTER ROUTINE,CREATE,CREATE ROUTINE,CREATE TEMPORARY TABLES,CREATE VIEW,DELETE,DROP," \
               f"EVENT,EXECUTE,INDEX,INSERT,LOCK TABLES,PROCESS,REFERENCES,RELOAD,REPLICATION CLIENT,REPLICATION " \
               f"SLAVE,SELECT,SHOW DATABASES,SHOW VIEW,TRIGGER,UPDATE ON *.* TO '{userName}'@'%'; "
    elif userType == "Finance":
        return f"GRANT CREATE, CREATE VIEW, EXECUTE, SELECT, SHOW VIEW ON *.* TO '{userName}'@'%';"
    else:
        return f"GRANT EXECUTE, SELECT, SHOW VIEW ON *.* TO '{userName}'@'%';"


def create_user_and_grant_permission_mysql_db():
    """ Mysql Config"""
    config = {
        'user': 'root',
        'password': 'adentro',
        'host': '127.0.0.1',
        'database': 'test',
        'raise_on_warnings': True
    }
    mysql_db = mysql.connector.connect(**config)
    mysql_cursor = mysql_db.cursor()

    """ Postgres Config"""
    postgres_db = psycopg2.connect(host="localhost",
                            port=5432,
                            database="test",
                            user="root",
                            password="adentro")

    postgres_cursor = postgres_db.cursor()

    try:
        for user in get_users_list_yml_file():
            """ Create User in Nation DB"""
            logging.info("Creating user in Nation's DB")
            random_password = get_random_string()
            mysql_query_create_user = create_user_with_password(user['username'], random_password)
            mysql_query_grant_access = grant_user_permissions_based_on_user_type(user['username'], user['userType'])
            mysql_cursor.execute(mysql_query_create_user)
            mysql_cursor.execute(mysql_query_grant_access)

            """ Create user in Realm DBs"""
            logging.info("Creating user in Realm's DB")
            postgres_query_create_user = create_postgres_user(user[username], random_password)

            #I need to create a list of schemas
            postgres_query_grant_access = grant_user_access_based_on_user_type_postgres(user['username'], user['userType'], schema)
            logging.info(f"Nation DB and Realm DB | User: {user['username']} Password: {random_password}")
    except mysql.connector.Error as e:
        logging.error("Something went wrong!!")
        logging.error(e)
    finally:
        mysql_db.close()


def main():
    logging.basicConfig(level=logging.INFO)
    create_user_and_grant_permission_mysql_db()


if __name__ == '__main__':
    main()
