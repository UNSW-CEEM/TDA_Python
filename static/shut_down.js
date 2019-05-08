window.onbeforeunload = closingCode;
console.log('loaded shutdown function')
function closingCode(){
   $.ajax({url: '/shutdown', type : 'POST'});
   return null;
}