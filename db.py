import os
import psycopg2 # pip install psycopg2-binary



def setup_db():
	DATABASE_URL = os.environ['DATABASE_URL']
	conn = psycopg2.connect(host=os.environ['POSTGRESQL_SERVICE_HOST'],database=os.environ['POSTGRESQL_DATABASE'], user=os.environ['POSTGRESQL_USER'], password=os.environ['POSTGRESQL_PASSWORD'], sslmode='require')
	db = conn.cursor()
	db.execute("create extension if not exists cube;")
	db.execute("drop table if exists vectors")
	db.execute("create table vectors (id serial, file varchar, vec_low cube, vec_high cube);")
	db.execute("create index vectors_vec_idx on vectors (vec_low, vec_high);")
	conn.commit()
	db.close()
	conn.close()

setup_db()

