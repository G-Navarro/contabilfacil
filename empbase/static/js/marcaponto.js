


function marcaponto(obj) {
  var funcid = $(obj).attr('id');
  var tipo = $(obj).text().toLowerCase().replace(/\s/g, '');

  // Define the object mapping for column indexes
  var columnIndexes = {
    'entrada': 1,
    'intervalo': 2,
    'fimintervalo': 3,
    'saida': 4
  };

  // Get the column index based on the "tipo" value
  var columnIndex = columnIndexes[tipo];

  $.post({
    url: 'ponto',
    type: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    data: { 'funcid': funcid, 'tipo': tipo},
    success: function(response) {
      if('msg' in response){
        console.log(response.msg)
      } else {
      // Retrieve the received "dia" and "hora" values from the response
      var dia = response.dia;
      var hora = response.hora;
      // Iterate over the table rows
      $('#tabelaponto tr').each(function() {
        var firstColumnValue = $(this).find('td:first').text();
        // Check if the first column value matches "dia"
        if (firstColumnValue === dia) {
          // Update the value of the corresponding column to "hora"
          $(this).find('td:eq(' + columnIndex + ')').text(hora);
        }
      });}
    },
    error: function(error) {
      // Handle any errors
      console.log(error);
    }
  });
}


  