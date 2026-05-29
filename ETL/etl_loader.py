import pandas as pd
import psycopg2
import os

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'watchlist'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )
    return conn


def extract():
    anime_df=pd.read_csv('anime_data.csv')
    genre_df=pd.read_csv('genre_data.csv')
    anime_genre_df=pd.read_csv('anime_genre_data.csv')

    print(f"Extracted {len(anime_df)} rows from Anime table")
    print(f"Extracted {len(genre_df)} rows from Genre table")
    print(f"Extracted {len(anime_genre_df)} rows from Anime_Genre table")

    return anime_df,genre_df,anime_genre_df


def transform(anime_df,genre_df,anime_genre_df):

    # 1. Datatype Conversions

    anime_df['id']=pd.to_numeric(anime_df['id'],errors='coerce')
    anime_df['rating']=pd.to_numeric(anime_df['rating'],errors='coerce')
    anime_df['total_episodes']=pd.to_numeric(anime_df['total_episodes'],errors='coerce')
    anime_df['avg_ep_length']=pd.to_numeric(anime_df['avg_ep_length'],errors='coerce')

    genre_df['genre_id']=pd.to_numeric(genre_df['genre_id'],errors='coerce')

    anime_genre_df['anime_id']=pd.to_numeric(anime_genre_df['anime_id'],errors='coerce')
    anime_genre_df['genre_id']=pd.to_numeric(anime_genre_df['genre_id'],errors='coerce')

    # 2. Stripping Whitespaces and Lower the Case

    anime_df['name']=anime_df['name'].str.strip().str.lower()
    anime_df['status']=anime_df['status'].str.strip().str.lower()

    genre_df['name']=genre_df['name'].str.strip().str.lower()


    # 3. Replacing NULL with None

    anime_df=anime_df.where(pd.notnull(anime_df),None)
    genre_df=genre_df.where(pd.notnull(genre_df),None)
    anime_genre_df=anime_genre_df.where(pd.notnull(anime_genre_df),None)

    # 4. Dropping Duplicates

    anime_df=anime_df.drop_duplicates()
    genre_df=genre_df.drop_duplicates()
    anime_genre_df=anime_genre_df.drop_duplicates()
    
    # 5. Range validation
    anime_df = anime_df[anime_df['total_episodes'] > 0]
    anime_df = anime_df.dropna(subset=['name'])

    print("Transform complete!")
    print(anime_df.dtypes)

    return anime_df,genre_df,anime_genre_df

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genre (
            genre_id INT PRIMARY KEY,
            name VARCHAR(100)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anime (
            id INT PRIMARY KEY,
            name VARCHAR(200),
            status VARCHAR(50),
            total_episodes INT,
            avg_ep_length INT,
            rating FLOAT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anime_genre (
            anime_id INT REFERENCES anime(id),
            genre_id INT REFERENCES genre(genre_id),
            PRIMARY KEY (anime_id, genre_id)
        );
    """)
    conn.commit()
    cursor.close()
    print("Tables created successfully!")

def load(anime_df, genre_df, anime_genre_df):
    conn = get_connection()
    create_tables(conn)
    cursor = conn.cursor()

    try:
        # Load genre first (no foreign key dependencies)
        for _, row in genre_df.iterrows():
            cursor.execute(
                "INSERT INTO genre (genre_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (int(row['genre_id']), row['name'])
            )

        # Load anime second
        for _, row in anime_df.iterrows():
            cursor.execute(
                "INSERT INTO anime (id, name, status, total_episodes, avg_ep_length, rating) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (int(row['id']), row['name'], row['status'], int(row['total_episodes']), int(row['avg_ep_length']), row['rating'])
            )

        # Load anime_genre last (depends on both)
        for _, row in anime_genre_df.iterrows():
            cursor.execute(
                "INSERT INTO anime_genre (anime_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (int(row['anime_id']), int(row['genre_id']))
            )

        conn.commit()
        print("Load complete! All rows inserted.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()


def run_etl():
    anime_df,genre_df,anime_genre_df=extract()
    anime_df,genre_df,anime_genre_df=transform(anime_df,genre_df,anime_genre_df)
    load(anime_df,genre_df,anime_genre_df)

run_etl()
