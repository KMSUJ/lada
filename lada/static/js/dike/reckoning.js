for (position of document.querySelectorAll(".ballot")) {
    if (position.id == "boss" || position.id == "covision") {
        for (button of position.querySelectorAll(".elected")) {
            button.classList.add("picked")
            button.classList.add("inactive")
        }
    }
}

let buttons = document.querySelectorAll(".elected:not(.boss):not(.covision)")
for (input of document.querySelectorAll("input[type=hidden]:not(#csrf_token)")) input.value = ""

for (button of buttons) activate(button)

function countFree() {
  return document.querySelector("#free").querySelectorAll(".picked").length
}

function choose(button) {
  button.classList.add("chosen")
  button.removeEventListener('click', pick_click)
}

function activate(button) {
  button.classList.remove("inactive")
  button.addEventListener('click', pick_click)
}

function activate_position(id) {
  for (button of buttons) {
    if (button.id.split("+")[0] == id && ! button.classList.contains("chosen")) {
      activate(button)
    }
  }
}

function choose_candidate(id) {
  for (button of buttons) {
    if (button.id.split("+")[1] == id) choose(button)
  }
}

function dechoose(button) {
  button.classList.remove("chosen")
  button.addEventListener('click', pick_click)
}

function deactivate(button) {
  button.classList.add("inactive")
  button.removeEventListener('click', pick_click)
}

function deactivate_position(id, careful=false) {
  for (button of buttons) {
    if (button.id.split("+")[0] == id) {
      if (!(careful && button.classList.contains("picked"))) deactivate(button)
    }
  }
}

function dechoose_candidate(id) {
  for (button of buttons) {
    if (button.id.split("+")[1] == id) dechoose(button)
  }
}

function pick_click() {
  id = this.id.split("+")
  if (this.classList.contains("picked")) {
    activate_position(id[0])
    dechoose_candidate(id[1])
  } else {
    if (!(id[0] == "free" && countFree() < 2)) deactivate_position(id[0], careful=true)
    choose_candidate(id[1])
  }
  activate(this)
  this.classList.toggle("picked")
  document.querySelector(`input#${id[0]}`).value = Array.from(document.querySelector(`section#${id[0]}`).querySelectorAll(".picked")).map(button => button.id.split("+")[1]).join("+")
}
