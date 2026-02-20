from sqlmodel import SQLModel, create_engine, Session

# 1. Definiujemy nazwę pliku bazy danych.
# "sqlite:///" oznacza, że używamy bazy SQLite (plik na dysku, nie serwer).
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 2. Tworzymy silnik (engine).
# To jest "główny kabel" łączący Pythona z plikiem bazy.
# echo=True sprawi, że w konsoli będziesz widział, co robi baza (super do nauki).
engine = create_engine(sqlite_url, echo=True)

# 3. Funkcja tworząca tabele.
# Uruchomimy ją raz przy starcie aplikacji, żeby stworzyć puste tabele.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Funkcja dostarczająca sesję (Dependency).
# To jest jak "wydawanie przepustki" do bazy dla każdego zapytania.
def get_session():
    with Session(engine) as session:
        yield session
