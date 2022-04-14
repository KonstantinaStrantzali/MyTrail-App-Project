const likesButtons = document.querySelectorAll('.like-icon');


//Change Icon class and input



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

/*
$(document).ready(function(){
    if($(".like-icon").attr("href")==window.location.href){
        $(".like-icon").attr("class","far");
    }
   else{
      $(".like-icon").attr("class","fas");
     }
});

$(document).ready(function() {
    var body_class = $.cookie('body_class');
    if(body_class) {
        $('body').attr('class', body_class);
    }
    $("a#switcher").click(function() {
        $("body").toggleClass("alternate_body");
        $.cookie('body_class', $('body').attr('class'));
    });
});
*/