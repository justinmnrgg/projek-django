from django.shortcuts import render, redirect
from django.views.generic import (CreateView, UpdateView, DeleteView,
                                  FormView, TemplateView, DetailView,
                                  ListView, View)
from .models import (Administrator, Akun, Berita,
                     Group, User)
from .form import (AdministratorForm, UserForm, UserLoginForm,
                   PengunjungForm, AsuransiForm, RumahSakitForm)
from rumah_sakit.models import RumahSakit
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.urlresolvers import reverse_lazy
from extra_views import CreateWithInlinesView, InlineFormSet
from asuransi.models import (Asuransi, HubunganRumahSakitAsuransi)
from rumah_sakit.models import RumahSakit, Penyakit
from pengunjung.models import (Pengunjung, Review)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class Page404View(TemplateView):
    template_name = '404.html'

class Page403View(TemplateView):
    template_name = '403.html'

    # def get(self, request, *args, **kwargs):
    #     self.get_context_data(**kwargs)
    #     return super(Page404View, self).get(request=request, *args, **kwargs)



class HomeView(View):
    def get(self, request):
        rumah_sakit = RumahSakit.objects.filter(status_validasi='validated')

        return render(request, 'home/index.html', {'rumah_sakits':rumah_sakit})

class HomeView2(View):
    def get(self, request):
        rumah_sakit = RumahSakit.objects.filter(status_validasi='validated')

        return render(request, 'home/index2.html', {'rumah_sakits':rumah_sakit})


class BeritaListView(ListView):
    context_object_name = 'beritas'
    model = Berita
    template_name = 'berita/berita_list.html'

class BeritaCreateView(LoginRequiredMixin, CreateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = 'berita/berita_form.html'
    fields = ('judul','isi','foto_berita')
    model = Berita

    def get(self, request, *args, **kwargs):
        if(request.session['role']!='administrator'):
            return redirect('not_found')
        return super(BeritaCreateView, self).get(request=request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.administrator = Administrator.objects.get(pk=int(self.request.session['role_pk']))
        return super(BeritaCreateView, self).form_valid(form)

class BeritaDetailView(DetailView):
    model = Berita
    template_name = 'berita/berita_detail.html'
    context_object_name = 'berita_detail'

class BeritaUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = 'berita/berita_form.html'
    fields = ('judul', 'isi', 'foto_berita')
    model = Berita

    def get(self, request, *args, **kwargs):
        if(request.session['role']!='administrator'):
            return redirect('not_found')
        return super(BeritaUpdateView, self).get(request=request, *args, **kwargs)

class BeritaDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'utama:login'
    redirect_field_name = ''
    model = Berita
    success_url = reverse_lazy('utama:list')
    context_object_name = 'berita'
    template_name = 'berita/berita_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        if (request.session['role'] != 'administrator'):
            return redirect('not_found')
        return super(BeritaDeleteView, self).get(request=request, *args, **kwargs)

class AdministratorDetailView(DetailView):
    model = Administrator
    template_name = 'administrator/administrator_detail.html'
    context_object_name = 'administrator_detail'

    def get(self, request, *args, **kwargs):
        if(request.session['role']!='administrator'):
            return redirect('not_found')
        return super(AdministratorDetailView, self).get(request=request, *args, **kwargs)

class AdministratorUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = 'administrator/administrator_update.html'
    fields = ('nama', 'alamat', 'jenis_kelamin', 'nomor_telepon', 'foto_profil')
    model = Administrator

    def get(self, request, *args, **kwargs):
        if(request.session['role']!='administrator'):
            return redirect('not_found')
        return super(AdministratorUpdateView, self).get(request=request, *args, **kwargs)

class PencarianListView(ListView):
    template_name = 'pencarian/pencarian_list.html'
    context_object_name = 'data_pencarian'
    model = RumahSakit

    def get(self, request, *args, **kwargs):
        pilihan_cari = request.GET['search_select']
        data = request.GET['data']

        if(pilihan_cari == 'asuransi'):
            self.queryset = RumahSakit.objects.filter(hubungan_rumah_sakit_asuransis__asuransi__nama__contains=data).distinct()
        elif (pilihan_cari == 'rumah_sakit'):
            self.queryset = RumahSakit.objects.filter(nama__contains=data).distinct()
        elif (pilihan_cari == 'penyakit'):
            self.queryset = RumahSakit.objects.filter(dokters__spesialis__penyakits=Penyakit.objects.filter(nama__contains=data).first()).distinct()
        elif (pilihan_cari == 'lokasi'):
            self.queryset = RumahSakit.objects.filter(alamat__contains=data).distinct()

        return super(PencarianListView, self).get(request=request, *args, **kwargs)

#logout
class Logout(LoginRequiredMixin, View):
    login_url = 'utama:login'
    redirect_field_name = ''

    def get(self, request):
        logout(request)
        try:
            del request.session['username']
            del request.session['pk']
            del request.session['role']
            del request.session['role_pk']
            del request.session['image_url']
            del request.session['status']
        except KeyError:
            pass
        return redirect('utama:home')

#login

def login_view(request):
    if 'username' in request.session:
        return redirect('not_found')

    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if Akun.objects.filter(user=user).first() is not None:
            akun = Akun.objects.get(user=user)
            role = akun.role

            if role == 'asuransi':
                data_akun = Asuransi.objects.get(akun=akun)
                request.session['status'] = data_akun.status_validasi
            elif role == 'rumah_sakit':
                data_akun = RumahSakit.objects.get(akun=akun)
                request.session['status'] = data_akun.status_validasi
            elif role == 'administrator':
                data_akun = Administrator.objects.get(akun=akun)
                request.session['status'] = 'validated'
            else:
                data_akun = Pengunjung.objects.get(akun=akun)
                request.session['status'] = 'validated'

            request.session['username'] = username
            request.session['pk'] = akun.pk
            request.session['role'] = role
            request.session['role_pk'] = data_akun.pk
            request.session['image_url'] = data_akun.foto_profil.url

            login(request, user)
            return redirect('utama:home')

        else:
            return redirect('utama:login')

    return render(request, "login/login.html", {"form": form, "title": title})

def pengunjung_registrasi(request):
    if 'username' in request.session:
        return redirect('not_found')

    user_form = UserForm(data=request.POST or None)
    pengunjung_form = PengunjungForm(data=request.POST or None)
    if user_form.is_valid() and pengunjung_form.is_valid():
        user = user_form.save()
        user.save()
        user.set_password(user.password)
        user.save()
        akun = Akun(user=user, role='pengunjung')
        akun.save()
        pengunjung = pengunjung_form.save(commit=False)
        pengunjung.akun = akun
        if 'foto_profil' in request.FILES:
            pengunjung.foto_profil = request.FILES['foto_profil']

        pengunjung.save()

    else:
        print(user_form.errors, pengunjung_form.errors)

    return render(request, 'registrasi/pengunjung_registrasi.html', {'user_form':user_form, 'pengunjung_form' : pengunjung_form})

def asuransi_registrasi(request):
    if 'username' in request.session:
        return redirect('not_found')

    user_form = UserForm(data=request.POST or None)
    asuransi_form = AsuransiForm(data=request.POST or None)
    if user_form.is_valid() and asuransi_form.is_valid():
        user = user_form.save()
        user.save()
        user.set_password(user.password)
        user.save()
        akun = Akun(user=user, role='asuransi')
        akun.save()
        asuransi = asuransi_form.save(commit=False)
        asuransi.akun = akun
        if 'foto_profil' in request.FILES:
            asuransi.foto_profil = request.FILES['foto_profil']

        if 'dokumen' in request.FILES:
            asuransi.dokumen = request.FILES['dokumen']

        asuransi.save()

    else:
        print(user_form.errors, asuransi_form.errors)

    return render(request, 'registrasi/asuransi_registrasi.html', {'user_form':user_form, 'asuransi_form' : asuransi_form})

def rumah_sakit_registrasi(request):
    if 'username' in request.session:
        return redirect('not_found')

    user_form = UserForm(data=request.POST or None)
    rumah_sakit_form = RumahSakitForm(data=request.POST or None)
    if user_form.is_valid() and rumah_sakit_form.is_valid():
        user = user_form.save()
        user.save()
        user.set_password(user.password)
        user.save()
        akun = Akun(user=user, role='rumah_sakit')
        akun.save()
        rumah_sakit= rumah_sakit_form.save(commit=False)
        rumah_sakit.akun = akun
        if 'foto_profil' in request.FILES:
            rumah_sakit.foto_profil = request.FILES['foto_profil']

        if 'dokumen' in request.FILES:
            rumah_sakit.dokumen = request.FILES['dokumen']

        rumah_sakit.save()

    else:
        print(user_form.errors, rumah_sakit_form.errors)

    return render(request, 'registrasi/rumah_sakit_registrasi.html', {'user_form': user_form, 'rumah_sakit_form': rumah_sakit_form})

class HubunganRumahSakitAsuransiListView(LoginRequiredMixin, View):
    login_url = 'utama:login'
    redirect_field_name = ''
    def get(self, request, *args, **kwargs):
        hubungan_request = HubunganRumahSakitAsuransi.objects.filter(status_validasi_administrator='request')
        hubungan_validated = HubunganRumahSakitAsuransi.objects.filter(status_validasi_administrator='validated')
        hubungan_rejected = HubunganRumahSakitAsuransi.objects.filter(status_validasi_administrator='rejected')
        return render(request, 'administrator/hubungan_list.html', context={'hubungan_request':hubungan_request,
                                                                                    'hubungan_validated':hubungan_validated,
                                                                                    'hubungan_rejected':hubungan_rejected})

class PermintaanHubunganAsuransiListView(LoginRequiredMixin, ListView):
    login_url = 'utama:login'
    redirect_field_name = ''
    context_object_name = 'hubungan_rumah_sakit_asuransis'
    model = HubunganRumahSakitAsuransi
    template_name = ('administrator/hubungan_request_list.html')

    def get(self, request, *args, **kwargs):
        if (not (request.session['status'] == 'validated')):
            return redirect('access_denied')
        if (request.session['role'] != 'administrator'):
            return redirect('not_found')
        self.queryset = HubunganRumahSakitAsuransi.objects.filter(status_validasi_administrator='request')
        return super(PermintaanHubunganAsuransiListView, self).get(request, *args, **kwargs)

class ValidatedHubunganAsuransiView(LoginRequiredMixin, TemplateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = ('administrator/hubungan_request_list.html')
    def get(self, request, *args, **kwargs):
        if(request.GET['submit'] is not None):
            hubungan_rumah_sakit_asuransi = HubunganRumahSakitAsuransi.objects.get(pk = int(request.GET['submit']))
            hubungan_rumah_sakit_asuransi.status_validasi_administrator = 'validated'
            hubungan_rumah_sakit_asuransi.save()
            redirect('utama:hubungan_request')
        return super(ValidatedHubunganAsuransiView, self).get(request, *args, **kwargs)

class RejectedHubunganAsuransiView(LoginRequiredMixin, TemplateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = ('administrator/hubungan_request_list.html')
    def get(self, request, *args, **kwargs):
        if(request.GET['submit'] is not None):
            hubungan_rumah_sakit_asuransi = HubunganRumahSakitAsuransi.objects.get(pk = int(request.GET['submit']))
            hubungan_rumah_sakit_asuransi.status_validasi_administrator = 'rejected'
            hubungan_rumah_sakit_asuransi.save()
            redirect('utama:hubungan_request')
        return super(RejectedHubunganAsuransiView, self).get(request, *args, **kwargs)

class ReviewAllListView(LoginRequiredMixin, View):
    login_url = 'utama:login'
    redirect_field_name = ''
    def get(self, request, *args, **kwargs):
        review_request = Review.objects.filter(status_validasi='request')
        review_validated = Review.objects.filter(status_validasi='validated')
        review_rejected = Review.objects.filter(status_validasi='rejected')
        review_rejected_by_system = Review.objects.filter(status_validasi='rejected_by_System')
        return render(request, 'administrator/review_list.html', context={'review_request':review_request,
                                                                                    'review_validated':review_validated,
                                                                                    'review_rejected':review_rejected,
                                                                                    'review_rejected_by_system':review_rejected_by_system})

class PermintaanReviewListView(LoginRequiredMixin, ListView):
    login_url = 'utama:login'
    redirect_field_name = ''
    context_object_name = 'reviews'
    model = Review
    template_name = ('administrator/review_request_list.html')

    def get(self, request, *args, **kwargs):
        if (not (request.session['status'] == 'validated')):
            return redirect('access_denied')
        if (request.session['role'] != 'administrator'):
            return redirect('not_found')
        self.queryset = Review.objects.filter(status_validasi='request')
        return super(PermintaanReviewListView, self).get(request, *args, **kwargs)

class ValidatedReviewView(LoginRequiredMixin, TemplateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = ('administrator/review_request_list.html')
    def get(self, request, *args, **kwargs):
        if(request.GET['submit'] is not None):
            review = Review.objects.get(pk = int(request.GET['submit']))
            review.status_validasi = 'validated'
            review.save()
            redirect('utama:review_request')
        return super(ValidatedReviewView, self).get(request, *args, **kwargs)

class RejectedReviewView(LoginRequiredMixin, TemplateView):
    login_url = 'utama:login'
    redirect_field_name = ''
    template_name = ('administrator/review_request_list.html')
    def get(self, request, *args, **kwargs):
        if(request.GET['submit'] is not None):
            review = Review.objects.get(pk=int(request.GET['submit']))
            review.status_validasi = 'rejected'
            review.save()
            redirect('utama:review_request')
        return super(RejectedReviewView, self).get(request, *args, **kwargs)
