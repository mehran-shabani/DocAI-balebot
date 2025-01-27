from django.contrib import admin
from .models import BaleUser, ChatSession


# Custom Admin for BaleUser
@admin.register(BaleUser)
class BaleUserAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'phone_number', 
        'chat_id', 
        'is_authenticated', 
        'daily_message_limit', 
        'current_message_count', 
        'assistant_role', 
        'system_role', 
        'token_limit'
    )
    # Fields to filter the list view
    list_filter = ('is_authenticated', 'assistant_role', 'system_role')
    # Fields for searching
    search_fields = ('phone_number', 'chat_id')
    # Fields that are read-only
    readonly_fields = ('current_message_count',)
    # Sections and fields to display in the edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('phone_number', 'chat_id', 'is_authenticated')
        }),
        ('Settings', {
            'fields': ('daily_message_limit', 'current_message_count', 'token_limit', 'assistant_role', 'system_role')
        }),
    )
    # Pagination for large datasets
    list_per_page = 25


# Custom Admin for ChatSession
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'user', 
        'assistant_role', 
        'system_role', 
        'created_at'
    )
    # Fields to filter the list view
    list_filter = ('assistant_role', 'system_role', 'created_at')
    # Fields for searching
    search_fields = ('user__phone_number', 'assistant_role', 'system_role')
    # Fields that are read-only
    readonly_fields = ('created_at',)
    # Sections and fields to display in the edit form
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Chat Details', {
            'fields': ('user_message', 'bot_response', 'assistant_role', 'system_role', 'created_at')
        }),
    )
    # Pagination for large datasets
    list_per_page = 25
