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
        else if(modalMainButton.dataset.modalType === 'hard_delete_one'){
            modalMainButton.innerText = 'Удалить';
            modalMainButton.setAttribute('class', 'btn btn-danger');
            const form = document.getElementById('modal_form_link');
            const text = document.getElementById('myModalLabel');
            form.setAttribute('action', newsDeleteUrl);
            text.innerText = 'Вы точно хотите безвозвратно удалить эту статью? Статью потом невозможно будет восстановить.';
        }
    }
}

window.addEventListener('load', onLoad);