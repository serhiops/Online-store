

const ValidateEmail = text =>
{
    let mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    return Boolean(text.match(mailformat));
}

$(document).ready(()=>{
    $('#newsletter_form').submit((e)=>{
        e.preventDefault();
        let text = $('#newsletter_input').val();
        console.log($('#newsletter_form').attr('action'))
        if(ValidateEmail(text)){
            $.ajax({
                url : $('#newsletter_form').attr('action'),
                type : 'POST',
                data : {
                    'csrfmiddlewaretoken' : getCookie('csrftoken'),
                    'mail' : text,
                },
                success : data =>{
                    data.create ? $('#newsletter_block').remove() : document.getElementById('newsletter_input').value = '';
                    
                    $('#alerts').append(`<div class="alert alert-${data.create ? 'success' : 'primary'}" id="temp_alert_success" role="alert">${data.text}</div>`);
                    setTimeout(()=>{$('#temp_alert_success').remove()}, 10000);
                },
                error : error =>{
                    $('#alerts').append(`<div class="alert alert-danger" id="temp_alert_error" role="alert">Щось пішло не так! Можете повідомити про це адміністратора.</div>`);
                    setTimeout(()=>{$('#temp_alert_error').remove()}, 10000);
                }
            })
        }
        else{
            $('#alerts').append(`<div class="alert alert-danger" id="temp_alert_error_gmail" role="alert">Це не дуже схоже на електронну пошту...</div>`);
            setTimeout(()=>{$('#temp_alert_error_gmail').remove()}, 10000);
            document.getElementById('newsletter_input').value = '';
        }
        window.scrollTo(0, 0);
    })  
})