const editBtnRef = document.querySelector('btn-edit-post');

// const postDetailsRef = document.querySelector('.post-details');
// const postCommentsRef = document.querySelector('.comments-section');
// const postFormRef = document.querySelector('post-form-wrapper');
userId = localStorage.getItem('user_id')

if (user_id === postUserId) {
    console.log("equal")
    editBtnRef.attributes.remove('hidden')
}


console.log(editBtnRef)

const editTogglePage = (e) => {
    // postDetailsRef.classList.toggle('hidden');
    // postCommentsRef.classList.toggle('hidden');
    // postFormRef.classList.toggle('hidden');
}


// editBtnRef.addEventListener('click', (event) => editTogglePage)
