let positions = document.querySelectorAll(".ballot")

var candidate_count = {}
for (position of positions) {
  candidate_count[position.id] = position.querySelectorAll(".candidate").length
}

var candidate_index = {}
for (position in candidate_count) {
  candidate_index[position] = 1
}

for (button of document.querySelectorAll(".veto_button")) {
  button.addEventListener('click', veto_click)
}

for (candidate of document.querySelectorAll(".candidate")) {
  candidate.addEventListener('click', pick_click)
  if (candidate.querySelector("input.position").value == "n") {
    candidate.style.order = candidate_count[candidate.parentElement.id]+1
  } else if (candidate.querySelector("input.position").value == "x") {
    veto_candidate.call(candidate)
  } else {
    candidate.classList.toggle("picked")
    set_position(candidate, candidate.querySelector("input.position").value)
    candidate_index[candidate.parentElement.id]++
  }
}

function veto_candidate() {
  if (this.classList.contains("picked")) unpick_candidate.call(this)
  this.classList.toggle("vetoed")
  this.style.order = 2*candidate_count[this.parentElement.id]+1
  this.querySelector(".position").textContent = ""
  this.querySelector("input.position").value = "x"
  this.removeEventListener('click', pick_click)
  this.addEventListener('click', unveto_click)
}

function unveto_candidate() {
  this.classList.toggle("vetoed")
  reset_position(this)
  this.removeEventListener('click', unveto_click)
  this.addEventListener('click', pick_click)
}

function pick_candidate() {
  this.classList.toggle("picked")
  set_position(this, candidate_index[this.parentElement.id])
  candidate_index[this.parentElement.id]++
}

function unpick_candidate() {
  this.classList.toggle("picked")
  removed = this.style.order
  reset_position(this)
  reorder_candidates(this.parentElement, removed)
  candidate_index[this.parentElement.id]--
}

function set_position(candidate, position) {
  candidate.style.order = position
  candidate.querySelector("div.position").textContent = position
  candidate.querySelector("input.position").value = position
}

function reset_position(candidate) {
  candidate.style.order = candidate_count[candidate.parentElement.id]+1
  candidate.querySelector("div.position").textContent = "" 
  candidate.querySelector("input.position").value = "n"
}

function reorder_candidates(ballot, removed) {
  candidates = ballot.querySelectorAll(".picked")
  for (candidate of candidates) {
    if (candidate.style.order > removed) {
      set_position(candidate, candidate.style.order-1)
    }
  }
}

function pick_click() {
  if (this.classList.contains("picked")) { 
    event.stopImmediatePropagation()
    unpick_candidate.call(this)
  } else {
    event.stopImmediatePropagation()
    pick_candidate.call(this)
  }
}

function veto_click() {
  candidate = this.parentElement
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
