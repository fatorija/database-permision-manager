#!/usr/bin/env python3

import logging
import random
import string
import yaml
import mysql.connector
from psycopg2 import connect, extensions


def get_users_and_servers_lists_yml_file():
    with open("config.yaml", 'r') as stream:
        data = yaml.safe_load(stream)
        return data['users'], data['servers']


def get_random_string(length=31):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))


def get_postgresql_connection(server):
    """ Postgres Config"""
    postgres_db = connect(host=server['server_url'],
                        port=5432,
                        user=server['admin']['username'],
                        password=server['admin']['password'])

    postgres_db.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return postgres_db


def get_mysql_connection(server):
    """ Mysql Config"""
    config = {
        'user': server["admin"]["username"],
        'password': server["admin"]["password"],
        'host': server["server_url"],
        'raise_on_warnings': True
    }
    mysql_db = mysql.connector.connect(**config)
    return mysql_db


def create_postgres_user(user_name, password):
    return f"CREATE ROLE \"{user_name}\" WITH ENCRYPTED PASSWORD '{password}';"


def grant_user_access_based_on_user_type_postgres(user_name, user_type, schema):
    if user_type == "Admin":
        return f"GRANT ALL ON ALL TABLES IN SCHEMA {schema} TO \"{user_name}\";"
    elif user_type == "Backend":
        return f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {schema} TO \"{user_name}\""
    else:
        return f"grant select on all tables in schema {schema} to \"{user_name}\""


def create_user_with_password(user_name, password):
    return f"CREATE USER '{user_name}'@'%' IDENTIFIED BY '{password}';"


def grant_user_permissions_based_on_user_type(user_name, user_type):
    if user_type == "Admin":
        return f"GRANT ALTER,ALTER ROUTINE,CREATE,CREATE ROUTINE,CREATE TEMPORARY TABLES,CREATE USER,CREATE VIEW," \
               f"DELETE,DROP,EVENT,EXECUTE,INDEX,INSERT,LOCK TABLES,PROCESS,REFERENCES,RELOAD,REPLICATION CLIENT," \
               f"REPLICATION SLAVE,SELECT,SHOW DATABASES,SHOW VIEW,TRIGGER,UPDATE ON *.* TO '{user_name}'@'%'; "
    elif user_type == "Backend":
        return f"GRANT ALTER,ALTER ROUTINE,CREATE,CREATE ROUTINE,CREATE TEMPORARY TABLES,CREATE VIEW,DELETE,DROP," \
               f"EVENT,EXECUTE,INDEX,INSERT,LOCK TABLES,PROCESS,REFERENCES,RELOAD,REPLICATION CLIENT,REPLICATION " \
               f"SLAVE,SELECT,SHOW DATABASES,SHOW VIEW,TRIGGER,UPDATE ON *.* TO '{user_name}'@'%'; "
    elif user_type == "Finance":
        return f"GRANT CREATE, CREATE VIEW, EXECUTE, SELECT, SHOW VIEW ON *.* TO '{user_name}'@'%';"
    else:
        return f"GRANT EXECUTE, SELECT, SHOW VIEW ON *.* TO '{user_name}'@'%';"


def create_user_and_grant_permission_mysql_db(server, users):
    try:
        db = get_mysql_connection(server)
        cursor = db.cursor()
        for user in users:
            mysql_query_create_user = create_user_with_password(user['username'], user["password"])
            mysql_query_grant_access = grant_user_permissions_based_on_user_type(user['username'], user['userType'])
            # logging.info(f"Creating user: {user['username']} in: {server['engine']}/{server['server_url']}")
            cursor.execute(mysql_query_create_user)
            logging.info(f"Created user in {server['server_url']} | User: {user['username']} Password: {user['password']}")
            cursor.execute(mysql_query_grant_access)
            logging.info(
                f"Granted Access in {server['server_url']} | User: {user['username']} as {user['userType']}")
    except mysql.connector.Error as e:
        logging.error("Something went wrong!!")
        logging.error(e)
    finally:
        cursor.close()
        db.close()


def create_user_and_grant_permission_postgre_db(server, users):
    try:
        db = get_postgresql_connection(server)
        cursor = db.cursor()
        for user in users:
            postgres_query_create_user = create_postgres_user(user['username'], user['password'])
            # logging.info(f"Creating user: {user['username']} in: {server['engine']}/{server['server_url']}")
            cursor.execute(postgres_query_create_user)
            logging.info(f"Created user in {server['server_url']} | User: {user['username']} Password: {user['password']}")
            for schema in server["schemas"]:
                # logging.info(f"Now granting access to {user['username']} in {schema}")
                postgres_query_grant_access = grant_user_access_based_on_user_type_postgres(user['username'], user['userType'], schema)
                cursor.execute(postgres_query_grant_access)
                logging.info(
                    f"Granted Access in {server['server_url']}/{schema} | User: {user['username']} as {user['userType']}")
    except mysql.connector.Error as e:
        logging.error("Something went wrong!!")
        logging.error(e)
    finally:
        cursor.close()
        db.close()


def create_users(server, users):
    try:
        if server["engine"].find("postgresql") != -1:
            create_user_and_grant_permission_postgre_db(server, users)
        else:
            if server["engine"] == "mysql":
                create_user_and_grant_permission_mysql_db(server, users)
    except Exception as e:
        logging.error("Server " + server["engine"] + " failed with ", e)


def add_password_to_users(users):
    for user in users:
        user["password"] = get_random_string()


def test_connection(server):
    print("Testing connection: " + server["engine"])
    try:
        if server["engine"].find("postgresql") != -1:
            query = "SELECT datname FROM pg_database;"
            print(server["schemas"])
            for db in server["schemas"]:
                print('URL: ' + server["server_url"] + ", db: " + db)
                db = get_postgresql_connection(server, db)
                cursor = db.cursor()
                result = cursor.execute(query)
                print(f" Result = {result}")
        else:
            if server["engine"] == "mysql":
                query = "SHOW DATABASES;"
                print('URL: ' + server["server_url"])
                db = get_mysql_connection(server)
                cursor = db.cursor()
                result = cursor.execute(query)
                print(result)
    except Exception as e:
        print("Server " + server["engine"] + " failed with ")
        raise e


def main():
    logging.basicConfig(level=logging.INFO)
    users, servers = get_users_and_servers_lists_yml_file()
    add_password_to_users(users)
    for server in servers:
        # test_connection(server)
        create_users(server, users)

if __name__ == '__main__':
    main()
