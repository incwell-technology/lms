const editButton = document.querySelectorAll('.editButton');
const editHolidayModal = document.querySelector('#editHoliday');

const deleteButton = document.querySelectorAll('.delete');
const confirmDeletion = document.querySelector('#confirmDeletion');

const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const date = new Date();

const addLeadingZeros = (num) => {
    if (num < 10) {
        num = "0" + num;
    }
    return num;
};


editButton.forEach(edit => {
    edit.addEventListener('click', event => {
        const card = edit.parentElement;
        const title = card.querySelector('h4');
        const from = card.querySelector('.from');
        from.month = from.innerText.split(" ")[0];
        from.month = addLeadingZeros(months.indexOf(from.month) + 1);  //Convert month format, e.g Feb => 02
        from.day = addLeadingZeros(from.innerText.split(" ")[1]);
        const to = card.querySelector('.to');
        to.month = to.innerText.split(" ")[0];
        to.month = addLeadingZeros(months.indexOf(to.month) + 1);
        to.day = addLeadingZeros(to.innerText.split(" ")[1]); 
        const description = card.querySelector('.description');
        const modalTitle = editHolidayModal.querySelector('#holidayTitle');
        const modalfromDate = editHolidayModal.querySelector('#fromDate');
        const modaltoDate = editHolidayModal.querySelector('#toDate');
        const modalDescription = editHolidayModal.querySelector('#holidayDescription');
        modalTitle.value = title.innerText;
        modalfromDate.value = date.getFullYear() + '-' + from.month + '-' + from.day;
        modaltoDate.value = date.getFullYear() + '-' + to.month + '-' + to.day;
        modalDescription.value = description.innerText;
    });
});

deleteButton.forEach(button => {
    button.addEventListener('click', event => {
        const href = button.getAttribute('href');
        confirmDeletion.setAttribute("href", href);
    });
});