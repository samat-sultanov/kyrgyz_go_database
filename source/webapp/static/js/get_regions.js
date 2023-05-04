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

async function deletePRegion(pRegion){
    pRegion.remove();
}

async function setPRegion(){
    let pCountry = document.getElementById('country_p_id');
    let pRegions = document.createElement("p");
    let selectRegion = document.createElement("select");
    pRegions.innerText = 'Регион';
    selectRegion.setAttribute('name', 'region');
    selectRegion.setAttribute('id', 'id_region');
    pRegions.appendChild(selectRegion);
    pRegions.setAttribute('id', 'region_p_id');

    let parent = pCountry.parentNode;
    parent.insertBefore(pRegions, pCountry.nextSibling);
}

async function getRegions(event){
    event.preventDefault();

    let pRegion = document.getElementById("region_p_id");
    if (pRegion){
        await deletePRegion(pRegion);
        await setPRegion();
    }else{
        await setPRegion();
    }

    let pCountry = document.getElementById('country_p_id');

    let select = document.getElementById('id_country');
    let selectedCountry = select.value;
    let input = {"country": selectedCountry};

    const settings = {
        method:'POST',
        headers:{
            "Content-Type":"application/json;charset=utf-8",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(input)
    }

    let url = pCountry.dataset['getRegionsLink'];
    let raw_response = await makeRequest(url, settings);
    if (raw_response.ok){
        response = await raw_response.json();
        const entries = Object.entries(response);
        let selectRegion = document.getElementById("id_region");
        let dummyOption = document.createElement("option");
        dummyOption.innerText = "  -----  ";
        dummyOption.setAttribute('value', '');
        selectRegion.appendChild(dummyOption);

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
    if (selectCountry != null){
        window.console.log(selectCountry);
        selectCountry.onchange = getRegions;
    }
    else {
        window.console.log("couldn't find selectCountry");
    }
}

window.addEventListener('load', onLoad);