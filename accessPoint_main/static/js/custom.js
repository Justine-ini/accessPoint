
// Alert message timer function
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    const overlay = document.getElementById('message-overlay');
    if (overlay) {
      overlay.style.transition = "opacity 1s ease-out";
      overlay.style.opacity = 0;
      setTimeout(() => {
        overlay.style.display = 'none';
      }, 1000);
    }
  }, 5000);
});


let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "NG" - add your country code
        componentRestrictions: {'country': ['ng']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value
    geocoder.geocode({'address': address}, function(results, status){
      if(status == google.maps.GeocoderStatus.OK){
        var latitude = results[0].geometry.location.lat();
        var longitude = results[0].geometry.location.lng();
        $('#id_latitude').val(latitude)
        $('#id_longitude').val(longitude)
        
        $('#id_address').val(address)

      }
    });
    // Loop through the address components and assign the other address data
    console.log(place.address_components)
    for(var i=0; i<place.address_components.length; i++){
      for(var j=0; j<place.address_components[i].types.length; j++){
        // get country
        if(place.address_components[i].types[j] == 'country'){
          $('#id_country').val(place.address_components[i].long_name)
        }
        // get state
        if(place.address_components[i].types[j] == 'administrative_area_level_1'){
          $('#id_state').val(place.address_components[i].long_name)
        }
        // get city
        if(place.address_components[i].types[j] == 'administrative_area_level_2'){
          $('#id_city').val(place.address_components[i].long_name)
        }
        // get pincode
        if(place.address_components[i].types[j] == 'postal_code'){
          $('#id_pincode').val(place.address_components[i].long_name)
        }else{
          $('#id_pincode').val("N/A")
        }

      }
      
    }
}