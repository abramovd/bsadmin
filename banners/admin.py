from urllib.parse import urljoin

from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django_select2.forms import Select2MultipleWidget
from django.urls import reverse
from django.utils.html import format_html

from banners.backend import publish
from helpers.fields import ChoiceArrayField
from banners.models import (
    Banner, Slot, Page, Publication, BannerSnapshot,
)


class ArrayFieldSelectMultiple(Select2MultipleWidget):

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs['data-width'] = '50em'
        return attrs


class BannerAdmin(admin.ModelAdmin):
    model = Banner
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'slot', ),
        }),
        ('Settings', {
            'fields': (
                'priority', 'start_time', 'end_time',
                'dismissible', 'stopped',
            ),
        }),
        ('Segmentation', {
            'fields': ('countries', 'languages', 'segments'),
        }),
        ('Body', {
            'fields': ('body',),
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('create_time', 'update_time', 'published_at'),
        }),
    )
    readonly_fields = (
        'id',
        'create_time',
        'update_time',
    )
    autocomplete_fields = (
        'slot',
    )
    formfield_overrides = {
        ChoiceArrayField: {
            'widget': ArrayFieldSelectMultiple,
        },
    }
    search_fields = ('name', )

    list_display = (
        'name', 'create_time', 'update_time', 'priority',
        'has_changes_to_publish',
        'stopped',
    )
    list_filter = (
        'stopped',
    )

    actions = (
        'publish',
        'duplicate',
    )

    def has_changes_to_publish(self, obj):
        return obj.published_at is None or obj.update_time > obj.published_at
    has_changes_to_publish.boolean = True

    @staticmethod
    def get_banners_by_publication_url(publication):
        return urljoin(
            reverse('admin:banners_banner_changelist'),
            f'?publications__in=[{publication.id}]'
        )

    def publish(self, request, queryset):
        republished_banners, newly_published = publish(publisher=request.user)
        self.message_user(
            request,
            f'Kept published: {republished_banners} banners',
        )
        self.message_user(
            request,
            f'Newly Published: {newly_published} banners',
        )
        self.message_user(
            request,
            f'Total currently published: '
            f'{republished_banners + newly_published} banners',
        )
    publish.allowed_permissions = ('publish',)

    def has_publish_permission(self, request):
        """Does the user have the publish permission?"""
        opts = self.opts
        codename = get_permission_codename('publish', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def duplicate(self, request, queryset):
        duplicated_banners = queryset.duplicate()
        self.message_user(
            request,
            f'Duplicated: {len(duplicated_banners)} banners',
        )
    duplicate.allowed_permissions = ('duplicate',)

    def has_duplicate_permission(self, request):
        """Does the user have the duplicate permission?"""
        opts = self.opts
        codename = get_permission_codename('copy', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


class SlotAdmin(admin.ModelAdmin):
    model = Slot
    readonly_fields = (
        'id',
        'create_time',
        'update_time',
    )
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'page', 'description'),
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('create_time', 'update_time'),
        }),
    )
    search_fields = ('name',)


class PageAdmin(admin.ModelAdmin):
    model = Page
    readonly_fields = (
        'create_time',
        'update_time',
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Audit', {
            'classes': ('collapse',),
            'fields': ('create_time', 'update_time'),
        }),
    )
    search_fields = ('name',)


class BannerSnapshotAdmin(admin.ModelAdmin):
    model = BannerSnapshot

    fields = (
        'id',
        'name',
        'priority',
        'countries',
        'start_time',
        'end_time',
        'dismissible',
        'body',
        'languages',
        'segments',
        'slot_link',
        'banner_link',
    )
    readonly_fields = fields

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @staticmethod
    def banner_link(obj):
        url = reverse('admin:banners_banner_change',
                      args=[obj.original_banner.id, ])
        return format_html(
            '<a href="{}">Banner {}</a>',
            url, obj.original_banner.name,
        )

    banner_link.short_description = 'Banner'
    banner_link.allow_tags = True

    @staticmethod
    def slot_link(obj):
        url = reverse('admin:banners_slot_change', args=[obj.slot['id'], ])
        return format_html(
            '<a href="{}">Slot {}</a>',
            url, obj.slot['name'],
        )

    slot_link.short_description = 'Slot'
    slot_link.allow_tags = True


class BannerSnapshotInlineAdmin(admin.TabularInline):
    model = BannerSnapshot.publications_log.through

    fields = (
        'snapshot_link',
    )
    readonly_fields = fields

    verbose_name = 'Banner Snapshot'
    verbose_name_plural = 'Published Banners Snapshots'

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    @staticmethod
    def snapshot_link(obj):
        url = reverse('admin:banners_bannersnapshot_change',
                      args=[obj.bannersnapshot.id, ])
        return format_html(
            '<a href="{}">Banner {} ({})</a>',
            url, obj.bannersnapshot.name, obj.bannersnapshot.create_time,
        )

    snapshot_link.short_description = 'Banner'
    snapshot_link.allow_tags = True


class PublicationAdmin(admin.ModelAdmin):
    model = Publication
    readonly_fields = (
        'create_time',
        'update_time',
        'published_at',
        'published_by',
        'state',
    )
    fields = readonly_fields
    list_filter = (
        'state',
    )
    list_display = (
        'id', 'create_time', 'state', 'published_at', 'published_by',
    )
    inlines = [
        BannerSnapshotInlineAdmin,
    ]
    exclude = ('publications_log', )


admin.site.register(Banner, BannerAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(BannerSnapshot, BannerSnapshotAdmin)
