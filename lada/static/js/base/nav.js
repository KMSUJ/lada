let button = document.querySelector("#navbutton");
let overlay = document.querySelector("#navoverlay");
button.addEventListener("click", open_nav);
overlay.addEventListener("click", open_nav);

function open_nav() {
  var nav = document.querySelector("#navigation");
  var button = document.querySelector("#navbutton");
  var overlay = document.querySelector("#navoverlay");
  nav.classList.toggle("open");
  button.classList.toggle("open");
  overlay.classList.toggle("open");
}
