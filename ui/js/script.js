const collapse = document.querySelector('.collapse');
const body = document.querySelector('body');

body.onclick = () => {
    if (collapse.classList.contains("show")) {
        $('.collapse').collapse('toggle');
    }
};