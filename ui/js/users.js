const editRhyme = document.querySelectorAll('.editRhyme');
const editRhymeModal = document.querySelector('#editRhymesModal');
const editRhymeType = document.querySelectorAll('.editRhymeType');
const editRhymeTypeModal = document.querySelector('#editRhymeType');

const deleteButton = document.querySelectorAll('.delete');
const confirmDeletion = document.querySelector('#confirmDeletion');

editRhyme.forEach(edit => {
    edit.addEventListener('click', event => {
        const tr = edit.parentElement.parentElement;
        const title = tr.querySelector('.rhymeTitle');
        const rhyme = tr.querySelector('.rhymeContent');
        const modalTitle = editRhymeModal.querySelector('#rhyme-title');
        const modalRhyme = editRhymeModal.querySelector('#rhyme');
        modalTitle.value = title.innerText;
        modalRhyme.value = rhyme.innerText;
    });
});

editRhymeType.forEach(edit => {
    edit.addEventListener('click', event => {
        const tr = edit.parentElement.parentElement;
        const type = tr.querySelector('.rhymeType');
        const modalType = editRhymeTypeModal.querySelector('#rhyme-type');
        modalType.value = type.innerText;
    });
});

deleteButton.forEach(button => {
    button.addEventListener('click', event => {
        const href = button.getAttribute('href');
        confirmDeletion.setAttribute("href", href);
    });
});