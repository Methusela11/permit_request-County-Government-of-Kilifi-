from django.contrib import admin
from .models import PermitRequest

@admin.action(description='Approve selected permit requests')
def approve_permits(modeladmin, request, queryset):
    queryset.update(approved=True)

@admin.register(PermitRequest)
class PermitRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'ward', 'approved', 'submitted_at')
    list_filter = ('approved', 'ward', 'submitted_at')
    search_fields = ('full_name', 'id_number', 'phone')

    actions = [approve_permits]
