from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WatchItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_items')
    company_name = models.CharField(max_length=100, db_index=True)
    stock_code = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company_name')  # 유저별 중복 방지
        ordering = ['-id']

    def __str__(self):
        return f'{self.user.username} - {self.company_name}'