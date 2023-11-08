try{
  $(document).ready(function() {
    marginLeft = $('#esconde_left').css('margin-left')
    if($('#content_left').css('width') == '0px') {
      $('#esconde_left').addClass('left_bottom');
    }

  
    $('esconde_left').click(function() {
      if($('#content_left').css('width') != '0px') {
        isContentLeftVisible = true;
      } else {
        isContentLeftVisible = false;
      }

      if (isContentLeftVisible) {
        $('#content_left').css('width', '0');
        $('#content_left').css('border-right', '0');
        $('#content_right').css('margin-left', '0');
        $('#pesquisa').css('display', 'none');
        $('#esconde_left').css('margin-left', marginLeft);        
        $('#esconde_left').css('bottom', marginLeft);         
        $('#esconde_left').css('position', 'fixed');
      } else {
        $('#content_left').css('width', '20rem');
        $('#content_left').css('border-right', '');
        $('#content_right').css('margin-left', '');
        $('#pesquisa').css('display', 'inline-block');
        $('#pesquisa').focus();
        $('#esconde_left').css('position', 'static');
      }
  
      isContentLeftVisible = !isContentLeftVisible;
    });

    topoheight = $('#topo').height()
    $('#content_left').css('top', topoheight + 'px');
  });

  window.addEventListener('resize', function() {
    try{  
      var contentLeftElement = document.getElementById('content_left');
      var pesquisaElement = document.getElementById('pesquisa');

      if (window.innerWidth <= 930) {
          contentLeftElement.style.width = '0';
          pesquisaElement.style.display = 'none';
      } else {
          contentLeftElement.style.width = '20rem';
          pesquisaElement.style.display = 'inline-block';}
      } catch(error){
    }
}); } catch(error){
    console.log(error);
}