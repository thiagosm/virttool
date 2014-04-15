$(document).ready(function(){
    
    $('int_field').setMask('99999999999999999999');

    $('.mac_field').keypress(function(){
         var macval = $('.mac').setMask('**:**:**:**:**:**').val();
         macval = macval.replace(/([^0-9a-fA-F:])|\s/g,'').toUpperCase();
         $('.mac').attr('value' , macval); 
    });       
});