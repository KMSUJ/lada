// workaround for flask-pagedown label placement
document.querySelector("div.flask-pagedown").appendChild(document.querySelector("label[for='body']"))

// tags

let tagField = document.querySelector("input#tags");
let tagContainer = document.querySelector("div#tagcontainer");
let tagInput = document.querySelector("input#taginput");
tagInput.addEventListener('keydown', spacepress);
let tags = new Set();


for (value of tagField.value.toString().split(" ")) {
  if (value.length > 0) {
    element = createTagElement(value);
    tagContainer.appendChild(element);
    element.classList.add("valid");
    tags.add(value);
  }
}

function spacepress(e) {
  if (e.code === "Space") {
    value = tagInput.value.toString().replace(/\s/g, "").toLowerCase();
    if (value.length > 0) {
      processTag(value);
    }
    clearInput();
  }
}

function clearInput() {
  tagInput.value = "";
}

function setTagField() {
  tagField.value = Array.from(tags).join(" ");
}

function processTag(value) {
  element = createTagElement(value);
  tagContainer.appendChild(element);
  if (!tags.has(value)) {
    element.classList.add("valid");
    tags.add(value);
    setTagField();
  } else {
    setTimeout(function() {element.remove()}, 864);
  }
}

function createTagElement(value) {
  tagSpan = document.createElement("span");
  tagSpan.classList.add("tag");
  tagSpan.id = value;
  tagSpan.appendChild(document.createTextNode(`#${value}`));
  tagSpan.appendChild(createCrossElement());
  return tagSpan
}

function createCrossElement() {
  cross = document.createElement("div");
  cross.classList.add("closecross");
  fwdbar = document.createElement("span");
  fwdbar.classList.add("fwd");
  bwdbar = document.createElement("span");
  bwdbar.classList.add("bwd");
  cross.appendChild(fwdbar);
  cross.appendChild(bwdbar);
  cross.addEventListener('click', deleteTag);
  return cross
}

function deleteTag() {
  parentElement = this.parentNode;
  value = parentElement.id;
  tags.delete(value);
  setTagField();
  parentElement.remove();
}

// mail

for (button of document.querySelectorAll("input.switch")) {button.addEventListener("click", toggleSwitch);}

function toggleSwitch() {
  value = this.name.toString().replace(/\s/g, "").toLowerCase();
  if (this.checked == true) {
    processTag(value);
  } else {
    tags.delete(value);
    setTagField();
    document.querySelector(`span#${value}`).remove()
  }
}
