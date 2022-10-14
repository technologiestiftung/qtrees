RED='\033[0;31m'
NC='\033[0m'
echo -e "${RED}############ Setting up GIS ${NC}"
sleep 3
PGPASSWORD=${POSTGRES_PASSWD} psql --host=$DB_QTREES --port=5432 --username=postgres -a -f 01_create_gis_admin.sql
PGPASSWORD=${GIS_PASSWD} psql --host=$DB_QTREES --port=5432 --username=gis_admin --dbname=lab_gis -a -f 02_load_gis_extension.sql
echo "${RED}############ Setting up tables ${NC}"
sleep 3
PGPASSWORD=${POSTGRES_PASSWD} psql --host=$DB_QTREES --port=5432 --username=postgres --dbname=qtrees -a -f 03_setup_tables.sql
echo "${RED}############ Setting up postgREST ${NC}"
sleep 3
PGPASSWORD=${POSTGRES_PASSWD} psql --host=$DB_QTREES --port=5432 --username=postgres --dbname=qtrees -a -f 04_setup_postgrest.sql
echo "${RED}############ Adding JWT support ${NC}"
sleep 3
PGPASSWORD=${POSTGRES_PASSWD} psql --host=$DB_QTREES --port=5432 --username=postgres --dbname=qtrees -a -f 05_add_jwt.sql
echo "${RED}############ Setup sql user management ${NC}"
sleep 3
PGPASSWORD=${POSTGRES_PASSWD} psql --host=$DB_QTREES --port=5432 --username=postgres --dbname=qtrees -a -f 06_sql_user_management.sql

#export LC_CTYPE=C
#export JWT_SECRET=$(< /dev/urandom tr -dc A-Za-z0-9 | head -c32)