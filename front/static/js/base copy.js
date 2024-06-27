// const domEl = 

// const addOnClickEvent = domEl => {

// }


// document.addEventListener('DOMContentLoaded', (event) => {
//     const token = localStorage.getItem('access_token');
//     if (token) {
//         document.querySelectorAll('a').forEach(domEl => addOnClickEvent(domEl))
//         domEl.addEventListener('click', (event) => {
//             event.preventDefault();
//             const url = event.target.href;
//             console.log("url", url)

//             fetch(url, {
//                 method: 'GET',
//                 headers: new Headers({
//                     'Authorization': `Bearer ${token}`,
//                 })
//             })
//                 .then(response => response.text())
//                 .then(html => {
//                     // Обновление содержимого страницы
//                     document.body.innerHTML = html;
//                     // window.history.pushState({}, '', url);
//                     window.location.reload();
//                 })
//                 .catch(error => console.error('Error:', error));


//         })
//     }

// })

// document.addEventListener('DOMContentLoaded', (event) => {
//     // document.addEventListener('document', (event) => {
//     const token = localStorage.getItem('access_token');
//     console.log(token)

//     if (token) {
//         // Перехват всех кликов по ссылкам
//         document.querySelectorAll('a').forEach(link => {
//             // console.log("add event to link")
//             console.log("link:", link)
//             link.addEventListener('click', (event) => {
//                 event.preventDefault();
//                 const url = event.target.href;
//                 console.log("url", url)

//                 fetch(url, {
//                     method: 'GET',
//                     headers: new Headers({
//                         'Authorization': `Bearer ${token}`,
//                     })
//                 })
//                     .then(response => response.text())
//                     .then(html => {
//                         // Обновление содержимого страницы
//                         document.body.innerHTML = html;
//                         window.history.pushState({}, '', url);
//                         // window.location.reload();

//                     })
//                     .catch(error => console.error('Error:', error));
//             });
//         });
//     }
// });

function fetchAndReplaceContent(url) {
    const token = localStorage.getItem('access_token');
    fetch(url, {
        method: 'GET',
        headers: new Headers({
            'Authorization': `Bearer ${token}`,
        })
    })
        .then(response => response.text())
        .then(html => {
            document.body.innerHTML = html;
            window.history.pushState({}, '', url);
        })
        .catch(error => console.error('Error:', error));
}
// w

document.addEventListener('click', function (event) {
    console.log("event.target", event)
    if (event.target.matches('a.nav-link') || event.target.parentElement.matches('a.nav-link')) {
        console.log("event.target.href: ", event.target.href)
        event.preventDefault();
        const url = event.target.href;
        fetchAndReplaceContent(url);
    }
});

const markFormOnSubmit = (formLogin) => {
    // document.querySelector('form-login')
    formLogin.onsubmit = async e => {
        e.preventDefault();
        console.log(e)
        const formData = new FormData(e.target);
        console.log("formData=", formData)
        // const response = await fetch('/api/auth/signin', {
        //     method: 'POST',
        //     body: new FormData(e.target) 
        // });
        await fetch('/api/auth/signin', {
            method: 'POST',
            body: formData
        }).then(async response => {
            if (response.ok) {
                console.log("OK")
                data = await response.json();
                console.log(data)
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                localStorage.setItem('token_type', data.token_type);

            };
        }).catch(async (error) => {
            console.log(error)
            // Завершился ошибкой
        })

        const result = await response.json();
        console.log(result);
    };

}
const scanForm = () => {
    const formLoginRef = document.getElementById('form-login');
    console.log("Элемент формы есть:", formLoginRef)
    if (formLoginRef) {
    }
}
scanForm()
// markFormOnSubmit();

// Создание экземпляра MutationObserver и передача callback-функции
const observer = new MutationObserver(scanForm);

// Выбор элемента для наблюдения
const targetNode = document.getElementById('form-login');

// Конфигурация observer для наблюдения за изменениями в элементе
const config = { childList: true, subtree: true, attributes: true };

// Начало наблюдения за выбранным элементом
observer.observe(document.body, config);

// window.location.reload();