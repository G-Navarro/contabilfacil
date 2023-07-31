var timer

removedados = () => {
    $('#divinfo').remove()
}

$(document.body).on('click', ()=>{removedados()})

buscadadosobra = (obj, tipo) => {
    obj = $(obj)
    prev = obj.prev()
    div = obj.parent()[0]
    clearTimeout(timer)
    timer = setTimeout(function(){
        data = {'tipo': tipo, 'val':obj.val()}
        if(obj.val() == ''){} else {
        $.get({url: '/buscadados', data,
        success: (res)=>{
            if(res['msg']){
                removedados()
                divinfo = converthtml(`<div id="divinfo">${res['msg']}</div>`)
                div.append(divinfo)
            } else {
                removedados()
            obras = ''
                for(obra of res){
                    obras += `<p class='hover' onclick='mudaobra(this, ${obra['id']}, ${obra['nota']})'>${obra['cod']} - ${obra['nome']}</p>`
                }
                divinfo = converthtml(`<div id="divinfo">${obras}</div>`)
                div.append(divinfo)
        }}, error: (res)=>{
            console.log(res)        
        }})}}, 1000)
}

buscadados = (obj, tipo) => {
    obj = $(obj)
    prev = obj.prev()
    div = obj.parent()[0]
    clearTimeout(timer)
    timer = setTimeout(function(){
        data = {'tipo': tipo, 'val':obj.val()}
        if(obj.val() == ''){} else {
        $.get({url: '/buscadados', data,
        success: (res)=>{
            if(res['msg']){
                removedados()
                divinfo = converthtml(`<div id="divinfo">${res['msg']}</div>`)
                div.append(divinfo)
            } else {
                removedados()
            funcs = ''
                for(func of res){
                    funcs += `<p class='hover' onclick='addaloc(this, ${func['id']}, ${obj.attr("id")})'>${func['nome']}</p>`
                }
                divinfo = converthtml(`<div id="divinfo">${funcs}</div>`)
                div.append(divinfo)
        }}, error: (res)=>{
            console.log(res)        
        }})}}, 1000)
}

addaloc = (obj, funcid, obraid) => {
    obj = $(obj)
    prev = obj.parent().parent()
    input = $($('#divinfo').prev().prev())
    input.val('')
    removedados()
    $.get({url:'/alocacao_edit', data:{'tipo': 'cadastrar', 'funcid': funcid, 'obraid': obraid},
    success: (res) => {
        funcobj = converthtml(
        `<div>
            <span>${res['cod']} - ${res['nome']}</span><button onclick='deletaaloc(this, ${res['id']}, ${obraid})'>Remover</button>
        </div>`
        )
        document.getElementById(`${obraid}`).value = ''
        document.getElementById(`${obraid}`).focus()
        $(prev).after(funcobj)
    }, error: (res) => {
        console.log(res)
    }})
}

deletaaloc = (obj, funcid, obraid) => {
    obj = $(obj)
    prev = obj.prev()
    $.get({url:'/alocacao_edit', data:{'tipo': 'excluir', 'funcid': funcid, 'obraid': obraid},
    success: (res) => {
        obj.parent()[0].remove()
    }, error: (res) => {
        console.log(res)
    }})
}

mudaobra = (obj, idobra) => {
    idnota = $('#id').val()
    $.get({url:'/alocacao_edit', data:{'tipo': 'alteranota', 'idobra': idobra, 'idnota': idnota},
    success: (res) => {
        console.log(res)
        location.reload()
    }, error: (res) => {
        console.log(res)
    }})
}

limpar = (obj) => {
    console.log(obj)
    $(`${obj}`).remove()
}

$(".hover").on('click', function(event){
    event.stopPropagation()
    event.stopImmediatePropagation()
    console.log('ola')
})