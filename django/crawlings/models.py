# crawlings/models.py

from django.db import models

# Create your models here.
class Comment(models.Model):
    company_name = models.CharField(max_length=100, db_index=True)
    stock_code = models.CharField(max_length=32, blank=True)  # 현재 크롤러가 코드 미반환이라 비워둘 수 있게
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"[{self.company_name}] {self.text[:30]}"