from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import random

from .models import Martyr, MartyrMemory
from .serializers import MartyrSerializer
from .forms import MartyrMemoryForm, MartyrForm


# API ViewSet برای شهدا
class MartyrViewSet(viewsets.ModelViewSet):
    queryset = Martyr.objects.all()
    serializer_class = MartyrSerializer

    @action(detail=False, methods=['get'])
    def random(self, request):
        count = Martyr.objects.count()
        if count == 0:
            return Response({"detail": "No martyrs found."}, status=404)
        random_index = random.randint(0, count - 1)
        martyr = Martyr.objects.all()[random_index]
        serializer = self.get_serializer(martyr)
        return Response(serializer.data)


# صفحه ایجاد شهید (فقط برای مدیران)
@login_required
# @user_passes_test(lambda u: u.is_superuser or u.is_staff)
def create_martyr_view(request):
    if request.method == 'POST':
        form = MartyrForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return redirect('martyr_list')  # فرض می‌کنیم URL نام martyr_list است
            return redirect('martyrs:martyr_list')
    else:
        form = MartyrForm()
    
    print(request.POST.get('birth_date'))
    print(request.POST.get('martyr_date'))


    return render(request, 'martyrs/create_martyr.html', {'form': form})


# لیست شهدا
from django.db.models import Q  # بالای فایل اضافه شود




from django.db.models import Q
from django.shortcuts import render
from .models import Martyr  # اطمینان از ایمپورت مدل

def martyr_list(request):
    query = request.GET.get('q', '').strip()
    martyrs = Martyr.objects.all()

    if query:
        keywords = query.split()
        q_object = Q()
        for word in keywords:
            q_object &= (
                Q(first_name__icontains=word) |
                Q(last_name__icontains=word)
            )
        martyrs = martyrs.filter(q_object)

    return render(request, 'martyrs/martyr_list.html', {
        'martyrs': martyrs,
        'query': query,
    })







# نمایش جزئیات شهید + نمایش دل‌نوشته‌ها + فرم ثبت دل‌نوشته
from .forms import MartyrMemoryForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import Martyr, MartyrMemory
from .forms import MartyrMemoryForm

def martyr_detail(request, martyr_id):  # ✅ اینجا اسم باید با urls.py بخونه
    martyr = get_object_or_404(Martyr, id=martyr_id)
    memories = martyr.memories.select_related('user', 'persona').all()

    if request.method == 'POST':
        form = MartyrMemoryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.user = request.user
            memory.martyr = martyr
            memory.save()
            return redirect('martyrs:martyr_detail', martyr_id=martyr.id)  # ✅ با اسم پارامتر یکی باشه
    else:
        form = MartyrMemoryForm(user=request.user)

    return render(request, 'martyrs/martyr_detail.html', {
        'martyr': martyr,
        'form': form,
        'memories': memories,
    })




from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Martyr
from .forms import MartyrForm

class MartyrUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Martyr
    form_class = MartyrForm
    template_name = 'martyrs/martyr_edit.html'
    success_url = reverse_lazy('martyrs:martyr_list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        # چون birth_date و martyr_date در Meta نیستند، باید دستی ست شوند
        self.object = form.save(commit=False)
        self.object.birth_date = form.cleaned_data['birth_date']
        self.object.martyr_date = form.cleaned_data['martyr_date']
        self.object.save()
        return super().form_valid(form)
