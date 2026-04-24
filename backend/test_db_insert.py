import os
import django
import random
from datetime import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_city.settings')
django.setup()

from api.models import Capteur, Mesure

def test_insert():
    capteur = Capteur.objects.filter(statut='ACTIF').first()
    if not capteur:
        print("No active capteur found")
        return
    
    print(f"Testing with capteur: {capteur.uuid}")
    try:
        m = Mesure.objects.create(
            capteur=capteur,
            timestamp=datetime.now(),
            valeurs={'test': 1},
            indice_pollution=Decimal('50.0'),
            qualite_air='BON'
        )
        print(f"Successfully created mesure: {m.id}")
    except Exception as e:
        print(f"Failed to create mesure: {e}")

if __name__ == '__main__':
    test_insert()
