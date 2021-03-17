// Enabling Bootstrap 5 popovers and tooltips on all pages:
$(document).ready(function(){
  $('[data-bs-toggle="tooltip"]').tooltip();
  $('[data-bs-toggle="popover"]').popover();
});


// Toggles page and components visibility and then enables page visibility. This
// will allow visual comfortability during page load
$(document).ready(function(){
    const x = $('.display_page').attr('id');
    if (x === 'countries_page') {
      $('.flag').css('visibility','visible')
    }
    else {
      $('.flag').css('visibility','hidden')
    }
    $('html').css('visibility','visible')
});
