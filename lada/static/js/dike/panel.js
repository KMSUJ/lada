let positions = document.querySelectorAll(".ballot")

var candidate_count = {}
for (position of positions) {
  candidate_count[position.id] = position.querySelectorAll(".candidate").length
}

for (candidate of document.querySelectorAll(".candidate")) {
  candidate.addEventListener('click', veto_click)
  if (candidate.querySelector("input.position").value == "n") {
    candidate.style.order = candidate_count[candidate.parentElement.id]+1
  } else if (candidate.querySelector("input.position").value == "x") {
    veto_candidate.call(candidate)
  }
}

function veto_candidate() {
  if (this.classList.contains("picked")) unpick_candidate.call(this)
  this.classList.toggle("vetoed")
  this.style.order = 2*candidate_count[this.parentElement.id]+1
  this.querySelector("input.position").value = "x"
  this.removeEventListener('click', veto_click)
  this.addEventListener('click', unveto_click)
}

function unveto_candidate() {
  this.classList.toggle("vetoed")
  reset_position(this)
  this.removeEventListener('click', unveto_click)
  this.addEventListener('click', veto_click)
}

function reset_position(candidate) {
  candidate.style.order = candidate_count[candidate.parentElement.id]+1
  candidate.querySelector("input.position").value = "n"
}

function veto_click() {
  candidate = this
  if (candidate.classList.contains("vetoed")) { 
    event.stopImmediatePropagation()
    unveto_candidate.call(candidate)
  } else {
    event.stopImmediatePropagation()
    veto_candidate.call(candidate)
  }
}

function unveto_click() {
  unveto_candidate.call(this)
}
