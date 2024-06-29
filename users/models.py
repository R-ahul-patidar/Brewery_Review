from django.db import models

class Review(models.Model):
    brewery_id = models.CharField(max_length=100)
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} - {self.brewery_id}"
