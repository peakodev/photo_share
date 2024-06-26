
const formRef = document.querySelector('form');

const markFormOnSubmit = () => {
    document.querySelector('form').onsubmit = async e => {
        e.preventDefault();

        console.log("!!! markFormOnSubmite Signup Form:  ", e)
        const formData = new FormData(e.target);
        console.log("formData=", formData)
        const formDataObj = {};
        formData.forEach((value, key) => formDataObj[key] = value);


        for (let [name, value] of formData.entries()) {
            console.log(`${name}: ${value}`);
        }

        await fetch(api_signup, {
            method: 'POST',
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            body: JSON.stringify(formDataObj),
        }).then(async response => {
            if (response.ok) {
                console.log("OK signUp")
                window.location.href = redirect_url;
            };
        }).catch(async (error) => {
            console.log(error)
            // Завершился ошибкой
        })

        // const result = await response.json();
        // console.log(result);
    };

}

markFormOnSubmit();

// Создание экземпляра MutationObserver и передача callback-функции
const observer = new MutationObserver(markFormOnSubmit);

// Выбор элемента для наблюдения
const targetNode = document.getElementById('form-signup');

// Конфигурация observer для наблюдения за изменениями в элементе
const config = { childList: true, subtree: true, attributes: true };

// Начало наблюдения за выбранным элементом
observer.observe(targetNode, config);

