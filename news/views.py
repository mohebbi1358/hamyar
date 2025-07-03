# news/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import News, NewsImage, Category
from .forms import NewsForm, NewsImageFormSet




def news_list(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        news_items = News.objects.filter(category_id=selected_category_id).order_by('-created_at')
    else:
        news_items = News.objects.all().order_by('-created_at')

    paginator = Paginator(news_items, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category_id': int(selected_category_id) if selected_category_id else None
    })


from .forms import CommentForm
from .models import Comment


from django.db.models import Case, When, Value, IntegerField

def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)

    comments = news.comments.filter(is_approved=True).select_related('persona').annotate(
        persona_type_order=Case(
            When(persona__persona_type='legal', then=Value(0)),
            When(persona__persona_type='real', then=Value(1)),
            default=Value(2),
            output_field=IntegerField()
        )
    ).order_by('persona_type_order', '-created_at')

    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST, user=request.user)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.news = news
                comment.save()
                return redirect('news:news_detail', news_id=news.id)
        else:
            form = CommentForm(user=request.user)

    return render(request, 'news/news_detail.html', {
        'news': news,
        'comments': comments,
        'form': form,
    })






from django.utils import timezone
from django.contrib import messages

@login_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, user=request.user)
        formset = NewsImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            category = form.cleaned_data['category']
            daily_limit = category.daily_limit

            if daily_limit > 0:
                today = timezone.now().date()
                news_count_today = News.objects.filter(
                    author=request.user,
                    category=category,
                    created_at__date=today
                ).count()

                if news_count_today >= daily_limit:
                    messages.error(request, f'شما به سقف مجاز ارسال روزانه ({daily_limit} خبر) در دسته‌بندی "{category.name}" رسیده‌اید.')
                    return redirect('news:create_news')  # یا بازگشت به همان فرم

            # ادامه روند ذخیره:
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            formset.instance = news
            formset.save()
            return redirect('news:news_detail', news_id=news.id)
    else:
        form = NewsForm(user=request.user)
        formset = NewsImageFormSet()

    return render(request, 'news/create_news.html', {
        'form': form,
        'formset': formset
    })








def home(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        all_news = News.objects.filter(category_id=selected_category_id).order_by('-created_at')
    else:
        all_news = News.objects.all().order_by('-created_at')

    latest_news = News.objects.all().order_by('-created_at')[:5]  # همیشه آخرین ۵ خبر

    paginator = Paginator(all_news, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'latest_news': latest_news,
        'page_obj': page_obj,
        'all_news': all_news,
        'categories': categories,
        'selected_category_id': int(selected_category_id) if selected_category_id else None
    })





# news/views.py (اضافه کن)

from django.contrib import messages
from .forms import CategoryForm

@login_required
def manage_categories(request):
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news:manage_categories')
    else:
        form = CategoryForm()

    return render(request, 'news/manage_categories.html', {
        'categories': categories,
        'form': form
    })


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'دسته‌بندی حذف شد.')
    return redirect('news:manage_categories')


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی ویرایش شد.')
            return redirect('news:manage_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'news/edit_category.html', {
        'form': form,
        'category': category
    })







from django.http import JsonResponse
from news.models import Category




from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

def check_daily_limit(request):
    category_id = request.GET.get("category_id")

    if not category_id:
        return JsonResponse({
            "ok": False,
            "message": "هیچ شناسه‌ای ارسال نشده."
        })

    try:
        category_id = int(category_id)
    except ValueError:
        return JsonResponse({
            "ok": False,
            "message": "شناسه دسته‌بندی معتبر نیست."
        })

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({
            "ok": False,
            "message": "دسته‌بندی پیدا نشد."
        })

    # اگر سقف روزانه صفر بود یعنی محدودیتی ندارد
    if category.daily_limit == 0:
        return JsonResponse({
            "ok": True,
            "message": f"دسته‌بندی {category.name} پیدا شد و محدودیتی برای ارسال خبر ندارد."
        })

    today = now().date()
    count_today = News.objects.filter(
        category=category,
        created_at__date=today
    ).count()

    if count_today >= category.daily_limit:
        return JsonResponse({
            "ok": False,
            "message": f"سقف مجاز ارسال خبر در دسته‌بندی '{category.name}' برای امروز پر شده است."
        })

    return JsonResponse({
        "ok": True,
        "message": f"دسته‌بندی {category.name} پیدا شد و می‌توانید خبر ارسال کنید."
    })





