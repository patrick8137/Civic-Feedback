import os
import sys
import django
import json

# Ensure project root is on sys.path so Django can import backend.settings
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
django.setup()
from feedback.models import Feedback

qs = Feedback.objects.all()
print('COUNT:', qs.count())
print('SAMPLE:')
arr = []
for f in qs[:10]:
    arr.append({'id': f.id, 'category': f.category, 'status': f.status, 'location': f.location, 'created_at': f.created_at.isoformat()})
print(json.dumps(arr, indent=2))
