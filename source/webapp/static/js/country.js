const base_url = 'https://restcountries.com/v3.1/all';

function makeRequest(url, method='GET') {
    return new Promise(function(resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.onload = function() {
            if (this.status === 200) resolve(this.response);
            else reject(this);
            req = this.responseText;
            JsonFile = JSON.parse(req);
            // console.log(JsonFile)
        };
        xhr.open(method, url);
        xhr.send();
    });
}

async function Flags() {
    let current = await makeRequest(base_url)
    let countries = JSON.parse(current);
    country_code = document.getElementById('country_code')
    flag = document.getElementById('flag')
    let code_c =  country_code.textContent
    let count_country = countries.length
    // console.log(count_country)
    for (let i=0; i<count_country; i++){
        if(countries[i].cca2.toLowerCase() === code_c.toLowerCase()){
            flag.innerHTML = `<img class="card-img-top" alt="..." style="width: 60%;border-radius: 8px;" 
            id="flag-img" src="${countries[i].flags.png}">` + `<p>${countries[i].name.common}</p>`
        }
    }
}

Flags()