
const formRef = document.querySelector('form');

const markFormOnSubmit = () => {
    document.querySelector('form').onsubmit = async e => {
        e.preventDefault();

        console.log("markFormOnSubmite: ", e)
        const formData = new FormData(e.target);
        console.log("formData=", formData)
        for (let [name, value] of formData.entries()) {
            console.log(`${name}: ${value}`);
        }

        const response = await fetch('/api/auth/signin', {
            method: 'POST',
            body: new FormData(e.target)
        });
        await fetch('/api/auth/login', {
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
                localStorage.setItem('user_id', 1);


                window.location.href = redirect_url;
            };
        }).catch(async (error) => {
            console.log(error)
            // Завершился ошибкой
        })

        // const response_user = await fetch(`${/}`, {
        //     headers: {
        //         'Authorization': `Bearer ${token}`
        //     }
        // });

        // if (response.ok) {
        //     const html = await response.text();
        //     document.open();
        //     document.write(html);
        //     document.close();
        //     window.history.pushState({}, '', page);
        // } else {
        //     console.error('!!!Error:', response.status, response.statusText);
        // }

        // const result = await response.json();
        // console.log(result);
    };

}

markFormOnSubmit();

// Создание экземпляра MutationObserver и передача callback-функции
const observer = new MutationObserver(markFormOnSubmit);

// Выбор элемента для наблюдения
const targetNode = document.getElementById('form-login');

// Конфигурация observer для наблюдения за изменениями в элементе
const config = { childList: true, subtree: true, attributes: true };

// Начало наблюдения за выбранным элементом
observer.observe(targetNode, config);

// const observer = new MutationObserver((mutations) => {
//     mutations.forEach((mutation) => {
//         if (mutation.type === 'childList') {
//             console.log('DOM изменён');
//             // Привязка событий после изменения DOM
//             markFormOnSubmit();
//         }
//     });
// });


// document.querySelector('form').onsubmit = async e => {
//     e.preventDefault();
//     console.log(e)
//     const formData = new FormData(e.target);
//     console.log("formData=", formData)
//     // const response = await fetch('/api/auth/signin', {
//     //     method: 'POST',
//     //     body: new FormData(e.target) 
//     // });
//     await fetch('/api/auth/signin', {
//         method: 'POST',
//         body: formData
//     }).then(async response => {
//         if (response.ok) {
//             console.log("OK")
//             data = await response.json();
//             console.log(data)
//             localStorage.setItem('access_token', data.access_token);
//             localStorage.setItem('refresh_token', data.refresh_token);
//             localStorage.setItem('token_type', data.token_type);

//         };
//     }).catch(async (error) => {
//         console.log(error)
//         // Завершился ошибкой
//     })

//     const result = await response.json();
//     console.log(result);
// };




async function login(e) {
    // const formData = new FormData(e.target);
    // console.log(e);
    // fetch('/api/auth/signin', {
    //     method: 'POST',
    //     body: formData
    // }).then(response => {
    //     if (response.ok) {
    //         console.log("OK")
    //         console.log(response)

    //         localStorage.setItem('access_token', data.access_token);
    //     }
    // })
    // const response = await fetch('/api/auth/signin', {
    // method: 'POST',
    // body: formData
    // });
    // const data = await response.json();
    // if (response.ok) {
    //     console.log(data);
    //     localStorage.setItem('access_token', data.access_token);
    //     window.location.href = '/protected';
    // } else {
    //     console.log("!!!! error auth", data.detail)
    //     alert('Login failed: ' + data.detail);
    // }
}


// form.addEventListener('submit', (e) => {
//     e.preventDefault();
//     login(e);
// })