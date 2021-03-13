// Enabling Bootstrap 5 popovers and tooltips on all pages:
$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
  $('[data-bs-toggle="tooltip"]').tooltip();
});


// Toggles visibility of select form by clicking on the country-title container:
$("#country-title").click(function(){
  $(".form-select").toggle();
});


// Toggles page and components visibility and then enables page visibility. This
// will allow visual comfortability during page load
$(document).ready(function(){
    const x = $('.display_page').attr('id');
    if (x === 'countries_page') {
      $('.form-select').css('visibility','visible')
    }
    else {
      $('.form-select').css('visibility','hidden')
    }
    $('html').css('visibility','visible')
});
