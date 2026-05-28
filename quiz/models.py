from django.db import models
from shop.models import Product


class QuizQuestion(models.Model):
    step_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.title}"


class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, blank=True, default='')
    description = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=50, help_text='Internal value for matching')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.title} → {self.text}"


class QuizRecommendation(models.Model):
    """Maps answer combinations to products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quiz_recommendations')
    gender_value = models.CharField(max_length=50, blank=True, help_text='Matches Step 1')
    vibe_value = models.CharField(max_length=50, blank=True, help_text='Matches Step 2')
    occasion_value = models.CharField(max_length=50, blank=True, help_text='Matches Step 3')
    season_value = models.CharField(max_length=50, blank=True, help_text='Matches Step 4')
    strength_value = models.CharField(max_length=50, blank=True, help_text='Matches Step 5')
    score_weight = models.PositiveIntegerField(default=1, help_text='Higher = stronger match')

    def __str__(self):
        return f"{self.product.name} → {self.vibe_value}/{self.occasion_value}"
