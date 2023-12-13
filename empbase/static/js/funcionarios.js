$('#tiporescisao').on('change', function() {
    tiporescisao = $('#tiporescisao').val()
    if (tiporescisao == 'TERM' || tiporescisao == 'TERANT') {
        $('#avisodemissao').val('');
        $('#avisodemissao').prop('disabled', true);
        $('#tipoaviso').prop('disabled', true);
        $('#datademissao').prop('disabled', false);
    } else {        
        $('#tipoaviso').prop('disabled', false);
    }
    if (tiporescisao == 'DSJ') {
        $('#tiporeducao').prop('disabled', false);
    } else {
        $('#tiporeducao').prop('disabled', true);
    }
})

$('#tipoaviso').on('change', function() {
    tipoaviso = $('#tipoaviso').val()
    if (tipoaviso == 'Indenizado' || tipoaviso == 'Dispensado') {
        $('#tiporeducao').prop('disabled', true);
        $('#avisodemissao').val('');
        $('#avisodemissao').prop('disabled', true);
        $('#datademissao').prop('readonly', false);
    } else {
        if ($('#tiporescisao').val() == '2') {
            $('#tiporeducao').prop('disabled', false);
        }
        $('#avisodemissao').prop('disabled', false);
        $('#datademissao').prop('readonly', true);
    }
})

$('#avisodemissao').on('input', function() {
    clearTimeout(timer)
    timer = setTimeout(function(){
        aviso = new Date($('#avisodemissao').val())
        final = new Date(aviso.setDate(aviso.getDate() + 30))
        $('#datademissao').val(final.toISOString().split('T')[0])
    }, 500)
  });

$('#inicioferias').on('input', function() {
    clearTimeout(timer)
    timer = setTimeout(function(){
        data = $('#inicioferias').val().split('-')
        datamaxima = $('#datamaxima').val()
        aviso = new Date(data[0], data[1] - 1, data[2], 12, 0, 0)
        inicio = new Date(data[0], data[1] - 1, data[2], 12, 0, 0)
        final = new Date(data[0], data[1] - 1, data[2], 12, 0, 0)
        diadasemana = inicio.getDay()
        aviso = new Date(aviso.setDate(aviso.getDate() - 30))
        final = new Date(final.setDate(final.getDate() + parseInt($('#diasdedireito').val())))
        console.log(datamaxima, $('#inicioferias').val())
        if (datamaxima < $('#inicioferias').val()){
            showmsg('A data de início não pode ser maior que a data máxima')
        } else{
            if (diadasemana === 1 || diadasemana === 2 || diadasemana === 3) {
                $('#avisoferias').val(aviso.toISOString().split('T')[0]);
                $('#fimferias').val(final.toISOString().split('T')[0]);
            } else {
                $('#avisoferias').val('');
                $('#fimferias').val('');
                showmsg('As férias devem iniciar Segunda, Terça ou Quarta-feira')
        }}}, 500)
  });

  $('#faltaate').on('input', function() {
    clearTimeout(timer)
    timer = setTimeout(function(){
    falta = $('#falta').val()
    faltaate = $('#faltaate').val()
    if (falta > faltaate){
        showmsg('Falta maior que a falta final')
    }
    }, 500)})

