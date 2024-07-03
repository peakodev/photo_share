
const formRef = document.querySelector('form');
// const formMessagesRef = document.getElementById('messages');
const formMessagesRef = document.querySelector('.messages-text');



console.log("formMessagesRef: ", formMessagesRef)
console.log("formRef: ", formRef)

const markFormOnSubmit = () => {
    // const formPostRef = document.getElementById('#form-post');

    console.log(`api_create_url: ${api_create_url}`)
    // document.querySelector('form').onsubmit = async e => {

    formRef.onsubmit = async e => {
        e.preventDefault();
        console.log("!!!!!! ")
        console.log(e)
        console.log(`api_create_url: ${api_create_url}`)
        
        const token = localStorage.getItem('access_token');
        
        if (token) {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${token}`);

            const formData = new FormData(e.target);
            for (let [name, value] of formData.entries()) {
                console.log(`${name}: ${value}`);
            }
            try {
                const res = await fetch('http://localhost:8000/post', {
                    method: 'POST',
                    body: formData,
                    headers: headers
                });
                const response_json = await res.json()
                // console.log("response: ", response)
                // console.log("response body: ", response_json)
                if (res.ok) {
                    console.log("OK")
                    // const html = await response.text();
                    // document.open();
                    // document.write(html);
                    // document.close();
                    // console.log("response_json=", response_json)
                    console.log("redirect_url: ", redirect_url)
                    red_url = redirect_url + "posts/" + response_json.id
                    console.log("red_url=", red_url)
                    window.location.href = red_url;
                }
                else {
                    console.log("Error")
                    console.log(res)
                    formMessagesRef.textContent = res.status + ": " + res.statusText
                }


            }
            catch (error) {
                console.log(error)
            }

        }

    };

}

markFormOnSubmit();

// Создание экземпляра MutationObserver и передача callback-функции
const observer = new MutationObserver(markFormOnSubmit);

// Выбор элемента для наблюдения
const targetNode = document.getElementById('form-post');

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


