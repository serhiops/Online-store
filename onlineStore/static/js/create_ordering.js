const  KEY = '8ce1b1742686b544f5c622b7532b49d5'
const URL_POST = 'https://api.novaposhta.ua/v2.0/json/';

const getCookie = name => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            } 
        }
    }
    return cookieValue;
}
$('#checkout_city').on('input', ()=>{
    let text = $('#checkout_city').val();
    if (text.length > 2){
        let data = {
            "apiKey": KEY,
            "modelName": "Address",
            "calledMethod": "searchSettlements",
            "methodProperties": {
                "CityName": text,
                "Limit": "50",
                "Page": "1"
            },
            csrfmiddlewaretoken: getCookie('csrftoken')
        };
    
        fetch(URL_POST, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(data)
        })
            .then(res => { return res.json() })
            .then(( { data } ) => {
                let dataList = $('#cityname');
                data[0].Addresses.forEach(city => {
                    dataList.append(`<option value="${city.Present}">`);
                });
            });
        
            data = {
                "apiKey": KEY,
                "modelName": "Address",
                "calledMethod": "getWarehouses",
                "methodProperties": {
                    "CityName": text,
                    "Page": "1",
                    "Language": "UA",
                },
                csrfmiddlewaretoken: getCookie('csrftoken')
            };

        fetch(URL_POST, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(data)
        })
            .then(res => { return res.json() })
            .then(( { data } ) => {
                let postList = $('#postname');
                data.forEach(postOficce => {
                    postList.append(`<option value='${postOficce.Description}'>`)
                });
            });
            $('#checkout_post').removeAttr('disabled');
    } else {
        $('#checkout_post').attr('disabled', 'disabled');
    }
})