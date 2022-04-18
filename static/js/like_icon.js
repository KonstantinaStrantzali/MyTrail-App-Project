const likesButtons = document.querySelectorAll('.like-icon');

//Change Icon class on favorite section
likesButtons.forEach(likeButton => {
    likeButton.addEventListener('click', e => {
        if (e.target.classList.contains('far')) {
            e.target.classList.remove('far');
            e.target.classList.add('fas');
            
        } else {
            e.target.classList.remove('fas');
            e.target.classList.add('far');
            
        }
    });
});
