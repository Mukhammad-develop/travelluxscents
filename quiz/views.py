from django.shortcuts import render
from django.db.models import Count, Q
from .models import QuizQuestion, QuizAnswer, QuizRecommendation
from shop.models import Product


def quiz_start(request):
    """HTMX: Return quiz step 1."""
    question = QuizQuestion.objects.filter(step_number=1).first()
    if not question:
        return render(request, 'partials/quiz_empty.html')
    total_steps = QuizQuestion.objects.count()
    context = {
        'question': question,
        'answers': question.answers.all(),
        'step': 1,
        'total_steps': total_steps,
    }
    return render(request, 'partials/quiz_step.html', context)


def quiz_step(request, step):
    """HTMX: Return quiz step N."""
    total_steps = QuizQuestion.objects.count()

    if step > total_steps:
        # Process results
        return quiz_results(request)

    question = QuizQuestion.objects.filter(step_number=step).first()
    if not question:
        return quiz_results(request)

    context = {
        'question': question,
        'answers': question.answers.all(),
        'step': step,
        'total_steps': total_steps,
        # Carry forward previous answers
        'previous_answers': {k: v for k, v in request.GET.items() if k.startswith('step_')},
    }
    return render(request, 'partials/quiz_step.html', context)


def quiz_results(request):
    """Calculate and return quiz results."""
    answers = {}
    for key, value in request.GET.items():
        if key.startswith('step_'):
            answers[key] = value

    # Score products based on answer matching
    recs = QuizRecommendation.objects.select_related('product')

    filters = Q()
    if answers.get('step_1'):
        filters |= Q(gender_value=answers['step_1'])
    if answers.get('step_2'):
        filters |= Q(vibe_value=answers['step_2'])
    if answers.get('step_3'):
        filters |= Q(occasion_value=answers['step_3'])
    if answers.get('step_4'):
        filters |= Q(season_value=answers['step_4'])
    if answers.get('step_5'):
        filters |= Q(strength_value=answers['step_5'])

    if filters:
        matching = recs.filter(filters)
        # Get products ordered by match count
        product_ids = (
            matching.values('product_id')
            .annotate(match_score=Count('id'))
            .order_by('-match_score')[:6]
        )
        products = Product.objects.filter(
            id__in=[p['product_id'] for p in product_ids]
        ).prefetch_related('variants', 'notes', 'badges')
    else:
        products = Product.objects.filter(featured=True)[:6]

    return render(request, 'partials/quiz_results.html', {'products': products})
