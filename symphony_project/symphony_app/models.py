from django.db import models

class EntitiesMaster(models.Model):
    artist_name = models.CharField(max_length=255)
    artist_role = models.CharField(max_length=255)
    program_name = models.CharField(max_length=255)
    composer = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    tickets_info = models.TextField()
    url = models.URLField(null=True)

    def __str__(self):
        return self.artist_name  # Or any other field you want to represent the model in admin
