let positions = document.querySelectorAll(".ballot")

var candidate_count = {}
for (position of positions) {
  candidate_count[position.id] = position.querySelectorAll(".candidate").length
}

for (candidate of document.querySelectorAll(".candidate")) {
  candidate.addEventListener('click', veto_click)
}

function veto_candidate() {
  if (this.classList.contains("picked")) unpick_candidate.call(this)
  this.classList.toggle("vetoed")
  this.style.order = 2*candidate_count[this.parentElement.id]+1
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
}

function set_formfield() {
  document.querySelector("input#candidates").value = Array.from(document.querySelectorAll("article.vetoed")).map(article => article.id).join("+") 
}

function veto_click() {
  candidate = this
  if (candidate.classList.contains("vetoed")) { 
    event.stopImmediatePropagation()
    unveto_candidate.call(candidate)
    set_formfield()
  } else {
    event.stopImmediatePropagation()
    veto_candidate.call(candidate)
    set_formfield()
  }
}

function unveto_click() {
  unveto_candidate.call(this)
  set_formfield()
}
