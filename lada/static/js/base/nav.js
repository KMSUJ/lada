document.querySelector("#navbutton").addEventListener("click", open_nav);
document.querySelector("#navoverlay").addEventListener("click", open_nav);

document.querySelector("#closeflash").addEventListener("click", close_flash);

function open_nav() {
  document.querySelector("#navigation").classList.toggle("open");
  document.querySelector("#navbutton").classList.toggle("open");
  document.querySelector("#navoverlay").classList.toggle("open");
}

function close_flash() {
  document.querySelector('.flash').style.display = "None";
}
