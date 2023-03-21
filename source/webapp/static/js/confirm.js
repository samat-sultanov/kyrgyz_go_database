async function makeRequest(url, method='GET') {
    let response = await fetch(url, {method});
    if (response.ok) {
        return await response.json();
    } else {
        let error = new Error(response.statusText);
        console.log(error)
        error.response = response;
        throw error;
    }
}
async function ChangeConf(event){
        let url = event.target.dataset.indexLink;
        let pk = event.target.dataset.id
        let response = await makeRequest(url);
        let button_s = document.getElementById(`butt-${pk}`)
        let tb_c = document.getElementById(`status-${pk}`)
        // console.log('response ', response)
        // console.log(button_s)
        if(response.status_res === false){
            button_s.innerText = 'Not confirmed'
            tb_c.innerText = 'Confirmed'
        } else if(response.status_res === true){
            button_s.innerText = 'Confirmed'
            tb_c.innerText = 'Not confirmed'
        }
    }

