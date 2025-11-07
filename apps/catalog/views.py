from django.shortcuts import render


def product_list_view(request):
    """Product listing page"""
    return render(request, 'catalog/product_list.html')


def product_detail_view(request, slug):
    """Product detail page"""
    return render(request, 'catalog/product_detail.html', {'slug': slug})
