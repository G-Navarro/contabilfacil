//apenas um pode ser selecionado
$(document).ready(function() {
    $(".single-check").on("change", "input[type='checkbox']", function() {
        $(this).siblings("input[type='checkbox']").prop("checked", false);
        pesquisa_alvo(this)
    });
});


//function pesquisa_alvo(obj) {
function pesquisa_alvo(obj) {
    let div = $(obj).parents(".filtros")
    let inputs = div.find("input")
    $('.pesquisa_alvo').each(function() {
        element_alvo = this
        text = true
        checkbox = true 
        date = true
        for(input of inputs) {
            class_name = input.className
            campo_alvo = $(element_alvo).find(`.${class_name}`)
            //input text
            if(input.type == 'text'){
                campo_alvo = campo_alvo[0].outerText.toLowerCase()
                inputValue = $(input).val().toLowerCase()
                if (inputValue !== '') {
                    if (campo_alvo.includes(inputValue)) {
                        text = true
                    } else {
                        text = false
                    }
                }
            }

            //input checkbox
            if(input.type == 'checkbox'){
                if(input.checked){
                    if(campo_alvo.length == 1){
                        checkbox = true
                    } else {
                        checkbox = false
                    }
                }
            }
            
            //input date
            if(input.type == 'date'){
                if(input.value != ''){
                    data = $(input).val().split('-')
                    campo_alvo = campo_alvo[0].outerText
                    if (campo_alvo.includes(data[2] + '/' + data[1] + '/' + data[0])) {
                        date = true
                    } else {
                        date = false
                    }
                }
            }
        };

        if(text && checkbox && date) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}