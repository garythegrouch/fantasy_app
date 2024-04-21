from django.test import TestCase
from .models import * 
from .views import *

# Create your tests here.
class PlayerModelTest(TestCase):
    def setUp(self): 
        self.player = Player.objects.create(name = 'Kai Havertz', position = 'midfielder', current_form = 4.2, price = 8.4, EPL_team = 'Arsenal')
    
    def test_PlayerModelCreate(self): 
        self.assertEqual(self.player.name, 'Kai Havertz')
        self.assertEqual(self.player.position, 'Midfielder')
        self.assertEqual(self.player.EPL_team, 'Arsenal')

        
