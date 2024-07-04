To run in dev mode:
`export SECRET_KEY="verysecretkey"`
`export DATABASE_URL="postgresql://yourname:yourpassword@localhost:5432/dbname"`
`uvicorn  backend.main:app`
To edit database
`psql -U nickname -d db -h localhost`
