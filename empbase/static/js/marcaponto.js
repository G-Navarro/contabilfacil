function marcaponto(obj) {    
  event.preventDefault();
  obj = $(obj)
  tipo = obj.attr('id').split('_');
  horario = $('#dia_hora').val()
  diainicio = $('#datainicio').val()

  //checa se é data futura
  agora = new Date()
  hora = agora.toTimeString().slice(0, 5)
  data = agora.toLocaleDateString().split('/')
  data = data[2] + '-' + data[1] + '-' + data[0]
  agora_formatado = data + 'T' + hora
  console.log(horario, agora_formatado)
  if (horario > agora_formatado){
    alert('Data e hora não pode ser maior que agora')
  } else {
    // Define the object mapping for column indexes
    var columnIndexes = {
      'entrada': 1,
      'intervalo': 2,
      'fimintervalo': 3,
      'saida': 4
    };

    // Get the column index based on the "tipo" value
    var columnIndex = columnIndexes[tipo[1]];
    event.preventDefault();
    $.post({
      url: 'ponto',
      type: 'POST',
      headers: { 'X-CSRFToken': csrftoken },
      data: {'tipo': tipo[1], 'horario': horario, 'datainicio': diainicio },
      success: function(response) {
        console.log(response);
        if('msg' in response){
          msg = $('#msg')
          msg.text(response.msg)
          msg.show()
          $(document).ready(function() {
            setTimeout(function() {
              msg.hide()
            }, 3000);
          });
        } else {
          obj.addClass('btn-green')
          obj.prop('disabled', true)
          // Retrieve the received "dia" and "hora" values from the response
          var dia = response.dia;
          var hora = response.hora;
          console.log('ola', dia, hora)
          $('#' + dia).find("td:eq(" + columnIndex + ")").text(hora)
        }
      },
      error: function(error) {
        // Handle any errors
        console.log(error);
      }
  });}
}

function isValidDateTime(dateTimeString) {
  // Regex pattern to match 'yyyy-mm-ddThh:mm'
  var regexPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;

  // Check if the format matches the expected pattern
  if (!regexPattern.test(dateTimeString)) {
    return false;
  }

  // Create a Date object from the dateTimeString
  var dateObj = new Date(dateTimeString);

  // Check if the Date object represents a valid date and time
  if (isNaN(dateObj.getTime())) {
    return false;
  }

  // Check if the time component is a valid time
  var hours = dateObj.getHours();
  var minutes = dateObj.getMinutes();
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
    return false;
  }

  // Return true if the dateTimeString is a valid date and time
  return true;
}

try{
  datainicio = $('#datainicio')
  dia_hora = $('#dia_hora')
  agora = new Date()
  hora = agora.toTimeString().slice(0, 5)
  data = agora.toLocaleDateString().split('/')
  data = data[2] + '-' + data[1] + '-' + data[0]
  if (data > datainicio.val()){ 
    dia_hora.val(datainicio.val() + 'T' + hora)
    console.log(data, datainicio)
  } else {
    dia_hora.val(data + 'T' + hora)
  }
  } catch(e){
    console.log(e)
  }

$('#retificarponto').hover(()=> {
  datainicio = $('#inicioem').val()
  entrada = $('#entrada').val()
  intervalo = $('#intervalo').val()
  fimintervalo = $('#fimintervalo').val()
  saida = $('#saida').val()

  entradah = entrada.substring(11,16)
  intervaloh = intervalo.substring(11,16)
  fimintervaloh = fimintervalo.substring(11,16)
  saidah = saida.substring(11,16)
  $("#retificarponto").prop('disabled', true);
  if (entrada.slice(0, 10) > datainicio) {
    showmsg('Entrada não pode ser maior que a data de início');
  }
  else if (entrada.slice(0, 10) < datainicio) {
    showmsg('Entrada não pode ser menor que a data de início');
  }
  else if (entrada > saida && saidah != '00:00') {
    showmsg('Entrada não pode ser maior que a saída');
  }
  else if (entrada < saida && saidah == '00:00') {
    showmsg('Hora da saída não pode ser 00:00');
  }
  else if (entrada > intervalo && intervalo != fimintervalo) {
    showmsg('Entrada não pode ser maior que o início do intervalo'); 
  } 
  else if (intervalo > fimintervalo && fimintervaloh != '00:00') {
    showmsg('Início intervalo não pode ser maior que o fim do intervalo');
  }
  else if (fimintervalo > saida && saidah != '00:00') {
    showmsg('Fim do intervalo não pode ser maior que a saída ');
  } else {
    $("#retificarponto").prop('disabled', false);
  }})
  /*if (entradah == '00:00' && intervaloh == '00:00' && fimintervaloh == '00:00' && saidah == '00:00' || saida == '') {
    event.preventDefault();
    alert('Todos os campos estão vazios');
  }*/

  marca_falta = () => {
    loading = converthtml("<div id=blackout><span class='loader'></span></div>")
    $('body').append(loading)
    func = $('#funcid').val()
    falta = $('#datafalta').val()
    data = {'tipo': 'falta', 'funcid':func, 'falta':falta,}
    $.post({url: '/ponto', headers: {'X-CSRFToken': csrftoken}, data,
      success: (res)=>{
        if(res['status'] == 'ok'){
          location.reload()
        }
      }, error: (res)=>{
        console.log(res)
    }})}

  marca_folga = () => {
    loading = converthtml("<div id=blackout><span class='loader'></span></div>")
    $('body').append(loading)
    func = $('#funcid').val()
    folga = $('#datafalta').val()
    data = {'tipo': 'falta', 'funcid':func, 'falta':falta,}
    $.post({url: '/ponto', headers: {'X-CSRFToken': csrftoken}, data,
      success: (res)=>{
        if(res['status'] == 'ok'){
          location.reload()
        }
      }, error: (res)=>{
        console.log(res)
    }})}

excluir_lancamento = (lancid) => {
  data = {'tipo': 'excluir_lanc', 'funcid':$('#funcid').val(), 'lancid':lancid,}
  $.post({url: '/ponto', headers: {'X-CSRFToken': csrftoken}, data,
    success: (res)=>{
      if(res['status'] == 'ok'){
        location.reload()
      }
    }, error: (res)=>{
      console.log(res)
  }})}
