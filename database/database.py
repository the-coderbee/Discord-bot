import peewee

from settings import db_name, db_host, db_port, db_user, db_pass

db = peewee.PostgresqlDatabase(db_name, user=db_user, password=db_pass, host=db_host, port=db_port)
# db = peewee.SqliteDatabase('gookyDB.db')
