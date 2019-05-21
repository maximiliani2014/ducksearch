from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Storing password as plaintext, terrible security, fix later
    def __str__(self):
        return str(self.id)

class Interest(models.Model):
    name = models.CharField(max_length=100)
    strength = models.DecimalField(max_digits=2, decimal_places=1)
    associated_user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return str(self.id)
