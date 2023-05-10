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

async function deletePCity(pCity){
    pCity.remove();
}

async function setPCity(){
    let divRegions = document.getElementById('region_p_id');
    let divCities = document.createElement("div");
    divCities.setAttribute('class', 'form-row');
    divCities.setAttribute('id', 'city_p_id');

    let divLabelCity = document.createElement("div");
    let pLabelCity = document.createElement("p");
    divLabelCity.setAttribute('class', 'form-label-col');
    pLabelCity.setAttribute('class', 'form-label');
    pLabelCity.innerText = 'Город: ';
    divLabelCity.appendChild(pLabelCity);
    divCities.appendChild(divLabelCity);

    let divValueCity = document.createElement("div");
    divValueCity.setAttribute('class', 'form-value-col');
    let pValueCity = document.createElement("p");
    pValueCity.setAttribute('class', 'form-value');
    let selectCity = document.createElement("select");
    selectCity.setAttribute('name', 'city');
    selectCity.setAttribute('id', 'id_city');
    pValueCity.appendChild(selectCity);
    divValueCity.appendChild(pValueCity);
    divCities.appendChild(divValueCity);

    let parent = divRegions.parentNode;
    parent.insertBefore(divCities, divRegions.nextSibling);
}

async function getCities(event){
    let pCity = document.getElementById("city_p_id");
    if (pCity){
        await deletePCity(pCity);
        await setPCity();
    }else{
        await setPCity();
    }

    let pCountry = document.getElementById('country_p_id');
    let select = document.getElementById('id_country');
    let selectedCountry = select.value;

    let pRegion = document.getElementById('region_p_id');
    let selectRegion = document.getElementById('id_region');
    let selectedRegion = selectRegion.value;

    let inputs = {"country": selectedCountry, "region": selectedRegion};

    const settings = {
        method:'POST',
        headers:{
            "Content-Type":"application/json;charset=utf-8",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(inputs)
    }

    let url = pRegion.dataset['getCitiesLink'];
    let raw_response = await makeRequest(url, settings);
    if (raw_response.ok){
        response = await raw_response.json();
        const entries = Object.entries(response);
        let selectCity = document.getElementById("id_city");
        let dummyOption = document.createElement("option");
        dummyOption.innerText = "  -----  ";
        dummyOption.setAttribute('value', '');
        selectCity.appendChild(dummyOption);

        for (let [key, value] of entries){
            let option = document.createElement('option');
            option.innerText = value;
            option.setAttribute('value', key);
            selectCity.appendChild(option);
        }
    }else if(raw_response.status === 400){
        response = await raw_response.json();
        let formTop = document.getElementsByClassName('form-group')[0];
        let error = document.createElement('h4');
        error.innerText = response.error;
        error.className = "text-bg-danger";
        formTop.appendChild(error);
    }
}

async function setPRegion(){
    let divCountry = document.getElementById('country_p_id');
    let divRegions = document.createElement("div");
    divRegions.setAttribute('id', 'region_p_id');
    divRegions.setAttribute('data-get-cities-link', `/api/v1/get_cities/`);
    divRegions.setAttribute('class', 'form-row');

    let divLabelRegions = document.createElement('div');
    divLabelRegions.setAttribute('class', 'form-label-col');
    let pLabelRegions = document.createElement('p');
    pLabelRegions.setAttribute('class', 'form-label');
    pLabelRegions.innerText = 'Регион: ';
    divLabelRegions.appendChild(pLabelRegions);
    divRegions.appendChild(divLabelRegions);

    let divValueRegions = document.createElement('div');
    divValueRegions.setAttribute('class', 'form-value-col');
    let pValueRegions = document.createElement('p');
    pValueRegions.setAttribute('class', 'form-value');
    let selectRegion = document.createElement("select");
    selectRegion.setAttribute('name', 'region');
    selectRegion.setAttribute('id', 'id_region');
    selectRegion.setAttribute('onchange', 'getCities()');
    pValueRegions.appendChild(selectRegion);
    divValueRegions.appendChild(pValueRegions);
    divRegions.appendChild(divValueRegions);

    let parent = divCountry.parentNode;
    parent.insertBefore(divRegions, divCountry.nextSibling);
}

async function getRegions(event){
    event.preventDefault();

    let pRegion = document.getElementById("region_p_id");
    if (pRegion){
        await deletePRegion(pRegion);
        let pCity = document.getElementById("city_p_id");
        if (pCity){await deletePCity(pCity);}
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
        error.className = "text-bg-danger";
        formTop.appendChild(error);
    }
}


async function onLoad(){
    let selectCountry = document.getElementById('id_country');
    if (selectCountry != null){
        selectCountry.onchange = getRegions;
    }
    else {
        window.console.log("couldn't find selectCountry");
    }
}

window.addEventListener('load', onLoad);