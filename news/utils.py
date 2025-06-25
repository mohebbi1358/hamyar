# news/utils.py
from .models import News

def get_filtered_news(request):
    selected_category_id = request.GET.get('category')
    if selected_category_id:
        news_items = News.objects.filter(category_id=selected_category_id).order_by('-created_at')
    else:
        news_items = News.objects.all().order_by('-created_at')
    return news_items, selected_category_id
