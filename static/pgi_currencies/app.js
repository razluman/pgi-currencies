window.addEventListener("load", () => {
    document.querySelectorAll(".nav-link").forEach(navbar => {
        if (navbar.href === window.location.href) {
            navbar.classList.add("active");
            navbar.setAttribute("aria-current", "page");
        }
    });
});

function rateConvert(id, rate, toAriary = true) {
    let source = "devise";
    let target = "ariary";
    if (!toAriary) {
        source = "ariary";
        target = "devise";
    };
    amount = document.querySelector("#" + source + id).value;
    amount = stringToFloat(amount);
    if (toAriary) {
        amount = amount * rate
    } else {
        if (rate != 0) amount = amount / rate
    }
    amount = floatToString(amount);
    if (amount == "0,00") amount = "";
    document.querySelector("#" + target + id).value = amount
}

function amountFormatOnBlur(id) {
    input = document.querySelector(id);
    amount = input.value;
    amount = stringToFloat(amount);
    amount = floatToString(amount);
    if (amount == "0,00") amount = "";
    input.value = amount;
}

function stringToFloat(amount) {
    amount = amount.replace(/[^\d,.-]/g, '');
    amount = amount.replace(",", ".");
    amount = amount * 1;
    return amount;
}

function floatToString(amount) {
    amount = amount.toFixed(2)
    amount = amount.toString().replace(".", ",");
    amount = amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    return amount;
}