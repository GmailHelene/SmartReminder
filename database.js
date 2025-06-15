const database_url = os.getenv('DATABASE_URL')
if database_url and 'postgres.railway.internal' in database_url:
    database_url = database_url.replace(
        'postgres.railway.internal', 
        os.getenv('PGHOST')
    )
