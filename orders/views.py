import secrets
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from marketplace.models import Cart
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from marketplace.context_processors import get_cart_amounts
from accounts.utils import send_notification_email
from django.utils.translation import gettext as _
from orders.utils import generate_order_number
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
# Create your views here.


@login_required(login_url='login')
def place_order(request):
    reference = secrets.token_hex(8)  # unique ref
    user = request.user
    cart_items = Cart.objects.filter(user=user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        messages.warning(request, _(
            'Your cart is empty. Please add items to your cart before proceeding to checkout.'))
        return redirect('marketplace')

    subtotal = get_cart_amounts(request).get('cart_subtotal', 0)
    tax = get_cart_amounts(request).get('cart_tax', 0)
    total = get_cart_amounts(request).get('cart_total', 0)
    tax_data = get_cart_amounts(request).get('tax_dict', {})

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                pin_code=form.cleaned_data['pin_code'],
                country=form.cleaned_data['country'],
                user=user,
                total_tax=tax,
                total=total,
                tax_data=tax_data,
                payment_method=request.POST.get('payment_method', 'COD'),
            )
            order.save()

            # ✅ Generate order number after saving (so pk exists)
            order.order_number = generate_order_number(order.pk)
            order.save(update_fields=["order_number"])

            context = {
                'order': order,
                'cart_items': cart_items,
                'reference': reference,
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'tax_dict': tax_data,
                'form': form,
            }

            messages.success(
                request, 'Your order has been saved successfully!')
            return render(request, "orders/place_order.html", context)
        else:
            messages.error(
                request, 'There was an error placing your order. Please try again.')
    else:
        form = OrderForm()

    return render(request, "orders/place_order.html", )


@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("reference")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")

        order = Order.objects.get(user=request.user, order_number=order_number)

        payment = Payment(
            user=request.user,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount=order.total,
            status=status
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save(update_fields=['payment', 'is_ordered'])

        cart_items = Cart.objects.filter(user=request.user)

        # Prepare bulk insert list
        ordered_food_list = [
            OrderedFood(
                order=order,
                payment=payment,
                user=request.user,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
                amount=item.fooditem.price * item.quantity
            )
            for item in cart_items
        ]
        OrderedFood.objects.bulk_create(ordered_food_list)

        # Send order confirmation email to customer
        mail_subject = "Thank you for your order!"
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email
        }

        send_notification_email(mail_subject, mail_template, context)

        # Send order received email to vendors
        mail_subject = "You have received a new order!"
        mail_template = "orders/new_order_received_email.html"

        # Use a set to avoid duplicate emails if a vendor has multiple items
        vendors = set(item.fooditem.vendor for item in cart_items)

        for vendor in vendors:
            vendor_items = [
                item for item in cart_items if item.fooditem.vendor == vendor]

            context = {
                "user": vendor.user,
                "order": order,
                "to_email": vendor.user.email,
                "items": vendor_items,
                'total_amount': sum(item.fooditem.price * item.quantity for item in vendor_items),
            }
            print("Vendor Email Context:", context)

            send_notification_email(mail_subject, mail_template, context,)

        # Clear cart
        cart_items.delete()

        return JsonResponse({
            "status": "success",
            "message": "Payment processed successfully.",
            "order_number": order.order_number,
            "transaction_id": payment.transaction_id,
            "payment_method": payment.payment_method,
            "amount": payment.amount,
        })


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")

    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            user=request.user,
            is_ordered=True,
        )

        ordered_foods = OrderedFood.objects.filter(order=order)
        subtotal = sum(item.amount for item in ordered_foods)
        tax = order.total_tax
        grand_total = subtotal + tax

        if not ordered_foods.exists():
            messages.error(request, "No items were found in this order.")
            return redirect("home")

        context = {
            "order": order,
            "ordered_foods": ordered_foods,
            "subtotal": subtotal,
            "tax": tax,
            "grand_total": grand_total,
        }
        return render(request, "orders/order_complete.html", context)

    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect("home")


def download_receipt(request):
    order_number = request.GET.get("order_number")
    order = Order.objects.get(user=request.user, order_number=order_number)
    ordered_foods = OrderedFood.objects.filter(order=order)

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{order.order_number}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Order Receipt")
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Order Number: {order.order_number}")
    y -= 20
    p.drawString(50, y, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Payment Method: {order.payment.payment_method}")
    y -= 20
    p.drawString(50, y, f"Transaction ID: {order.payment.transaction_id}")
    y -= 40

    # Table header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Food Item")
    p.drawString(250, y, "Qty")
    p.drawString(300, y, "Price")
    p.drawString(400, y, "Amount")
    y -= 20
    p.line(50, y, 500, y)
    y -= 20

    # Table rows
    p.setFont("Helvetica", 12)
    for item in ordered_foods:
        p.drawString(50, y, item.fooditem.food_title)
        p.drawString(250, y, str(item.quantity))
        p.drawString(300, y, f"₦{item.price}")
        p.drawString(400, y, f"₦{item.amount}")
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y, "Total:")
    p.drawString(400, y, f"₦{order.payment.amount_paid}")

    # Finish PDF
    p.showPage()
    p.save()
    return response
