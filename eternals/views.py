from .models import Eternals
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Case, When, IntegerField

from .models import Eternals, CondolenceMessage, Ceremony
from .forms import EternalsForm, CeremonyForm, CondolenceMessageForm
from accounts.models import Persona


class EternalsListView(ListView):
    model = Eternals
    template_name = 'eternals/eternals_list.html'
    context_object_name = 'eternals'


from django.views.generic.detail import DetailView
from django.db.models import Case, When, IntegerField
from .models import Eternals, CondolenceMessage



from django.views.generic import DetailView
from django.db.models import Prefetch
from martyrs.models import Martyr
from donation.models import Donation
from eternals.models import CondolenceMessage
from .models import Eternals


from donation.forms import DonationForm

from django.db.models import Sum

class EternalsDetailView(DetailView):
    model = Eternals
    template_name = "eternals/eternals_detail.html"
    context_object_name = "eternal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eternal = self.get_object()

        condolences = CondolenceMessage.objects.filter(
            eternal=eternal
        ).select_related('persona').order_by('-created_at')[:5]

        donations_qs = Donation.objects.filter(
            eternal=eternal,
            status='SUCCESS'
        ).select_related('user', 'wallet_transaction').order_by('-created_at')

        donations = donations_qs[:5]

        donations_total = donations_qs.aggregate(total=Sum('amount'))['total'] or 0

        context['condolences'] = condolences
        context['donations'] = donations
        context['donations_total'] = donations_total
        context['donation_form'] = DonationForm()
        return context



#class EternalsDetailView(DetailView):
#    model = Eternals
#    context_object_name = "eternal"

#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        eternal = self.object  # self.get_object() نیز می‌توانست باشد

        # اول حقوقی‌ها، بعد حقیقی‌ها، سپس بر اساس تاریخ نزولی
        #condolences = CondolenceMessage.objects.filter(eternal=eternal).select_related('persona').annotate(
         #   persona_sort_order=Case(
          #      When(persona__persona_type='legal', then=0),
           #     When(persona__persona_type='real', then=1),
            #    default=2,
             #   output_field=IntegerField()
            #)
        #).order_by('persona_sort_order', '-created_at')

        #context['condolences'] = condolences
        #return context



class EternalsCreateView(CreateView):
    model = Eternals
    form_class = EternalsForm
    template_name = 'eternals/eternals_form.html'
    success_url = reverse_lazy('eternals:list')


# views.py

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from .models import Ceremony, Eternals
from .forms import CeremonyForm

class CeremonyCreateView(CreateView):
    model = Ceremony
    form_class = CeremonyForm
    template_name = 'eternals/ceremony_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Eternal رو ذخیره می‌کنیم تا در متدهای دیگه استفاده کنیم
        self.eternal = get_object_or_404(Eternal, id=self.kwargs['eternal_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eternal'] = self.eternal
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.eternal = self.eternal
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('eternals:detail', kwargs={'pk': self.eternal.id})


@login_required
def add_ceremony(request, eternal_id):
    eternal = get_object_or_404(Eternals, id=eternal_id)

    if request.method == 'POST':
        form = CeremonyForm(request.POST)
        if form.is_valid():
            ceremony = form.save(commit=False)
            ceremony.eternal = eternal
            ceremony.user = request.user
            ceremony.save()
            messages.success(request, "مراسم با موفقیت ثبت شد.")
            return redirect('eternals:detail', pk=eternal.id)
    else:
        form = CeremonyForm()

    return render(request, 'eternals/ceremony_form.html', {
        'form': form,
        'eternal': eternal
    })




from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from .models import CondolenceMessage, Eternals, Persona
from .forms import CondolenceMessageForm

class CondolenceMessageCreateView(CreateView):
    model = CondolenceMessage
    form_class = CondolenceMessageForm
    template_name = 'eternals/condolence_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.eternal = get_object_or_404(Eternals, id=kwargs['eternal_id'])
        self.persona = request.user.personas.filter(is_default=True).first()
        if not self.persona:
            # یا redirect کن به صفحه انتخاب persona
            raise Http404("هیچ شخصیتی برای این کاربر ثبت نشده است.")
        return super().dispatch(request, *args, **kwargs)
    


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eternal'] = self.eternal
        context['persona'] = self.persona
        return context

    def form_valid(self, form):
        form.instance.persona = self.persona
        form.instance.eternal = self.eternal
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('eternals:detail', kwargs={'pk': self.eternal.id})









def eternal_ceremony_list(request, eternal_id):
    eternal = get_object_or_404(Eternals, id=eternal_id)
    ceremonies = eternal.ceremonies.all()

    return render(request, 'eternals/eternal_ceremony_list.html', {
        'eternal': eternal,
        'ceremonies': ceremonies
    })



from django.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.views.generic.edit import UpdateView, DeleteView

class CeremonyUpdateView(UpdateView):
    model = Ceremony
    form_class = CeremonyForm
    template_name = 'eternals/ceremony_form.html'
    success_url = reverse_lazy('eternals:list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.user or (now() - obj.created_at).total_seconds() > 120:
            return HttpResponseForbidden("اجازه ویرایش ندارید.")
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        return reverse_lazy('eternals:detail', kwargs={'pk': self.object.eternal.id})


class CeremonyDeleteView(DeleteView):
    model = Ceremony
    template_name = 'eternals/ceremony_confirm_delete.html'
    success_url = reverse_lazy('eternals:list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.user or (now() - obj.created_at).total_seconds() > 120:
            return HttpResponseForbidden("اجازه حذف ندارید.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('eternals:detail', kwargs={'pk': self.object.eternal.id})






from django.views.generic.detail import DetailView
from .models import CondolenceMessage

class CondolenceDetailView(DetailView):
    model = CondolenceMessage
    template_name = "eternals/condolence_detail.html"
    context_object_name = "message"



from django.views.generic import ListView
from .models import CondolenceMessage, Eternals

class CondolenceListView(ListView):
    model = CondolenceMessage
    template_name = 'eternals/condolence_list.html'
    context_object_name = 'condolences'
    paginate_by = 10  # تعداد پیام در هر صفحه

    def get_queryset(self):
        eternal_id = self.kwargs['eternal_id']
        return CondolenceMessage.objects.filter(eternal_id=eternal_id).select_related('persona').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eternal'] = Eternals.objects.get(id=self.kwargs['eternal_id'])
        return context



from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from donation.forms import DonationForm
from donation.models import Donation

@login_required
def donate_to_eternal(request, pk):
    eternal = get_object_or_404(Eternals, pk=pk)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.eternal = eternal
            donation.user = request.user
            donation.status = 'PENDING'  # یا هر چیزی که مناسبه
            donation.save()
            messages.success(request, "صدقه با موفقیت ثبت شد.")
            return redirect('eternals:detail', pk=pk)
        else:
            messages.error(request, "اطلاعات وارد شده معتبر نیست.")
    else:
        form = DonationForm()
    return render(request, 'eternals/donate_form.html', {'form': form, 'eternal': eternal})


# eternals/views.py
from django.shortcuts import render, get_object_or_404
from donation.models import Donation

from django.db.models import Sum

def eternal_donations_list(request, pk):
    eternal = get_object_or_404(Eternals, pk=pk)
    donations = Donation.objects.filter(eternal=eternal, status='SUCCESS').order_by('-created_at')

    donations_total = donations.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'eternals/eternal_donations_list.html', {
        'eternal': eternal,
        'donations': donations,
        'donations_total': donations_total,
    })


