from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'utama'
urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^ganteng/', views.HomeView2.as_view(), name='home2'),

    url(r'^login/',views.login_view, name='login'),
    url(r'^logout/',views.Logout.as_view(), name='logout'),

    url(r'^signup/pengunjung/', views.pengunjung_registrasi, name='pengunjung_registrasi'),
    url(r'^signup/asuransi/', views.asuransi_registrasi, name='asuransi_registrasi'),
    url(r'^signup/rumah_sakit/', views.rumah_sakit_registrasi, name='rumah_sakit_registrasi'),

    url(r'^pencarian/', views.PencarianListView.as_view(), name='pencarian_list'),

    url(r'^berita/list/', views.BeritaListView.as_view(), name='list'),
    url(r'^berita/create/',views.BeritaCreateView.as_view(), name='create'),
    url(r'^berita/detail/(?P<pk>\d+)/$',views.BeritaDetailView.as_view(), name='detail'),
    url(r'^berita/update/(?P<pk>\d+)/$', views.BeritaUpdateView.as_view(), name='update'),
    url(r'^berita/delete/(?P<pk>\d+)/$', views.BeritaDeleteView.as_view(), name='delete'),

    url(r'^admin/detail/(?P<pk>\d+)/$',views.AdministratorDetailView.as_view(), name='administrator_detail'),
    url(r'^admin/update/(?P<pk>\d+)/$',views.AdministratorUpdateView.as_view(), name='administrator_update'),

    url(r'^admin/hubungan_rumah_sakit_asuransi/request/list/$', views.PermintaanHubunganAsuransiListView.as_view(), name='hubungan_request'),
    url(r'^admin/hubungan_rumah_sakit_asuransi/all/list/$', views.HubunganRumahSakitAsuransiListView.as_view(), name='hubungan_all'),
    url(r'^admin/hubungan_rumah_sakit_asuransi/validated/$', views.ValidatedHubunganAsuransiView.as_view(), name='hubungan_validated'),
    url(r'^admin/hubungan_rumah_sakit_asuransi/rejected/$', views.RejectedHubunganAsuransiView.as_view(), name='hubungan_rejected'),
    url(r'^admin/review/request/list/$', views.PermintaanReviewListView.as_view(), name='review_request'),
    url(r'^admin/review/all/list/$', views.ReviewAllListView.as_view(), name='review_all'),
    url(r'^admin/review/validated/$', views.ValidatedReviewView.as_view(), name='review_validated'),
    url(r'^admin/review/rejected/$', views.RejectedReviewView.as_view(), name='review_rejected'),
]
