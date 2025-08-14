// Alert message timer function
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    const overlay = document.getElementById("message-overlay");
    if (overlay) {
      overlay.style.transition = "opacity 1s ease-out";
      overlay.style.opacity = 0;
      setTimeout(() => {
        overlay.style.display = "none";
      }, 1000);
    }
  }, 5000);
});

let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      //default in this app is "NG" - add your country code
      componentRestrictions: { country: ["ng"] },
    }
  );
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  } else {
    // console.log('place name=>', place.name)
  }
  // get the address components and assign them to the fields
  var geocoder = new google.maps.Geocoder();
  var address = document.getElementById("id_address").value;
  geocoder.geocode({ address: address }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();
      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);
      $("#id_address").val(address);
    }
  });
  // Loop through the address components and assign the other address data
  console.log(place.address_components);
  for (var i = 0; i < place.address_components.length; i++) {
    for (var j = 0; j < place.address_components[i].types.length; j++) {
      // get country
      if (place.address_components[i].types[j] == "country") {
        $("#id_country").val(place.address_components[i].long_name);
      }
      // get state
      if (
        place.address_components[i].types[j] == "administrative_area_level_1"
      ) {
        $("#id_state").val(place.address_components[i].long_name);
      }
      // get city
      if (
        place.address_components[i].types[j] == "administrative_area_level_2"
      ) {
        $("#id_city").val(place.address_components[i].long_name);
      }
      // get postal code
      if (place.address_components[i].types[j] == "postal_code") {
        $("#id_pincode").val(place.address_components[i].long_name);
      } else {
        $("#id_pincode").val("N/A");
      }
    }
  }
}

// ADD CART
$(document).ready(function () {
  // Add to cart handler
  $(".add_to_cart").on("click", function (e) {
    e.preventDefault();

    const food_id = $(this).attr("data-id");
    const url = $(this).attr("data-url");

    if (!food_id || !url) {
      console.warn("Missing data-id or data-url on add_to_cart element");
      return;
    }

    $.ajax({
      type: "GET",
      url: url,
      data: { food_id: food_id },

      success: function (response) {
        console.log(response);

        const notyf = new Notyf();

        if (response.status === "login_required") {
          notyf.error(response.message || "Login required. Redirecting...");
          setTimeout(function () {
            window.location.href = "/login";
          }, 1500);
          return;
        }

        if (response.status === "success") {
          // Update cart counter
          if (response.cart_counter) {
            $("#cart_counter").html(response.cart_counter["cart_count"]);
          }

          // Update quantity display
          if (typeof response.qty !== "undefined") {
            $("#qty-" + food_id).html(response.qty);
          }
          // Update cart amounts
          if (response.cart_amounts) {
            updateCartSummary(response.cart_amounts);
          }
        } else {
          // Display failure message
          notyf.error(response.message || "Something went wrong.");
        }
      },

      error: function (xhr, errmsg, err) {
        console.error(`${xhr.status}: ${xhr.responseText}`);
        const notyf = new Notyf();
        notyf.error("An error occurred. Please try again.");
      },
    });
  });

  // Initialize item quantities on page load
  $(".item_qty").each(function () {
    const the_id = $(this).attr("id");
    const qty = $(this).data("qty") || 0;
    $("#" + the_id).html(qty);
  });
});


// DECREASE CART

$(document).ready(function () {
  const notyf = new Notyf();
  $(".decrease_cart").on("click", function (e) {
    e.preventDefault();

    const food_id = $(this).attr("data-id");
    const url = $(this).attr("data-url");
    const cart_id = $(this).attr("id");

    if (!food_id || !url) {
      console.warn("Missing food ID or URL");
      return;
    }

    $.ajax({
      type: "GET",
      url: url,
      data: { food_id: food_id },

      success: function (response) {
        console.log(response);


        if (response.status === "login_required") {
          notyf.error(response.message || "Please log in to continue.");

          setTimeout(function () {
            window.location.href = "/login";
          }, 1500);
          return; // Stop further execution
        }

        if (response.status === "success") {
          // Update cart counter
          if (response.cart_counter) {
            $("#cart_counter").html(response.cart_counter["cart_count"]);
          }
          // Update cart amounts
          if (response.cart_amounts) {
            updateCartSummary(response.cart_amounts);
          }
          // Update quantity display
          const qtyElement = $("#qty-" + food_id);
          if (qtyElement.length) {
            const newQty = response.qty > 0 ? response.qty : 0;
            qtyElement.html(newQty);
          }
          // If quantity is 0, remove the item from the cart
          if (window.location.pathname === "/cart/") {
            if (response.qty === 0) {
              $(`#cart-item-${cart_id}`).remove();
              notyf.success("Item removed from carts.");
            }
            // If no items left, show empty cart message
            const remaining = $(".menu-itam-list ul li").length;
            if (remaining === 0) {
              $("#menu-item-list-6272").hide(); // ⬅️ hide list container
              $("#empty-cart-message").show(); // ⬅️ show empty message
            }
          }
          
        } else {
          notyf.error(response.message || "Something went wrong.");
        }
      },

      error: function (xhr, errmsg, err) {
        console.error(xhr.status + ": " + xhr.responseText);
        notyf.error("An unexpected error occurred.");
      },
    });
  });
});

// REMOVE FROM CART
$(document).ready(function () {
  const notyf = new Notyf();

  $(".remove_from_cart").on("click", function (e) {
    e.preventDefault();

    const cart_id = $(this).attr("data-id");
    const url = $(this).attr("data-url");

    if (!cart_id || !url) {
      console.warn("Missing cart ID or URL");
      return;
    }

    $.ajax({
      type: "GET",
      url: url,
      data: { cart_id: cart_id },

      success: function (response) {
        console.log(response);

        if (response.status === "login_required") {
          notyf.error(response.message || "Please log in to continue.");
          setTimeout(() => (window.location.href = "/login"), 1500);
          return;
        }

        if (response.status === "success") {
          // Update cart counter
          if (response.cart_counter) {
            $("#cart_counter").text(response.cart_counter.cart_count);
            notyf.success(response.message || "Item removed from cart.");
          }

          // Remove the item from the cart display
          $(`#cart-item-${cart_id}`).remove();


          // ⬅️ AFTER removal, check if any items remain:
          const remaining = $(".menu-itam-list ul li").length;
          if (remaining === 0) {
            // Show only the empty cart card
            $("#menu-item-list-6272").hide(); // ⬅️ hide list container
            $("#empty-cart-message").show(); // ⬅️ show empty message
          }
          
          // Update cart amounts
          if (response.cart_amounts) {
            updateCartSummary(response.cart_amounts);
          } 
        } else {
          notyf.error(response.message || "Something went wrong.");
        }
      },

      error: function (xhr) {
        console.error(xhr.status + ": " + xhr.responseText);
        notyf.error("An unexpected error occurred.");
      },
    });
  });

  // Get the values of the input

  $('.add_hour').on("click", function (e) {
    e.preventDefault();
    const day = document.getElementById('id_day').value
    const from_hour = document.getElementById('id_from_hour').value
    const to_hour = document.getElementById('id_to_hour').value
    const is_closed_checked = document.getElementById('id_is_closed').checked;
    const csrf_token = $('input[name=csrfmiddlewaretoken]').val()
    const url = document.getElementById('add_hour_url').value
    console.log(day, from_hour, to_hour, is_closed_checked, csrf_token);

    let is_closed = is_closed_checked ? 'True' : 'False';

  // Validate day is always required
  if (!day) {
      notyf.error("Please select a day");
      return;
  }

  if (!is_closed && (!fromHour || !toHour)) {
    notyf.error('Please fill both opening and closing times');
    return;
  }

  if (day !== '' && from_hour !== '' && to_hour !== '') {
    $.ajax({
      type: 'POST',
      url: url,
      data: {
        'day': day,
        'from_hour': from_hour,
        'to_hour': to_hour,
        'is_closed': is_closed,
        'csrfmiddlewaretoken': csrf_token,
      },
      success: function(response){

        if (response.status == 'success'){

          if (response.is_closed == 'Closed'){
            html = `<tr id="hour-${response.id}">
                    <td><b>${response.day}</b></td>
                    <td>${response.is_closed}</td>
                    <td><a href="#" style="text-decoration: none;" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td>
                    </tr>`;

            notyf.success("Your holiday is successfully added!");
          }else{
            html = `<tr id="hour-${response.id}">
                        <td><b>${response.day}</b></td>
                        <td>${response.from_hour} - ${response.to_hour}</td>
                        <td><a href="#" style="text-decoration: none;" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td>
                    </tr>`;
            notyf.success(response.message || "Opening hour added successfully!.");
          }
          console.log(response)
         
          $(".opening_hours").append(html);
          location.reload(true); 
          document.getElementById("opening_hours").reset();

        }else{
          notyf.error(response.message || "An entry for this day already exists.");
        }
      }
    })
  } else {
    notyf.error( "Please fill all fields.");
  }
  });


  // Remove opening hour
  $(document).on('click', '.remove_hour', function(e){
    e.preventDefault();
    const url = $(this).attr("data-url");

    if(!url) {
      console.warn("Missing ID or URL");
      return;
    };
    
    $.ajax({
      type: "GET",
      url: url,
      success: function(response){
        if (response.status == 'success'){
          // Remove the item from the cart display
          $(`#hour-${response.id}`).remove();
          notyf.success(response.message || "Opening hour deleted successfully!.");
          console.log(response)
        }else{
          notyf.error(response.message || "Not successfully deleted.");
        }
      }
    })
  })

});


// Update cart summary function
function updateCartSummary(response) {
  // Only run on the /cart/ page
  if (window.location.pathname === "/cart/") {
    if (response && typeof response.cart_subtotal !== "undefined" &&
        typeof response.tax_dict !== "undefined" &&
        typeof response.cart_total !== "undefined") {
      // Update each field
      $("#cart_subtotal").html(response.cart_subtotal);
      $("#tax_dict").html(response.tax_dict);
      $("#cart_tax").html(response.cart_tax);
      $("#cart_total").html(response.cart_total);

      for (key1 in response.tax_dict) {
        for(key2 in response.tax_dict[key1])
        // Update each tax item
        $(`#tax_dict-`+key1).html(response.tax_dict[key1][key2]);

      }
    }
  }
}

