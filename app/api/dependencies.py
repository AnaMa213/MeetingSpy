# def get_db():
#     """
#     Dépendance pour obtenir une session SQLAlchemy.
#     Cette fonction garantit que la connexion à la base de données est ouverte
#     et fermée correctement pour chaque requête.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
