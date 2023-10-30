function converthtml(elementhtml){
    const parser = new DOMParser();
    const html = parser.parseFromString(elementhtml, 'text/html')
    return html.body.firstChild
};

try {
    phone = document.getElementById('fone')

    function formatofone(){
        num = phone.value.replace(/\D/g, '')
        if (num.length >= 3){
            ddd = '(' + num.slice(0,2) + ') '
            numcompleto = ddd + num.slice(2,) 
        
            if (num.length >= 7){
                numero = num.slice(2,)
                num1 = numero.slice(0,4) + '-'
                num2 = numero.slice(4,)
                numcompleto = ddd + num1 + num2
            }
    
            if (num.length > 10){
                numero = num.slice(2,)
                num1 = numero.slice(0,5) + '-'
                num2 = numero.slice(5,)
                numcompleto = ddd + num1 + num2
            }
    
            phone.value = numcompleto
        }
    };
    formatofone()
    phone.addEventListener("input", formatofone)

    } catch(erro) {
    
}

function formatInputValue(input) {
    valor = input.value.replace(/\D/g, '')
    if(valor.length >= 3){
        decimal = ',' + valor.slice(-2,)
        valorcompleto = valor.slice(0,-2) + decimal 
        input.value = valorcompleto
    }
  
    input.value = `${integerPart}${decimalPart}`;
}

function upperCase(obj) {
    obj.value = obj.value.toUpperCase();
  }

try{
    senhamostra = document.getElementById('senhamostra')
    senhamostra.addEventListener('click', mostrarsenha)
} catch(erro) {
}

function mostrarsenha() {
    x = document.getElementById("senha")
    if (x.type === "password") {
      x.type = "text"
      senhamostra.classList.remove("fa-eye")
      senhamostra.classList.add("fa-eye-slash")
    } else {
      x.type = "password"
      senhamostra.classList.remove("fa-eye-slash")
      senhamostra.classList.add("fa-eye")
    }
  }

$('.accordion-main').click(
(e) => {
    parent = $(e.target).parents('.accordion')
    pcontent = parent.find('.accordion-content')
    objheight = pcontent.height()
    if (pcontent.is( ":hidden" )){
        accordionc = $('.accordion-content')
        for(obj of accordionc){
            //$(obj).addClass('hidden')            
            $(obj).slideUp()
        }     
        //pcontent.css('height', '0px')
        //pcontent.removeClass('hidden')
        pcontent.show('fast')
        //pcontent.animate({height:`${objheight}px`})
    } else {
        pcontent.slideUp()
        //pcontent.addClass('hidden')
    }})

$('.abasmenu').click(
    (e)=>{
        p = $(e.target).index()
        abasmenu = $('.abasmenu')
        abas = $('.abas')
        console.log(abasmenu)
        console.log(abas)
        for(i = 0; i < abasmenu.length; i++){
            $(abasmenu[i]).removeClass('abaativa')
            $(abas[i]).addClass('hidden')
        }
        $(abasmenu[p]).addClass('abaativa')
        $(abas[p]).removeClass('hidden')
})


$('#teste').on('click',()=>{
    if($('#dragNdrop').hasClass('height100')){
        $('#dragNdrop').removeClass('height100')
    } else {
        $('#dragNdrop').addClass('height100')
    }
})

alterastatus = (obj, status, tr, fl) => {    
    obj = $(obj)
    i = obj.find('i')
    $(i).remove()
    if(status == true){
        i = converthtml(tr)
        obj.append(i)
        obj.removeClass('cdanger')
        obj.addClass('csuccess')
    } else if(status == false){            
        i = converthtml(fl)
        obj.append(i)
        obj.removeClass('csuccess')
        obj.addClass('cdanger')
    }
}

tramite = (obj, emp) => {
    url = '/tramite_altera'
    data = { 'tramite': $(obj).attr('id'), 'emp': emp }
    $.post({
        url: url,
        headers: { 'X-CSRFToken': csrftoken },
        data: data,
        success: (res) => {
            if ('status' in res) {
                alterastatus(obj, res['status'], '<i class="fa-solid fa-check"></i>', '<i class="fa-solid fa-xmark"></i>')
            }
        }, error: (res) => {
            console.log(res);
        }
})}

const postData = (url, csrftoken, data, obj, tr, fl) => {
    $.post({
      url: url,
      headers: { 'X-CSRFToken': csrftoken },
      data: data,
      success: (res) => {
        obj = $(obj)
        i = obj.find('i')
        $(i).remove()
        if(res['status'] == true){
            i = converthtml(tr)
            obj.append(i)
            obj.removeClass('cdanger')
            obj.addClass('csuccess')
        } else if(res['status'] == false){            
            i = converthtml(fl)
            obj.append(i)
            obj.removeClass('csuccess')
            obj.addClass('cdanger')
        }
      },
      error: (res) => {
        console.log(res);
      }
    });
};

imposto_pago = (obj) => {
const data = { 'imposto': $(obj).attr('id') };
postData('impostos', csrftoken, data, obj, '<i class="fa-solid fa-file-circle-check"></i>', '<i class="fa-solid fa-file-circle-xmark"></i>');
};

enviado = (obj) => {
const data = { 'imposto': $(obj).attr('id') };
postData('tarefas', csrftoken, data, obj, '<i class="fa-solid fa-check"></i>', '<i class="fa-regular fa-paper-plane"></i>');
};

holerite = (obj) => {
const data = { 'holerite': $(obj).attr('id') };
postData('tarefas', csrftoken, data, obj, '<i class="fa-solid fa-check"></i>', '<i class="fa-regular fa-paper-plane"></i>');
};

pagamento = (obj) => {
const data = { 'pagamento': $(obj).attr('id') };
postData('pagamentos', csrftoken, data, obj, '<i class="fa-solid fa-hand-holding-dollar"></i>', '<i class="fa-solid fa-money-check-dollar"></i>');
};

bloqueiauser = (obj) => {
const data = { 'bloqueiauser': $(obj).attr('id') };
postData('usuarios', csrftoken, data, obj, '<i class="fa-solid fa-check"></i>', '<i class="fa-solid fa-ban"></i>');
};

itemstatus = (obj, tipo) => {
    data = {info:{}}
    if(tipo == 'imposto'){
        data = {'imposto': $(obj).attr('id')}
        tr = '<i class="fa-solid fa-check"></i>'
        fl = '<i class="fa-regular fa-paper-plane"></i>'
    }
    if(tipo == 'holerite'){
        data = {'holerite': $(obj).attr('id')}
        tr = '<i class="fa-solid fa-check"></i>'
        fl = '<i class="fa-regular fa-paper-plane"></i>'
    }
    if(tipo == 'pagamento'){
        data.info = {'pagamento': $(obj).attr('id')}
        tr = '<i class="fa-solid fa-hand-holding-dollar"></i>'
        fl = '<i class="fa-solid fa-money-check-dollar"></i>'
    }
    $.post({url:'tarefas', headers:{'X-CSRFToken': csrftoken}, data:data, 
    success: (res) => {
        alterastatus(obj, res['status'], tr, fl)
    }, error: (res) => {
        console.log(res)
    }})
}

removefundo = () => {
    $("#fundo").remove()
    for(formdisplay of $(".formdisplay")){
        $(formdisplay).addClass('hidden')
    }
}

mostrar = (obj) => {
    next = $(obj).next()
    next.removeClass('hidden')
    $(document.body).append(converthtml('<div id="fundo"></div>'))
    $('#fundo').click(() => {
        removefundo()
    })
}

alteracomp = () => {
    comp_month = $('#comp_month').val()
    comp_year = $('#comp_year').val()
    console.log(comp_month)
    console.log(comp_year)
    $.post({url:'/empresas', headers:{'X-CSRFToken': csrftoken}, data:{'comp':`${comp_year}-${comp_month}`}, 
    success: (res) => {
        if(res['msg'] == 'sucesso'){
            location.reload()
        }
    }, error: (res) => {
        console.log(res)
    }})

}

adcionaacesso = (obj, id) => {
    val = $(obj).val()
    $.post({url:'/usuarios', headers:{'X-CSRFToken': csrftoken}, data:{'val_add':val, 'userid':id}, 
    success: (res) => {
        if(res['msg'] == 'sucesso'){
            document.getElementById('temacessos').innerHTML = ''
            emp = converthtml(res['emp'])
            $('#temacessos').append(emp)
        }
    }, error: (res) => {
        console.log(res)
    }})
}

userexiste = (obj) => {
    clearTimeout(timer)
    timer = setTimeout(function(){
    nome = $(obj).val()
    if(nome == ''){
        parent = $(obj).parent()
        iexiste = $(parent).find('i')
        $(iexiste).remove()
        $(obj).css('border-bottom-color', '#0ab4b4')
        $('#btnsubmit').css('display', 'inline-block')
    } else {
        $.get({url:'usuarios', data:{'nome_user': nome},
        success: (res) => {
            parent = $(obj).parent()
            iexiste = $(parent).find('i')
            $(iexiste).remove()
            if(res['msg'] == 'n_existe'){
                i = converthtml('<i class="fa-solid fa-check" style="color:#00E673"></i>')
                $(obj).css('border-bottom-color', '#0ab4b4')
                $(parent).append(i)
                $('#btnsubmit').css('display', 'inline-block')
            } if(res['msg'] == 'existe'){            
                i = converthtml('<i class="fa-solid fa-triangle-exclamation" style="color:#ff6666"></i>')
                $(obj).css('border-bottom-color', '#ff6666')
                $(parent).append(i)            
                $('#btnsubmit').css('display', 'none')
            }
        }, error: (res) => {
            console.log(res)
        }})
    }}, 1000)
}


function pesquisa(obj, id) {
    var input = $(obj).val().toLowerCase();
    $('#'+id+' a').each(function() {
        var text = $(this).text().toLowerCase();
        if (input === '') {
            $(this).show();
            $('#resultado_pesquisa').hide()
        } else if (text.indexOf(input) > -1) {
            $(this).show();
            $('#resultado_pesquisa').show()
        } else {
            $(this).hide();
        }
    });
}

showmenu = ()=> {
    height = $('#links').height()
    toplinks = document.getElementById("links").getBoundingClientRect()['y']
    console.log(toplinks + height)
    if ($('#conteudomenu').css('display') == 'none'){
        $('#conteudomenu').css('display', 'block')
        $('#conteudomenu').css('top', toplinks + 46.78 + 'px')
    } else {
        $('#conteudomenu').css('display', 'none')
        $('#conteudomenu').css('top', toplinks + 46.78 + 'px')
    }
}

showmsg = (msg) => {
    msg = converthtml(`<div id="msg">${msg}</div>`)
    console.log(msg)
    $('body').append(msg)
    $('#msg').css('display', 'block')
    setTimeout(function() {
    $('#msg').remove()
    }, 3000);
    
}

acho = (id) => {$(`#${id}`).removeClass('hidden')}
alakazam = (id) => {
    $(id).toggle()
    fundo = converthtml(`<div id="fundo"></div>`)
    $('body').append(fundo)
    $('#fundo').click(() => {
        $(id).toggle()
        removefundo()
    })
}