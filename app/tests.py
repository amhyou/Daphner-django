import os 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clicker.settings")

import django 
django.setup() 

from django.test import TestCase
from model_bakery import baker
from models import Profile,Conversation

class letsee(TestCase):

    def setUp(self):
        conv = baker.make('app.Conversation')
        prof = baker.make('app.Profile')
        print(prof.__dict__)
        print(conv.__dict__)

    def test(self):
        self.assertEqual(5,5)
