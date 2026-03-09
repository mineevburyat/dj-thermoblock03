from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
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