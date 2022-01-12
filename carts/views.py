from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    """ loops through all the
    values from the request,
    e.g. size, color, etc. to
    include those values in
    the POST """
    product = Product.objects.get(id=product_id) #gets product
    product_variation = [] #gets product variations
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
            except:
                    pass

    """ End of comment context """

    """ This whole section gets the cart. """
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
    cart.save()

    """ End of comment context """

    """ This whole section gets the cart *item*. """
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    # Checks whether cart item exists and stores result in the variable is_cart_item_exists
    if is_cart_item_exists:
        # Returns cart item objects.
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        # Sets up an empty list in which to store existing variations later.
        id = []
        # Sets up an empty list of cart item IDs.
        for item in cart_item:
            existing_variation = item.variations.all()
            # Stores all preexisting variations from the DB in the variable.
            ex_var_list.append(list(existing_variation))
            #Puts all preexisting variations, as stored in the var, into the previously empty list.
            #Make it a list to convert from a query set.
            id.append(item.id)
            # Adds cart item IDs to the previously empty list

        print(ex_var_list)

        if product_variation in ex_var_list:
            # Checks whether the current product variation is in the existing list/DB.
            index = ex_var_list.index(product_variation)
            # Returns the index position at which an item is found in a list or a string.
            # Puts the result in the variable.
            item_id = id[index]
            # Puts the index number / item ID in the variable.
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            # Increments the number of that item with those variation by 1.
            item.save()
        else:
            # This block creates a new item if one with those variations isn't already in the cart.
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                # Checks whether the product variation list is empty
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
         cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
         )
         if len(product_variation) > 0: # Checks whether the product variation list is empty
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
         cart_item.save()
    return redirect('cart')

    """ End of comment context """

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #ignore

    context = {
        'total': total,
        'quantity'    : quantity,
        'cart_items'  : cart_items,
        'tax'         : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html', context)
