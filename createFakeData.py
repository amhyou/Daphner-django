import os 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clicker.settings")

import django 
django.setup() 

from faker import factory,Faker 
from app.models import * 
from model_bakery.recipe import Recipe,foreign_key 

fake = Faker() 

for k in range(10):
    prof=Recipe(Profile,
                email=fake.email(),
                name=fake.name()
                )
  
    click=Recipe(Click, 
                owner=foreign_key(prof),
                msg=fake.sentence(nb_words=6,variable_nb_words=True),
                origin=foreign_key(prof),
                )
    
    like = Recipe(Like, 
                click=foreign_key(click), 
                sender=foreign_key(prof), 
                ) 
    prof.make()
    click.make()
    like.make()