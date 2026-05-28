from django.contrib import admin
from .models import QuizQuestion, QuizAnswer, QuizRecommendation


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 2


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('step_number', 'title')
    inlines = [QuizAnswerInline]


@admin.register(QuizRecommendation)
class QuizRecommendationAdmin(admin.ModelAdmin):
    list_display = ('product', 'gender_value', 'vibe_value', 'occasion_value', 'season_value', 'strength_value', 'score_weight')
    list_filter = ('gender_value', 'vibe_value', 'occasion_value', 'season_value')
    search_fields = ('product__name',)
