# blog

### Startup
```
pip install Flask
pip install flask_sqlalchemy flask-login
pip install psycopg2-binary
flask --app test run
```

### TinyMCE
Load and unpack into static:
```
https://www.tiny.cloud/blog/self-host-tinymce/
```
Fix:
```
sed -i 's@Upgrade@Z@g' themes/silver/theme.min.js
sed -i 's@https://www.tiny.cloud/tinymce-self-hosted-premium-features/?utm_source=TinyMCE&utm_medium=SPAP&utm_campaign=SPAP&utm_id=editorreferral@Z@g' themes/silver/theme.min.js
sed -i 's@https://www.tiny.cloud/powered-by-tiny?utm_campaign=editor_referral&utm_medium=poweredby&utm_source=tinymce&utm_content=v6@Z@g' themes/silver/theme.min.js
```

### DB
Run new Postgres DB in Docker:
```
sudo apt  install docker
sudo docker run --name blog-postgres -e POSTGRES_PASSWORD=test123 -d -p 5432:5432 postgres
sudo docker exec -it blog-postgres bash
psql -U postgres
CREATE DATABASE blog;
\q
```

Test DB from host:
```
sudo apt install postgresql-client-common postgresql-client-14
psql -h localhost -p 5432 -U postgres
```

Restart Container if failed:
```
sudo docker restart blog-postgres
```




