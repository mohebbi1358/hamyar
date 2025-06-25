from django.shortcuts import render
from django.core.paginator import Paginator
from news.models import News, Category
from eternals.models import Eternals

def home(request):
    # بخش 1: آخرین ۵ خبر (برای بخش آخرین اخبار)
    latest_news = News.objects.order_by('-created_at')[:5]

    # بخش 2: اخبار دسته‌بندی شده و صفحه‌بندی شده
    category_id = request.GET.get('category')
    categories = Category.objects.all()

    if category_id:
        news_list = News.objects.filter(category_id=category_id).order_by('-created_at')
        selected_category_id = int(category_id)
    else:
        news_list = News.objects.order_by('-created_at')
        selected_category_id = None

    paginator = Paginator(news_list, 5)  # 10 خبر در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # بخش 3: ۵ جاودانه آخر بر اساس تاریخ فوت
    latest_eternals = Eternals.objects.order_by('-death_date')[:5]

    return render(request, 'home.html', {
        'latest_news': latest_news,
        'categories': categories,
        'selected_category_id': selected_category_id,
        'page_obj': page_obj,
        'latest_eternals': latest_eternals,
    })
