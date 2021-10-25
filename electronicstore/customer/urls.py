from django.urls import path
from customer import views


urlpatterns = [
    path('register',views.RegistrationView.as_view(), name='register'),
    path('login', views.SignInView.as_view(), name='cust_signin'),
    path('signout',views.signout,name='signout'),
    path('home',views.HomePageView.as_view(), name='customer_home'),
    path('search',views.search,name="search"),
    path('mobiles',views.mobiles,name="mobiles"),
    path('laptops',views.laptops,name="laptops"),
    path('tablets',views.tablets,name="tablets"),
    path('price_low_to_high',views.price_low_to_high,name="price_low_to_high"),
    path('price_high_to_low', views.price_high_to_low, name="price_high_to_low"),
    path("view_profile",views.ViewDetails.as_view(), name="view_profile"),
    path("edit", views.EditDetails.as_view(), name="edit_profile"),
    path('viewproduct/<int:id>', views.ViewProduct.as_view(), name='viewproduct'),
    path('addtocart/<int:id>', views.add_to_cart, name='addtocart'),
    path('mycart', views.MyCart.as_view(), name='mycart'),
    path('removeitem/<int:pk>', views.DeleteFromCart.as_view(), name='deletecart'),
    path("placeorder/<int:pid>/<int:cid>", views.place_order, name="placeorder"),
    path("vieworders", views.view_orders, name="vieworders"),
    path("removeorder/<int:id>", views.cancel_order, name="removeorder"),
    path('viewproduct/<int:id>/writereview',views.WriteReview.as_view(),name='write_review'),
    path('brand/<int:pk>',views.FilterByBrand.as_view(),name='brandfilter'),
    path('base',views.BasePage.as_view(),name='basepage'),
    path('plus/<int:pk>',views.cart_plus,name='plus'),
    path('minus/<int:pk>',views.cart_minus,name='minus'),
]