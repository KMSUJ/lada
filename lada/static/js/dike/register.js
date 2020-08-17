let switchWolny = document.querySelector("#wolny");
let switchKomisja = document.querySelector("#komisja");
let switchesBoard = document.querySelectorAll("input.switch:not(#komisja):not(#wolny)")

for (s of switchesBoard) {
  s.addEventListener("click", toggleBoard);
  if (s.checked) {
    selectWolny()
  }
}

switchWolny.addEventListener("click", toggleWolny);
switchKomisja.addEventListener("click", toggleKomisja);

function toggleBoard() {
  checkedCount = countSwitches();
  if (this.checked == true) {
    deselectKomisja();
    selectWolny();
    if (checkedCount > 2) {
      disableSwitches();
    }
  } else if (checkedCount > 0) {
    enableSwitches();
  } else {
    switchWolny.disabled = false;
  }
}

function toggleWolny() {
  if (this.checked == true) {
    deselectKomisja();
  }
}

function toggleKomisja() {
  if (switchKomisja.checked == true) {
    deselectBoard();
    deselectWolny();
    enableSwitches();
  }
}

function deselectBoard() {
  for (s of switchesBoard) {
    s.checked = false;
  }
}

function selectWolny() {
  switchWolny.checked = true;
  switchWolny.disabled = true;
}

function deselectWolny() {
  switchWolny.checked = false;
  switchWolny.disabled = false;
}

function deselectKomisja() {
  switchKomisja.checked = false;
}

function countSwitches() {
  c = 0;
  for (s of switchesBoard) {
    if (s.checked == true) {
      c = c+1;
    }
  }
  return c;
}

function disableSwitches() {
  for (s of switchesBoard) {
    if (s.checked == false) {
      s.disabled = true;
    }
  }
}

function enableSwitches() {
  for (s of switchesBoard) {
    s.disabled = false;
  }
}
