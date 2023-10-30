 scrolladjust = () => {
    map = document.getElementById("map").getBoundingClientRect()
    if(map['y'] <= 0){
        $('#links').addClass('links_fix') 
        links_h = document.getElementById('links').clientHeight
        $('#topo').css('margin-bottom', links_h + 'px')
        $('#content_left').css('top', links_h + 'px')
    } else {
        $('#links').removeClass('links_fix')
        $('#topo').css('margin-bottom', '0px')
        topoheight = $('#topo').height()
        $('#content_left').css('top', topoheight + 'px')
    }
}

$(window).scroll(() => {scrolladjust()})
$(document).ready(() => {scrolladjust()})