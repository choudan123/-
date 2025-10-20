from django.contrib import admin
from .models import (
    Scene, PosterType, Style, ColorScheme, Layout, Size, AspectRatio,
    Font, ReferenceImage
)

admin.site.register(Layout)
admin.site.register(Size)
admin.site.register(Font)
admin.site.register(ReferenceImage)

@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    search_fields = ('name', 'tags')

@admin.register(PosterType)
class PosterTypeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'tags')

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    search_fields = ('name', 'tags')

@admin.register(ColorScheme)
class ColorSchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_color', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'main_color')
    ordering = ('order',)

@admin.register(AspectRatio)
class AspectRatioAdmin(admin.ModelAdmin):
    list_display = ('name', 'ratio_w', 'ratio_h', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)