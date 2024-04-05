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
        path = window.location.pathname
        emp = path.match(/\d+\//g)
        data = {'tipo': tipo, 'val':obj.val()}
        if(obj.val() == ''){} else {
        $.get({url: '/buscadados/' + emp, data,
        success: (res)=>{
            if(res['msg']){
                removedados()
                divinfo = converthtml(`<div id="divinfo">${res['msg']}</div>`)
                div.append(divinfo)
            } else {
                removedados()
            obras = ''
                for(obra of res){
                    obras += `<p class='hover' onclick='mudaobra(this, ${emp}, ${obra['id']}, ${$('#notaid').val()})'>${obra['cod']} - ${obra['nome']}</p>`
                }
                console.log(res)
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
        path = window.location.pathname
        emp = path.match(/\d+\//g)[0].replace(/\//g, '')
        data = {'tipo': tipo, 'val':obj.val()}
        if(obj.val() == ''){} else {
        $.get({url: '/buscadados/' + emp, data,
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
    path = window.location.pathname
    emp = path.match(/\d+\//g)[0].replace(/\//g, '')
    $.get({url:'/alocacao_edit/' + emp, data:{'tipo': 'cadastrar', 'funcid': funcid, 'obraid': obraid},
    success: (res) => {
        if(res['msg']){
            showmsg(res['msg'])
            document.getElementById(`${obraid}`).value = ''
            document.getElementById(`${obraid}`).focus()
        } else{
            funcobj = converthtml(
            `<div>
                <span>${res['cod']} - ${res['nome']}</span><button onclick='deletaaloc(this, ${res['id']}, ${obraid})'><i class="fa-regular fa-circle-xmark"></i></button>
            </div>`
            )
            document.getElementById(`${obraid}`).value = ''
            document.getElementById(`${obraid}`).focus()
            $(prev).after(funcobj)
        }
    }, error: (res) => {
        console.log(res)
    }})
}

deletaaloc = (obj, funcid, obraid) => {
    obj = $(obj)
    prev = obj.prev()
    path = window.location.pathname
    emp = path.match(/\d+\//g)[0].replace(/\//g, '')
    $.get({url:'/alocacao_edit/' + emp, data:{'tipo': 'excluir', 'funcid': funcid, 'obraid': obraid},
    success: (res) => {
        obj.parent()[0].remove() 
    }, error: (res) => {
        console.log(res)
    }})
}


mudaobra = (obj, emp, idobra) => {
    idnota = $('#notaid').val()
    $.get({url:'/alocacao_edit/' + emp, data:{'tipo': 'alteranota', 'idobra': idobra, 'idnota': idnota},
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

semalocacao = ()=> {
    content = $('.accordion-content')
    console.log(content)
    for(a of content){
        a = $(a).find('p')
        if(!a.innerText == 'Nenhuma alocação cadastrada'){
            acc = $(a).parent().parent().parent()
            if (acc.hasClass('hidden')){
                acc.removeClass('hidden') 
            } else {
                acc.addClass('hidden')  
            }   
        } else {      
        }
    }
}
