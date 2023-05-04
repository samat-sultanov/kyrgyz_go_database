function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

async function makeRequest(url, settings) {

    let response = await fetch(url, settings);
    if (response.ok) {  // нормальный ответ
        return response;
    } else {            // ошибка
        let error = new Error(response.statusText);
        error.response = response;
        throw error;
    }
}


async function getRegions(event){
    event.preventDefault();

    let pRegions = document.createElement("p");
    let selectRegion = document.createElement("select");
    selectRegion.setAttribute('name', 'region');
    selectRegion.setAttribute('id', 'id_region');
    pRegions.appendChild(selectRegion);
    pRegions.setAttribute('id', 'region_p_id');

    let pClass = document.getElementById('class_p_id');
    document.body.insertBefore(pRegions, pClass);

    let select = document.getElementById('id_country');
    let selectedCountry = select.options[select.selectedIndex];
    let input = {"country": selectedCountry};

    const settings = {
        method:'POST',
        headers:{
            "Content-Type":"application/json;charset=utf-8",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(input)
    }

    let pCountry = document.getElementById('country_p_id');
    let url = pCountry.dataset['getRegionsLink'];
    let raw_response = await makeRequest(url, settings);
    if (raw_response.ok){
        response = await raw_response.json();
        const entries = Object.entries(response);
        for (let [key, value] of entries){
            let option = document.createElement('option');
            option.innerText = value;
            option.setAttribute('value', key);
            selectRegion.appendChild(option);
        }
    }else if(raw_response.status === 400){
        response = await raw_response.json();
        let formTop = document.getElementsByClassName('form-group')[0];
        let error = document.createElement('h4');
        error.innerText = response.error;
        error.className = "card-title text-bg-danger";
        formTop.appendChild(error);
    }
}


async function getCities(event){
    pass
}


async function onLoad(){
    let selectCountry = document.getElementById('id_country');
    let selectRegion = document.getElementById('id_region');
    selectCountry.onchange = getRegions;
    selectRegion.onchange = getCities;
}

window.addEventListener('load', onLoad);