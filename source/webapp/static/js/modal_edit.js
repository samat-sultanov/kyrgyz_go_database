async function onLoad(){
    let modalMainButton = document.getElementById('kgf_modal');
    if (modalMainButton){
        if (modalMainButton.dataset.modalType === 'delete_news'){
            modalMainButton.innerText = 'Удалить';
            modalMainButton.setAttribute('class', 'btn btn-danger');
            const form = document.getElementById('modal_form_link');
            const text = document.getElementById('myModalLabel');
            form.setAttribute('action', newsDeleteUrl);
            text.innerText = 'Вы точно хотите удалить эту статью?';
        }
    }
}

window.addEventListener('load', onLoad);