from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import BlockSeries, Block, CharacteristicGroup, MediaLibrary

class SeriesListView(ListView):
    """Список всех серий блоков"""
    model = BlockSeries
    template_name = 'products/series_list.html'
    context_object_name = 'series_list'
    
    def get_queryset(self):
        return BlockSeries.objects.filter(is_active=True).prefetch_related(
            'blocks', 'characteristic_groups', 'linked_media'
        ).select_related('main_image')


class SeriesDetailView(DetailView):
    """Детальная страница серии со списком блоков"""
    model = BlockSeries
    template_name = 'products/series_detail.html'
    context_object_name = 'series'
    
    def get_queryset(self):
        return BlockSeries.objects.filter(is_active=True).prefetch_related(
            'blocks',
            'blocks__main_image',
            'blocks__linked_media',
            'characteristic_groups',
            'linked_media'
        ).select_related('main_image')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.get_object()
        
        # Группируем блоки по типу
        blocks_by_type = {}
        for block in series.blocks.filter(is_active=True):
            block_type = block.get_block_type_display()
            if block_type not in blocks_by_type:
                blocks_by_type[block_type] = []
            blocks_by_type[block_type].append(block)
        
        context['blocks_by_type'] = blocks_by_type
        context['characteristic_groups'] = series.characteristic_groups.all()
        context['media_files'] = series.linked_media.all()
        
        return context
    
class CatalogView(TemplateView):
    """Основная страница каталога"""
    template_name = 'products/catalog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все активные серии
        series_list = BlockSeries.objects.all().order_by('order')
        # Получаем ID выбранной серии из GET параметра
        selected_series_id = self.request.GET.get('series')
        
        blocks = Block.objects.all().select_related(
                    'main_image', 
                    'characteristic_group'
                ).prefetch_related(
                    'linked_media'
                )
        # Если выбрана конкретная серия, получаем её блоки
        selected_series = None
        if selected_series_id:
            try:
                selected_series = BlockSeries.objects.get(
                    id=selected_series_id, 
                    is_active=True
                )
                blocks = Block.objects.filter(
                    series=selected_series,
                    is_active=True
                ).select_related(
                    'main_image', 
                    'characteristic_group'
                ).prefetch_related(
                    'linked_media'
                )
            except BlockSeries.DoesNotExist:
                pass
        context.update({
            'series_list': series_list,
            'selected_series': selected_series,
            'blocks': blocks,
            'media_types': dict(MediaLibrary.MEDIA_TYPES),
        })
        
        return context


class SeriesDetailViewNew(DetailView):
    """Детальная страница серии"""
    model = BlockSeries
    template_name = 'products/series_detail.html'
    context_object_name = 'series'
    
    def get_queryset(self):
        return BlockSeries.objects.filter(is_active=True).prefetch_related(
            'blocks',
            'blocks__main_image',
            'blocks__linked_media',
            'blocks__characteristic_group',
            'characteristic_groups',
            'linked_media'
        ).select_related('main_image')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.get_object()
        
        # Получаем все блоки серии
        blocks = series.blocks.filter(is_active=True).select_related(
            'main_image', 'characteristic_group'
        ).prefetch_related('linked_media')
        
        # Группируем блоки по типу
        blocks_by_type = {}
        for block in blocks:
            block_type = block.get_block_type_display()
            if block_type not in blocks_by_type:
                blocks_by_type[block_type] = []
            blocks_by_type[block_type].append(block)
        
        # Получаем все медиа серии
        media_items = list(series.linked_media.all())
        if series.main_image:
            # Добавляем главное изображение в начало списка
            media_items.insert(0, series.main_image)
        
        # Получаем документы и чертежи
        documents = series.linked_media.filter(media_type='document')
        drawings = series.linked_media.filter(media_type='drawing')
        videos = series.linked_media.filter(media_type__in=['video_file', 'video_link'])
        
        context.update({
            'blocks': blocks,
            'blocks_by_type': blocks_by_type,
            'media_items': media_items,
            'documents': documents,
            'drawings': drawings,
            'videos': videos,
            'characteristic_groups': series.characteristic_groups.all(),
            'media_count': len(media_items),
        })
        
        return context