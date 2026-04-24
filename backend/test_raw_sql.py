import MySQLdb
import os
from datetime import datetime

try:
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="smart_city_db")
    cursor = db.cursor()
    
    # Try to insert one row
    sql = "INSERT INTO mesure (capteur_uuid, timestamp, valeurs, indice_pollution, qualite_air) VALUES ('0cf80838-d8e9-11f0-8530-d49390394a7d', %s, %s, %s, %s)"
    params = (datetime.now(), '{"test": 1}', 50.0, 'BON')
    
    cursor.execute(sql, params)
    db.commit()
    print("Raw SQL insertion successful!")
    db.close()
except Exception as e:
    print(f"Raw SQL insertion failed: {e}")
