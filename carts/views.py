from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart =request.session.create()
    return cart

def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id =product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product= product, user=request.user, id =cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product= product, cart=cart, id =cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get by id
    # is the user is authenticatec
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            #color = request.POST['color']
            #size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]
                #print(key, value)
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product= product, user = current_user).exists() # sprawdz czy istnieje dany produkt w koszyku
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product, user = current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.product_variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                #increase quantity of this cart item
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product= product, id = item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product = product, quantity =1, user = current_user)
                if len(product_variation) >0:
                    item.product_variation.clear()
                    item.product_variation.add(*product_variation) # * sprawia, że dodaje wszystkie wariancje produktów

            #cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) >0:
                cart_item.product_variation.clear()
                cart_item.product_variation.add(*product_variation)
            cart_item.save()
        #return HttpResponse(cart_item.product)
        return redirect('cart')
    else:
        product_variation = []
        if request.method == 'POST':
            #color = request.POST['color']
            #size = request.POST['size']
            for item in request.POST:
                key = item
                value = request.POST[key]
                #print(key, value)
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart= Cart.objects.get(cart_id=_cart_id(request)) #gte the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save() ### być może wciecie mniej

        is_cart_item_exists = CartItem.objects.filter(product= product, cart=cart).exists() # sprawdz czy istnieje dany produkt w koszyku
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product, cart = cart)
            #existing variation ->database

            #current variation -> prudct_variation
            #item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.product_variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                #increase quantity of this cart item
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product= product, id = item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product = product, quantity =1, cart = cart)
                if len(product_variation) >0:
                    item.product_variation.clear()
                    item.product_variation.add(*product_variation) # * sprawia, że dodaje wszystkie wariancje produktów

            #cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) >0:
                cart_item.product_variation.clear()
                cart_item.product_variation.add(*product_variation)
            cart_item.save()
        #return HttpResponse(cart_item.product)
        return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id =product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product= product, user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product= product, cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request):
    return render(request, 'store/cart.html')

def cart(request, total= 0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user= request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart= cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.product.price)  ### to check
            quantity += cart_item.quantity
        tax = (23 * total)/100
        grand_total = total  + tax

    except ObjectDoesNotExist:
        pass # ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total= 0, quantity=0, cart_items=None):
    try:
        #tax = 0
        #grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user= request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart= cart,is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.product.price)  ### to check
            quantity += cart_item.quantity
        tax = (23 * total)/100
        grand_total = total  + tax

    except ObjectDoesNotExist:
        pass # ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
