import random
import string
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
import json
from json import JSONEncoder
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm ,UserCreationForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            print("GETTTTTTTTT")
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                #default=True
            )
            print("ADRESS")
            print(shipping_address_qs)
            if shipping_address_qs.exists():
                print ("PRESENT")
                print(shipping_address_qs[0])
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = UserCreationForm(self.request.POST or None or self.request.GET)
        print("FORM")
        print (form)
        use_saved_address=False
        use_saved_address_2 = False
        need_prescription=False



        complete_address=''
        if (form.data['customer_mobile'] != '' and form.data['shipping_address'] != ''
         and form.data['customer_name'] != ''):
            use_saved_address=True
            use_saved_address_2=True
        else:
            use_saved_address=True


        try:
            order_qs = Order.objects.filter(
                user=self.request.user,
                ordered=False
            )
            if order_qs.exists():
                order = order_qs[0]
                # check if the order item is in the order
                if order.items.filter(item__prescription=True).exists():
                    need_prescription=True


            if (use_saved_address == True):
                print("OKOKOK")

                if use_saved_address_2 == False:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    print("HERE I AM")
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        complete_address=str(address_qs[0].customer_name)+" "+str(address_qs[0].customer_mobile)+" "+str(address_qs[0].street_address)+" "+str(address_qs[0].apartment_address)+" "+str(address_qs[0].locality_address)+" "+str(address_qs[0].city_address)+" "+str(address_qs[0].landmark_address)
                        print(complete_address)
                        order.shipping_address = shipping_address
                        order.address_of_order=complete_address
                        print ("ORDER SAVED")
                        order.save()

                        if need_prescription:
                            return redirect('core:upload_prescription')
                        else:
                            order_items = order.items.all()
                            order.ref_code = create_ref_code()
                            order_items.update(ordered=True)
                            order_items.update(bill_no=order.ref_code)
                            for item in order_items:
                                item.save()
                            amount1 = int(order.get_total() * 100)
                            order.ordered = True

                            order.amount = amount1

                            order.save()

                            messages.success(self.request, "Your order was successful!")
                            return redirect("/")
                    else:
                        print("SEt as DEFAULT222")
                        shipping_address1 = form.cleaned_data.get(
                            'shipping_address')
                        shipping_address2 = form.cleaned_data.get(
                            'shipping_address2')

                        shipping_zip = form.cleaned_data.get('shipping_zip')
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,

                            zip="226",
                            address_type='S'
                        )
                        shipping_address.save()
                        print (shipping_address)
                        print("SEt as DEFAULT")
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()
                        messages.info(
                            self.request, "ordered")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    cust = form.cleaned_data.get(
                        'customer_name')
                    mob = form.cleaned_data.get(
                        'customer_mobile')
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    loc = form.cleaned_data.get(
                        'locality_address')
                    city = form.cleaned_data.get(
                        'city_address')
                    land = form.cleaned_data.get(
                        'landmark_address')
                    shipping_zip = "SS"

                    if is_valid_form([shipping_address1, shipping_zip]):

                        shipping_address = Address(
                            user=self.request.user,
                            customer_name=cust,
                            customer_mobile=mob,

                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            locality_address=loc,
                            city_address=city,
                            landmark_address=land,

                            zip="226",
                            address_type='S'
                        )
                        shipping_address.save()
                        complete_address=cust+" "+mob+" "+shipping_address1+" "+shipping_address2+" "+loc+" "+city+" "+land
                        order.shipping_address = shipping_address
                        order.address_of_order = complete_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                        return redirect('core:upload_prescription')
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
            else:
                print ("EMPTY")
                print (form.errors)
                return HttpResponse(form.errors)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")
        print("NI HUA")
        return render( 'core:checkout', {'form': form})

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


def home(request):
    if 'term' in request.GET:
        qs = Item.objects.filter(title__istartswith=request.GET.get('term'))
        print(qs)
        titles = list()
        for product in qs:
            print(product)
            titles.append(str(product))

        # titles = [product.title for product in qs]
        # employeeJSON = json.loads(titles)
        return JsonResponse(titles, safe=False)



    return render(request, 'home.html')


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


def autocomplete1(request):
    if 'term' in request.GET:
        qs = Item.objects.filter(title__istartswith=request.GET.get('term'))
        print(qs)
        titles = list()
        for product in qs:
            print(product)
            titles.append(str(product))

        # titles = [product.title for product in qs]
        # employeeJSON = json.loads(titles)
        return JsonResponse(titles, safe=False)
    print("AA")
    return render(request, 'demo2.html')


class SearchResultsView(ListView):
    model = Item
    template_name = 'search_results.html'

    def get_queryset(self): # new
        query = self.request.GET.get('Search')
        object_list = Item.objects.filter(
            Q(title__icontains=query) | Q(price__icontains=query)
        )
        return object_list



class AccountSetting(TemplateView):
    def get(self, *args, **kwargs):
        try:
            order_qs = Item.objects.filter(
                title="cro cro").values('title', 'price')
            s=order_qs[0]

            print (s['title'])
            books = {
                'title':  s['title'],
                'num': s['price'],
            }
            print (books)
            return render(self.request, "account_setting.html", {'books':books})
        except ObjectDoesNotExist:

            return redirect("core:checkout")


class OrderHistory(TemplateView):
    def get(self, *args, **kwargs):
        try:
            all_order=Order.objects.filter(user=self.request.user,ordered=False)
            all_order2 = Order.objects.filter(user=self.request.user).order_by('start_date').reverse()
            context = {
                'object': all_order2
            }
            s=all_order[0]
            for checked_object in all_order[0].items.all():
                print(checked_object.item)

            for o in all_order2:
                for b in o.items.all():
                    print( b.item )

            if 'term' in self.request.GET:
                qs = Item.objects.filter(title__istartswith=request.GET.get('term'))
                print(qs)

            return render(self.request, "orderhistory.html",context)
        except ObjectDoesNotExist:

            return redirect("core:orderhistory")




class upload_prescription(ListView):
    model = Item
    template_name = 'upload_prescription.html'


