 scrolladjust = () => {
    body_h = document.body.offsetHeight
    window_h = window.innerHeight
    map = document.getElementById("map").getBoundingClientRect()
    if(map['y'] <= 0){
        $('#links').addClass('links_fix') 
        links_h = document.getElementById('links').clientHeight
        $('#topo').css('margin-bottom', links_h + 'px')
        $('#content_left').css('top', links_h + 'px')
        if (body_h <= window_h || body_h - window_h <= 100) {
            extensao = document.getElementById('extensao')
            console.log(!extensao)
            if (!extensao){
                console.log('oi')
                extensao = converthtml(`<div id="extensao" style="height: ${body_h - window_h }px"></div>`)
                $('body').append(extensao)
            }
        } 
    } else {
        $('#links').removeClass('links_fix')
        $('#topo').css('margin-bottom', '0px')
        topoheight = $('#topo').height()
        $('#content_left').css('top', topoheight + 'px')
    }
}

$(window).resize(() => {scrolladjust()})
$(window).scroll(() => {scrolladjust()})
$(document).ready(() => {scrolladjust()})