from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from apps.core.models.anggota import AnggotaKoperasi
from apps.modules.admin_daerah.models import RT

class AnggotaListView(LoginRequiredMixin, ListView):
    model = AnggotaKoperasi
    template_name = 'anggota/anggota.html'
    context_object_name = 'anggota_list'
    paginate_by = 20

    def get_queryset(self):
        return (
            AnggotaKoperasi.objects
            .select_related('rt', 'rt__rw', 'rt__rw__dusun')
            .order_by('-tanggal_daftar')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_anggota'] = AnggotaKoperasi.objects.count()
        return context

class AnggotaCreateView(LoginRequiredMixin, CreateView):
    model = AnggotaKoperasi
    template_name = 'anggota/anggota_form.html'
    fields = ['nik', 'nama_lengkap', 'jenis_kelamin', 'email', 'no_hp', 'rt', 'status_verifikasi']
    success_url = reverse_lazy('anggota:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rt'].queryset = RT.objects.select_related('rw', 'rw__dusun').order_by('rw__dusun__nama', 'rw__nomor', 'nomor')
        form.fields['rt'].widget.attrs.update({'class': 'form-select'})
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            form.fields.pop('status_verifikasi')
        elif 'status_verifikasi' in form.fields:
            form.fields['status_verifikasi'].widget.attrs.update({'class': 'form-select'})
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Anggota berhasil ditambahkan')
        return super().form_valid(form)

class PublicAnggotaCreateView(CreateView):
    model = AnggotaKoperasi
    template_name = 'anggota/anggota_form.html'
    fields = ['nik', 'nama_lengkap', 'jenis_kelamin', 'email', 'no_hp', 'rt']
    success_url = reverse_lazy('landing-page')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rt'].queryset = RT.objects.select_related('rw', 'rw__dusun').order_by('rw__dusun__nama', 'rw__nomor', 'nomor')
        form.fields['rt'].widget.attrs.update({'class': 'form-select'})
        # Remove status_verifikasi for public registration
        if 'status_verifikasi' in form.fields:
            form.fields.pop('status_verifikasi')
        return form

    def form_valid(self, form):
        # Set default status to pending for public registrations
        form.instance.status_verifikasi = 'pending'
        messages.success(self.request, 'Pendaftaran berhasil! Tunggu verifikasi dari admin.')
        return super().form_valid(form)

class AnggotaUpdateView(LoginRequiredMixin, UpdateView):
    model = AnggotaKoperasi
    template_name = 'anggota/anggota_form.html'
    fields = ['nik', 'nama_lengkap', 'jenis_kelamin', 'email', 'no_hp', 'rt', 'status_verifikasi']
    success_url = reverse_lazy('anggota:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rt'].queryset = RT.objects.select_related('rw', 'rw__dusun').order_by('rw__dusun__nama', 'rw__nomor', 'nomor')
        form.fields['rt'].widget.attrs.update({'class': 'form-select'})
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            form.fields.pop('status_verifikasi')
        elif 'status_verifikasi' in form.fields:
            form.fields['status_verifikasi'].widget.attrs.update({'class': 'form-select'})
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Anggota berhasil diperbarui')
        return super().form_valid(form)


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def approve_anggota(request, pk):
    """Approve pending member application"""
    anggota = get_object_or_404(AnggotaKoperasi, pk=pk)
    if anggota.status_verifikasi == 'pending':
        anggota.status_verifikasi = 'verified'
        anggota.save()
        messages.success(request, f'Anggota {anggota.nama_lengkap} telah disetujui')
    else:
        messages.warning(request, 'Anggota sudah dalam status yang berbeda')
    return redirect('anggota:list')


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def reject_anggota(request, pk):
    """Reject pending member application by deleting the record"""
    anggota = get_object_or_404(AnggotaKoperasi, pk=pk)
    if anggota.status_verifikasi == 'pending':
        nama = anggota.nama_lengkap
        anggota.delete()
        messages.success(request, f'Pendaftaran anggota {nama} telah ditolak')
    else:
        messages.warning(request, 'Hanya pendaftaran pending yang dapat ditolak')
    return redirect('anggota:list')
