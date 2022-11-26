let p = document.getElementById("add_p");
let code = document.getElementById("add_code");

p.addEventListener("click", function (e) {
    text = "<p></p>\n"
    let area = document.getElementById("textArea");
    area.value+=text;
});



