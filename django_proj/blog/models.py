from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="blog_posts")


    def __str__(self):
        return self.title


    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    # def get_success_url(self):
    #     return reverse("post_detail", kwargs={"pk": self.pk})
    
    
    