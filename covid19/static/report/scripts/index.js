$('p').css('text-align','justify')

const refTable = {'active_cases_page':'active_cases_class',
                'confirmed_cases_page':'confirmed_cases_class',
                'death_cases_page':'death_cases_class',
                'read_me_page':'read_me_page_class',
                'index_page':'index_class',
}

const x = $('.display_page').attr('id');
console.log(x);

$('.nav-link').removeClass('active');
$('#' + refTable[x]).addClass('active');
