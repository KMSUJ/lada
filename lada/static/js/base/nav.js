document.querySelector("#navbutton").addEventListener("click", open_nav);
document.querySelector("#navoverlay").addEventListener("click", open_nav);

function open_nav() {
  document.querySelector("#navigation").classList.toggle("open");
  document.querySelector("#navbutton").classList.toggle("open");
  document.querySelector("#navoverlay").classList.toggle("open");
}
