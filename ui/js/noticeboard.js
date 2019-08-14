const editButton = document.querySelectorAll('.editButton');
const editNoticeModal = document.querySelector('#editNotice');

const deleteButton = document.querySelectorAll('.delete');
const confirmDeletion = document.querySelector('#confirmDeletion');

editButton.forEach(edit => {
    edit.addEventListener('click', event => {
        const card = edit.parentElement;
        const title = card.querySelector('h4');
        const notice = card.querySelector('.notice-content');
        const modalTitle = editNotice.querySelector('#noticeTitle');
        const modalNotice = editNotice.querySelector('#notice');
        modalTitle.value = title.innerText;
        modalNotice.value = notice.innerText;
    });
});


deleteButton.forEach(button => {
    button.addEventListener('click', event => {
        const href = button.getAttribute('href');
        confirmDeletion.setAttribute("href", href);
    });
});