// Enabling Bootstrap 5 popovers and tooltips on all pages:
$(document).ready(function(){
  $('[data-bs-toggle="tooltip"]').tooltip();
  $('[data-bs-toggle="popover"]').popover({
    html:true,
    content:function(){
      return $(this).html()
    }
  });
});


var myDefaultAllowList = bootstrap.Tooltip.Default.allowList

// To allow table elements
myDefaultAllowList.table = []


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

$('#btnshowweektable').click(function(){
  if ($(this).text()==="Show table") {
    $(this).text('Hide table');
  }
  else {
    $(this).text('Show table');
  }
})

$('#btnshowmonthtable').click(function(){
  if ($(this).text()==="Show table") {
    $(this).text('Hide table');
  }
  else {
    $(this).text('Show table');
  }
})


$('#showweektable').click(function(){
  if ($('#weektable').text()==="Hide table") {
    $('#weektable').html("Show table");
  }
  else {
    $('#weektable').html("Hide table");
  }
})
