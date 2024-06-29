
const formRef = document.querySelector('form');
// const formMessagesRef = document.getElementById('messages');
const formMessagesRef = document.querySelector('.messages-text');


console.log("formMessagesRef: ", formMessagesRef)
console.log("formRef: ", formRef)

const markFormOnSubmit = () => {
    document.querySelector('form').onsubmit = async e => {
        e.preventDefault();
        console.log("!!!!!! ")
        console.log(e)
        const token = localStorage.getItem('access_token');
        if (token) {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${token}`);

            const formData = new FormData(e.target);
            for (let [name, value] of formData.entries()) {
                console.log(`${name}: ${value}`);
            }
            try {
                const response = await fetch('http://localhost:8000/post_create', {
                    method: 'POST',
                    body: formData,
                    headers: headers
                });
                if (response.ok) {
                    window.location.href = redirect_url;
                }
                else {
                    console.log("Error")
                    console.log(response)
                    formMessagesRef.textContent = response.status + ": " + response.statusText
                }


            }
            catch (error) {
                console.log(error)
            }

        }

        // console.log("markFormOnSubmite: ", e)
        // console.log("formData=", formData)


        // const response = await fetch('/post_create', {
        //     method: 'POST',
        //     body: new FormData(e.target)
        // });

        // const result = await response.json();
        // console.log(result);
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


