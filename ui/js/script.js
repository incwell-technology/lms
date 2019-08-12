const body = document.querySelector('body');

body.onclick = () => {
    const collapse = document.querySelector('.collapse');
    if (collapse.classList.contains("show")) {
        $('.collapse').collapse('toggle');
    }
};