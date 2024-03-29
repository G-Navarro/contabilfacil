dropArea = $('#dragNdrop')
divdropArea = $(dropArea.first())
labelfile = $('#arquivo')

divdropArea.on("dragover", function(event) {
    event.preventDefault();
    event.stopPropagation();
    dropArea.addClass("hover");
});

divdropArea.on("dragleave", function(event) {
    event.preventDefault();
    event.stopPropagation();
    dropArea.removeClass("hover");
});

processaarquivo = () => {
    currentUrl = window.location.href
    pattern = /\b\d{2}-\d{2}\b/g
    comp = currentUrl.match(pattern)
    url='/cadastrar?comp=' + comp
    loading = converthtml("<div id=blackout><span class='loader'></span></div>")
    $('body').append(loading) 
    divdropArea.append(loading)
    inputfile = $('#arquivo')
    inputfile = inputfile[0].files[0]
    form = new FormData();
    form.append('arquivo', inputfile)
    form.append('modelo', $('#modelo').val())
    form.append('comp', comp)
    $.post({url, headers: {'X-CSRFToken': csrftoken}, data: form, processData: false, contentType: false,
    success: (res)=>{
        if(res['msg'] == 'sucesso'){
            origin = window.location.origin 
            window.location.href = origin + res['redirect'];
        }
    }, error: (res)=>{
        console.log(res)
    }})
}

deleta_imposto = (id) => {
    const urlsplit = window.location.href.split('/')
    console.log(currentUrl);
    $.post({url: '/tarefas', headers: {'X-CSRFToken': csrftoken}, data: {'deletar': id }, 
    success: (res)=>{
        if(res['msg'] == 'sucesso'){
            location.reload()
        }
    }, error: (res)=>{
        console.log(res)
    }})
}

divdropArea.on("drop", function(event) {
    event.preventDefault();
    event.stopPropagation();
    dropArea.removeClass("hover");

    files = event.originalEvent.dataTransfer.files[0];
    console.log(files)
    inputfile = $('#arquivo')[0]
    dataTransfer = new DataTransfer()
    dataTransfer.items.add(files)
    inputfile.files = dataTransfer.files
    processaarquivo()
});

$('#arquivo').on('change', processaarquivo)