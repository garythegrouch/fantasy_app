from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class CustomUser(models.Model): 
    user = models.OneToOneField(User, on_delete = models.CASCADE)

class Player(models.Model): 
    name = models.CharField(max_length = 100)
    position = models.CharField(max_length = 100)
    current_form = models.DecimalField(max_digits = 5, decimal_places = 2)
    price = models.DecimalField(max_digits = 5, decimal_places = 2)
    statistics = models.JSONField(default = dict)

    def update_stats(self, **kwargs): 
            #function that updates the player's real life stats
            self.statistics.update(kwargs)
            self.save()

    def get_statistics(self, statistic_name): 
            #function to get a specific stat of the player
            return self.statistics.get(statistic_name)
    
    def __str__(self): 
            return self.name
    #add other features as needed

class Team(models.Model):
    name = models.CharField(max_length = 100)
    #each user can have multiple teams but each team has just one owner
    owner = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    players = models.ManyToManyField(Player, related_name = 'teams')

    FORMATION_CHOICES = [
        ('4-4-2', '4-4-2'),
        ('3-5-2', '3-5-2'),
        ('4-3-3', '4-3-3'),
        # Add more formations later. first value is what is stored in database, second is what is shown to user and in admin interface
    ]
    formation = models.CharField(max_length = 10, choices = FORMATION_CHOICES)
    weekly_pts = models.IntegerField()
    total_pts = models.IntegerField ()
    #figure out how to limit this jsut to H2H leagues
    pts_scored_against_weekly = models.IntegerField()
    pts_scored_against_season = models.IntegerField()

    def __str__(self): 
        return self.name
    #add other features as needed

class Match(models.Model): 
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateField()
    date_time = models.DateTimeField()
    final_score = models.CharField(max_length = 10)
    home_team_goals = models.IntegerField()
    away_team_goals = models.IntegerField()
    cards = models.IntegerField(max_length = 10)
    
    
class League(models.Model): 
    name = models.CharField(max_length = 100)
    commissioner = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    description = models.TextField()

    #store scoring rules as a JSON file 
    scoring_system = models.JSONField()
    roster_size = models.PositiveIntegerField()
    participants = models.ManyToManyField(Team)
    lineup_size = models.IntegerField()
    season_duration = models.IntegerField(default = 38)


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete = models.CASCADE)
    league = models.ForeignKey(League, on_delete = models.CASCADE)

    #for now ensure that each team and league pairing is unique
    class Meta: 
        unique_together = ('team', 'league')


class Position(models.Model):
    #need this model to represent positions of players
    name = models.CharField(max_length = 15, unique = True)
    abbreviation = models.CharField(max_length = 3, unique = True)

    # Position.objects.bulk_create([
    # Position(name='Goalkeeper', abbreviation='GK'),
    # Position(name='Defender', abbreviation='DEF'),
    # Position(name='Midfielder', abbreviation='MID'),
    # Position(name='Forward', abbreviation='FWD'),
    # ])


class RosterRequirements(models.Model): 
    league = models.ForeignKey(League, on_delete = models.CASCADE)
    position = models.ForeignKey(Position, on_delete = models.CASCADE)

    # RosterRequirement.objects.bulk_create([
    # RosterRequirement(league=my_league, position=Position.objects.get(abbreviation='GK'), required_number=2),
    # RosterRequirement(league=my_league, position=Position.objects.get(abbreviation='DEF'), required_number=5),
    # RosterRequirement(league=my_league, position=Position.objects.get(abbreviation='MID'), required_number=5),
    # RosterRequirement(league=my_league, position=Position.objects.get(abbreviation='FWD'), required_number=3),
    # ])

class Matchup(models.Model): 
    league = models.ForeignKey(League, on_delete = models.CASCADE)
    week_number = models.PositiveIntegerField()
    home_team = models.ForeignKey('Team', related_name = 'home_matchups', on_delete = models.CASCADE)
    away_team = models.ForeignKey('Team', related_name = 'away_matchups', on_delete = models.CASCADE)


class Transfer(models.Model): 
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    incoming_team = models.ForeignKey(Team, on_delete = models.CASCADE)
    outgoing_team = models.ForeignKey(Team, on_delete = models.CASCADE)
    transfer_date = models.DateField()
    gameweek = models.IntegerField()
    additional_points = models.IntegerField(default = 0)

    def __str__(self):
        return f"{self.player} transferred from {self.outgoing_team} to {self.incoming_team} on {self.transfer_date}"


class InGameScoring(models.Model): 
    name = models.CharField()
    rules = models.JSONField()

    def __str__(self): 
        return self.name
    
    #JSON scoring rulesheet would look like this... might need to make this more customizable
    # {
    # "goals": {
    #     "forward": 1,
    #     "midfielder": 2,
    #     "defender": 3
    # },
    # "assists": 1,
    # "clean_sheets": {
    #     "goalkeeper": 3,
    #     "defender": 2
    # },
    # "yellow_cards": -1,
    # "red_cards": -3
    # }

    # position = player.position  # Assume player position is stored in a 'position' attribute
    # if 'goals' in scoring_rules and position in scoring_rules['goals']:
    # points = scoring_rules['goals'][position]
    # else:
    # points = 0

class SystemNotif(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
    # def system_notifications(request):
    #     notifications = SystemNotif.objects.all()
    
    #     # Mark notifications as read if necessary
    #     # This logic depends on your specific requirements

    #     return render(request, 'system_notifications.html', {'notifications': notifications})

    

class UserNotif(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
    # def notifications(request):
    #   user = request.user
    #   notifications = UserNotif.objects.filter(user=user)
    #   unread_notifications = UserNotif.filter(is_read=False)
    
    #   # Mark unread notifications as read
    #   unread_notifications.update(is_read=True)
    #   return render(request, 'notifications.html', {'notifications': notifications})