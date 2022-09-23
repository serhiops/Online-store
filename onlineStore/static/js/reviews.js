$(document).ready(()=>{    
    $('#comentForm').submit((e)=>{
        e.preventDefault();
        text = $('#comentTextarea').val();
        productId = $('#productId').val();
        $.ajax({
            type : 'POST',
            url : $('#comentForm').attr('acttion'),
            data : {
                'csrfmiddlewaretoken' : getCookie('csrftoken'),
                'text' : text,
                'productId' : productId,
                'type' : 'CREATE'
            },
            success : data =>{
                console.log(data);
                $('#comentTextarea').val('')
                if (data.created && data.success){
                    $('#comentList').prepend(
                        `<div class="card reviews-cart" id="authorsCard" >
                        <div class="card-header">
                            <div style="float:left">Щойно створено</div>
                            <div style="float:right" class="btn-group" id="buttonGroup">
                                <button type="button" class="btn btn-success" onclick="changeButton()" id="changeButton">Редагувати</button>
                                <button type="button" class="btn btn-danger" onclick="deleteButton()" id="deleteButton">Видалити</button>
                            </div>
                        </div>
                        <div class="card-body">
                            <blockquote class="blockquote mb-0" id="authorsBlock">
                                <p>${ text }</p>
                            </blockquote>
                        </div>
                    </div>`
                    );
                    console.log('asddas');
                }
            },
            error : error =>{ console.log(error); }
        });
    });
})

const changeButton = ()=>{
    let changeButton = $('#changeButton');
    changeButton.text('Зберегти');
    changeButton.attr({ id : 'saveButton', onclick : 'saveButton()' });

    let deleteButton = $('#deleteButton');
    deleteButton.text('Назад');
    deleteButton.attr({ id : 'backButton', onclick : 'backButton()' });

    let textBlock = $('#authorsBlock>p:first');
    let prevText = textBlock.text();
    textBlock.remove();
    $('#authorsBlock').append(`<input type="text" class="form-control" style="color:black;" value="${prevText}">`);
}

const saveButton = ()=>{
    let changeInput = $('#authorsBlock>input:first');
    let text = changeInput.val();
    $.ajax({
        type : 'POST',
        url : $('#comentForm').attr('acttion'),
        data : {
            'csrfmiddlewaretoken' : getCookie('csrftoken'),
            'text' : text,
            'productId' : $('#productId').val(),
            'type' : 'UPDATE'
        },
        success : data =>{
            resetButton()
            let changeInput = $('#authorsBlock>input:first');
            let text = changeInput.val();
            changeInput.remove();
            $('#authorsBlock').append(`<p>${ text }</p>`);
        },
        error : error =>{
            console.log(data);
        }
    });

}

const deleteButton = ()=>{ 
    $.ajax({
        type : 'POST',
        url : $('#comentForm').attr('acttion'),
        data : {
            'csrfmiddlewaretoken' : getCookie('csrftoken'),
            'productId' : $('#productId').val(),
            'type' : 'DELETE',
        },
        success : data =>{
            $('#authorsCard').remove();
        },
        error : error =>{

        }
    });
}

const backButton = ()=>{
    resetButton()
    let changeInput = $('#authorsBlock>input:first');
    $.ajax({
        type : 'GET',
        url : $('#comentForm').attr('acttion'),
        data : {
            'productId' : $('#productId').val(),
        },
        success : data =>{
            changeInput.remove();
            $('#authorsBlock').append(`<p>${JSON.parse(data.review).fields.text}</p>`);
        },
        error : error =>{
            changeInput.remove();
            let text = changeInput.val();
            $('#authorsBlock').append(`<p>${ text }</p>`);
        }
    });
}

const resetButton = ()=>{
    let changeButton = $('#saveButton');
    changeButton.text('Редагувати');
    changeButton.attr({ id : 'changeButton', onclick : 'changeButton()' });

    let deleteButton = $('#backButton');
    deleteButton.text('Видалити');
    deleteButton.attr({ id : 'deleteButton', onclick : 'deleteButton()' });
} 