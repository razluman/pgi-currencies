function add_remove(add = true) {
    display = document.getElementById('display');
    not_display = document.getElementById('not_display');
    if (add) {
        option = not_display.options[not_display.selectedIndex];
        not_display.remove(option);
        display.add(option);
    } else {
        option = display.options[display.selectedIndex];
        display.remove(option);
        not_display.add(option);
    }
    document.getElementById('display_list').value = get_select_content(display);
    document.getElementById('not_display_list').value = get_select_content(not_display);
}

function get_select_content(select) {
    content = "";
    for (let i = 0; i < select.length; i++) {
        if (i > 0) content = content + "\t";
        content = content + select[i].value;
    }
    return content;
}